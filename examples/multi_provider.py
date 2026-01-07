#!/usr/bin/env python3
"""Multi-Provider Example: Using multiple LLMs with AI Skills.

This example demonstrates how to use multiple LLM providers together,
comparing responses, using fallbacks, and selecting the best provider
for different tasks.

Usage:
    pip install aiskills[llms]
    export OPENAI_API_KEY="..."
    export ANTHROPIC_API_KEY="..."
    export GEMINI_API_KEY="..."
    python examples/multi_provider.py
"""

import asyncio
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable

# Check which providers are available
AVAILABLE_PROVIDERS: dict[str, bool] = {}

try:
    from aiskills.integrations import create_openai_client
    AVAILABLE_PROVIDERS["openai"] = "OPENAI_API_KEY" in os.environ
except ImportError:
    AVAILABLE_PROVIDERS["openai"] = False

try:
    from aiskills.integrations import create_anthropic_client
    AVAILABLE_PROVIDERS["anthropic"] = "ANTHROPIC_API_KEY" in os.environ
except ImportError:
    AVAILABLE_PROVIDERS["anthropic"] = False

try:
    from aiskills.integrations import create_gemini_client
    AVAILABLE_PROVIDERS["gemini"] = (
        "GEMINI_API_KEY" in os.environ or "GOOGLE_API_KEY" in os.environ
    )
except ImportError:
    AVAILABLE_PROVIDERS["gemini"] = False

try:
    from aiskills.integrations import create_ollama_client
    AVAILABLE_PROVIDERS["ollama"] = True  # Ollama doesn't need API key
except ImportError:
    AVAILABLE_PROVIDERS["ollama"] = False


def get_available_clients() -> dict[str, Any]:
    """Create clients for all available providers."""
    clients = {}

    if AVAILABLE_PROVIDERS.get("openai"):
        clients["openai"] = create_openai_client(model="gpt-4")

    if AVAILABLE_PROVIDERS.get("anthropic"):
        clients["anthropic"] = create_anthropic_client()

    if AVAILABLE_PROVIDERS.get("gemini"):
        clients["gemini"] = create_gemini_client()

    if AVAILABLE_PROVIDERS.get("ollama"):
        try:
            client = create_ollama_client(model="llama3.1")
            if client.is_model_available():
                clients["ollama"] = client
        except Exception:
            pass

    return clients


# ============================================================
# Example 1: Compare responses from multiple providers
# ============================================================

def compare_providers(question: str) -> dict[str, str]:
    """Ask the same question to all available providers.

    Args:
        question: The question to ask

    Returns:
        Dictionary mapping provider name to response
    """
    clients = get_available_clients()
    responses = {}

    print(f"\nQuestion: {question}")
    print("=" * 60)

    for name, client in clients.items():
        try:
            start = time.time()
            response = client.chat(question)
            elapsed = time.time() - start

            responses[name] = response
            print(f"\n[{name.upper()}] ({elapsed:.2f}s)")
            print("-" * 40)
            # Truncate long responses
            if len(response) > 500:
                print(response[:500] + "...")
            else:
                print(response)

        except Exception as e:
            responses[name] = f"Error: {e}"
            print(f"\n[{name.upper()}] Error: {e}")

    return responses


# ============================================================
# Example 2: Parallel requests to multiple providers
# ============================================================

def parallel_query(question: str, timeout: float = 30.0) -> dict[str, str]:
    """Query all providers in parallel and return results.

    Args:
        question: The question to ask
        timeout: Maximum time to wait for all responses

    Returns:
        Dictionary mapping provider name to response
    """
    clients = get_available_clients()
    responses = {}

    def query_provider(name: str, client: Any) -> tuple[str, str, float]:
        start = time.time()
        try:
            response = client.chat(question)
            return name, response, time.time() - start
        except Exception as e:
            return name, f"Error: {e}", time.time() - start

    print(f"\nParallel query: {question}")
    print("=" * 60)

    with ThreadPoolExecutor(max_workers=len(clients)) as executor:
        futures = {
            executor.submit(query_provider, name, client): name
            for name, client in clients.items()
        }

        for future in as_completed(futures, timeout=timeout):
            name, response, elapsed = future.result()
            responses[name] = response
            print(f"[{name}] completed in {elapsed:.2f}s")

    return responses


# ============================================================
# Example 3: Fallback chain
# ============================================================

def query_with_fallback(
    question: str,
    preferred_order: list[str] | None = None,
) -> tuple[str, str]:
    """Try providers in order, falling back on errors.

    Args:
        question: The question to ask
        preferred_order: List of provider names in order of preference

    Returns:
        Tuple of (provider_name, response)
    """
    clients = get_available_clients()

    if preferred_order is None:
        # Default order: OpenAI -> Anthropic -> Gemini -> Ollama
        preferred_order = ["openai", "anthropic", "gemini", "ollama"]

    print(f"\nFallback query: {question}")
    print(f"Order: {' -> '.join(preferred_order)}")
    print("=" * 60)

    for provider in preferred_order:
        if provider not in clients:
            print(f"[{provider}] Not available, skipping...")
            continue

        try:
            print(f"[{provider}] Trying...")
            response = clients[provider].chat(question)
            print(f"[{provider}] Success!")
            return provider, response

        except Exception as e:
            print(f"[{provider}] Failed: {e}")
            continue

    return "none", "All providers failed"


# ============================================================
# Example 4: Best provider for task type
# ============================================================

# Map task types to recommended providers
TASK_PROVIDERS = {
    "code": ["anthropic", "openai", "gemini", "ollama"],
    "creative": ["anthropic", "gemini", "openai", "ollama"],
    "analysis": ["openai", "anthropic", "gemini", "ollama"],
    "fast": ["gemini", "ollama", "openai", "anthropic"],
    "local": ["ollama"],
}


def smart_query(question: str, task_type: str = "code") -> tuple[str, str]:
    """Route query to best provider for the task type.

    Args:
        question: The question to ask
        task_type: Type of task (code, creative, analysis, fast, local)

    Returns:
        Tuple of (provider_name, response)
    """
    preferred = TASK_PROVIDERS.get(task_type, ["openai", "anthropic"])
    return query_with_fallback(question, preferred)


# ============================================================
# Example 5: Streaming from multiple providers
# ============================================================

def stream_from_provider(provider: str, question: str):
    """Stream response from a specific provider.

    Args:
        provider: Provider name
        question: The question to ask
    """
    clients = get_available_clients()

    if provider not in clients:
        print(f"Provider '{provider}' not available")
        return

    print(f"\nStreaming from {provider}:")
    print("-" * 40)

    for chunk in clients[provider].chat_stream(question):
        print(chunk, end="", flush=True)

    print("\n")


# ============================================================
# Example 6: Consensus voting
# ============================================================

def consensus_query(question: str, min_providers: int = 2) -> dict[str, Any]:
    """Query multiple providers and find consensus.

    This is useful for fact-checking or getting reliable answers.

    Args:
        question: The question to ask
        min_providers: Minimum providers needed for consensus

    Returns:
        Dictionary with responses and any detected consensus
    """
    responses = parallel_query(question)

    # Simple consensus: check if responses mention same key concepts
    # In production, you'd want more sophisticated comparison

    result = {
        "responses": responses,
        "provider_count": len(responses),
        "all_succeeded": all(
            not r.startswith("Error:") for r in responses.values()
        ),
    }

    print(f"\nConsensus: {len(responses)} providers responded")

    return result


# ============================================================
# Main demo
# ============================================================

def main():
    """Run the multi-provider demo."""
    print("=" * 60)
    print("AI Skills Multi-Provider Demo")
    print("=" * 60)

    # Show available providers
    print("\nAvailable providers:")
    for name, available in AVAILABLE_PROVIDERS.items():
        status = "YES" if available else "no"
        print(f"  {name}: {status}")

    clients = get_available_clients()
    if not clients:
        print("\nNo providers available! Please configure at least one:")
        print("  - OPENAI_API_KEY for OpenAI")
        print("  - ANTHROPIC_API_KEY for Anthropic")
        print("  - GEMINI_API_KEY for Gemini")
        print("  - Install Ollama for local models")
        return

    print(f"\nUsing {len(clients)} provider(s): {', '.join(clients.keys())}")

    # Demo 1: Compare providers
    print("\n" + "=" * 60)
    print("DEMO 1: Compare Providers")
    print("=" * 60)
    compare_providers("What's the best way to handle errors in Python? Be concise.")

    # Demo 2: Fallback chain
    print("\n" + "=" * 60)
    print("DEMO 2: Fallback Chain")
    print("=" * 60)
    provider, response = query_with_fallback(
        "Explain async/await in 2 sentences."
    )
    print(f"\nFinal response from {provider}:")
    print(response[:300] + "..." if len(response) > 300 else response)

    # Demo 3: Smart routing
    print("\n" + "=" * 60)
    print("DEMO 3: Smart Routing (code task)")
    print("=" * 60)
    provider, response = smart_query(
        "Write a Python function to reverse a string.",
        task_type="code"
    )
    print(f"\nResponse from {provider}:")
    print(response[:400] + "..." if len(response) > 400 else response)

    # Demo 4: Streaming (if any provider available)
    if clients:
        print("\n" + "=" * 60)
        print("DEMO 4: Streaming")
        print("=" * 60)
        first_provider = list(clients.keys())[0]
        stream_from_provider(first_provider, "Count from 1 to 5.")


if __name__ == "__main__":
    main()
