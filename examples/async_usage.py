#!/usr/bin/env python3
"""Async usage examples for AI Skills SDK wrappers.

This script demonstrates how to use async/await with the SDK wrappers
for non-blocking operations and concurrent requests.

Requirements:
    pip install aiskills[llms]

Usage:
    python examples/async_usage.py
"""

import asyncio
import time
from typing import Any

# Check which providers are available
AVAILABLE_PROVIDERS: dict[str, Any] = {}


def check_providers():
    """Check which providers have API keys configured."""
    import os

    if os.getenv("OPENAI_API_KEY"):
        try:
            from aiskills.integrations import create_openai_client
            AVAILABLE_PROVIDERS["openai"] = create_openai_client
            print("  openai: YES")
        except ImportError:
            print("  openai: no (package not installed)")
    else:
        print("  openai: no (no API key)")

    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            from aiskills.integrations import create_anthropic_client
            AVAILABLE_PROVIDERS["anthropic"] = create_anthropic_client
            print("  anthropic: YES")
        except ImportError:
            print("  anthropic: no (package not installed)")
    else:
        print("  anthropic: no (no API key)")

    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        try:
            from aiskills.integrations import create_gemini_client
            AVAILABLE_PROVIDERS["gemini"] = create_gemini_client
            print("  gemini: YES")
        except ImportError:
            print("  gemini: no (package not installed)")
    else:
        print("  gemini: no (no API key)")

    # Ollama doesn't need API key
    try:
        from aiskills.integrations import create_ollama_client
        AVAILABLE_PROVIDERS["ollama"] = lambda: create_ollama_client(model="llama3.1")
        print("  ollama: YES (local)")
    except ImportError:
        print("  ollama: no (package not installed)")


# =============================================================================
# Demo 1: Basic Async Chat
# =============================================================================


async def demo_basic_async():
    """Basic async chat example."""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic Async Chat")
    print("=" * 60)

    if not AVAILABLE_PROVIDERS:
        print("No providers available. Skipping.")
        return

    # Use first available provider
    provider_name = next(iter(AVAILABLE_PROVIDERS))
    factory = AVAILABLE_PROVIDERS[provider_name]

    print(f"\nUsing provider: {provider_name}")

    client = factory()

    # Async chat - non-blocking
    print("\nSending async request...")
    start = time.perf_counter()

    response = await client.chat_async(
        "What are the top 3 Python debugging techniques? Be brief."
    )

    elapsed = time.perf_counter() - start
    print(f"\nResponse ({elapsed:.2f}s):")
    print("-" * 40)
    print(response[:500] + "..." if len(response) > 500 else response)


# =============================================================================
# Demo 2: Concurrent Requests
# =============================================================================


async def demo_concurrent_requests():
    """Run multiple requests concurrently."""
    print("\n" + "=" * 60)
    print("DEMO 2: Concurrent Requests (3 queries in parallel)")
    print("=" * 60)

    if not AVAILABLE_PROVIDERS:
        print("No providers available. Skipping.")
        return

    provider_name = next(iter(AVAILABLE_PROVIDERS))
    factory = AVAILABLE_PROVIDERS[provider_name]

    print(f"\nUsing provider: {provider_name}")

    client = factory()

    questions = [
        "What is a Python decorator? One sentence.",
        "What is a context manager? One sentence.",
        "What is a generator? One sentence.",
    ]

    print(f"\nSending {len(questions)} requests concurrently...")
    start = time.perf_counter()

    # Run all requests concurrently
    tasks = [client.chat_async(q) for q in questions]
    responses = await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start
    print(f"\nAll responses received in {elapsed:.2f}s (parallel)")

    for i, (q, r) in enumerate(zip(questions, responses), 1):
        print(f"\n{i}. Q: {q}")
        print(f"   A: {r[:150]}..." if len(r) > 150 else f"   A: {r}")


# =============================================================================
# Demo 3: Async Streaming
# =============================================================================


async def demo_async_streaming():
    """Async streaming response example."""
    print("\n" + "=" * 60)
    print("DEMO 3: Async Streaming")
    print("=" * 60)

    if not AVAILABLE_PROVIDERS:
        print("No providers available. Skipping.")
        return

    provider_name = next(iter(AVAILABLE_PROVIDERS))
    factory = AVAILABLE_PROVIDERS[provider_name]

    print(f"\nUsing provider: {provider_name}")

    client = factory()

    print("\nStreaming response:")
    print("-" * 40)

    start = time.perf_counter()
    char_count = 0

    async for chunk in client.chat_stream_async(
        "Write a haiku about Python programming."
    ):
        print(chunk, end="", flush=True)
        char_count += len(chunk)

    elapsed = time.perf_counter() - start
    print(f"\n-" * 40)
    print(f"Streamed {char_count} characters in {elapsed:.2f}s")


# =============================================================================
# Demo 4: Multi-Provider Concurrent
# =============================================================================


async def demo_multi_provider():
    """Query multiple providers concurrently."""
    print("\n" + "=" * 60)
    print("DEMO 4: Multi-Provider Concurrent Queries")
    print("=" * 60)

    if len(AVAILABLE_PROVIDERS) < 2:
        print("Need at least 2 providers for this demo. Skipping.")
        return

    question = "What is the best way to handle errors in Python? One sentence."

    print(f"\nQuery: {question}")
    print(f"Providers: {', '.join(AVAILABLE_PROVIDERS.keys())}")

    async def query_provider(name: str, factory) -> tuple[str, str, float]:
        """Query a single provider and return (name, response, time)."""
        client = factory()
        start = time.perf_counter()
        try:
            response = await client.chat_async(question)
            elapsed = time.perf_counter() - start
            return (name, response, elapsed)
        except Exception as e:
            elapsed = time.perf_counter() - start
            return (name, f"Error: {e}", elapsed)

    print("\nQuerying all providers concurrently...")
    start = time.perf_counter()

    tasks = [
        query_provider(name, factory)
        for name, factory in AVAILABLE_PROVIDERS.items()
    ]
    results = await asyncio.gather(*tasks)

    total_elapsed = time.perf_counter() - start

    print(f"\nAll responses in {total_elapsed:.2f}s:")
    print("-" * 40)

    for name, response, elapsed in results:
        print(f"\n[{name}] ({elapsed:.2f}s):")
        print(f"  {response[:200]}..." if len(response) > 200 else f"  {response}")


# =============================================================================
# Demo 5: Async with Usage Tracking
# =============================================================================


async def demo_async_with_tracking():
    """Async requests with usage tracking."""
    print("\n" + "=" * 60)
    print("DEMO 5: Async with Usage Tracking")
    print("=" * 60)

    if not AVAILABLE_PROVIDERS:
        print("No providers available. Skipping.")
        return

    from aiskills.integrations import UsageTracker, count_tokens_estimate

    provider_name = next(iter(AVAILABLE_PROVIDERS))
    factory = AVAILABLE_PROVIDERS[provider_name]

    print(f"\nUsing provider: {provider_name}")

    client = factory()
    tracker = UsageTracker()

    questions = [
        "What is asyncio?",
        "What is await?",
        "What is a coroutine?",
    ]

    print(f"\nSending {len(questions)} async requests with tracking...")

    for q in questions:
        response = await client.chat_async(q)

        # Estimate tokens (actual counts would come from API response)
        input_tokens = count_tokens_estimate(q, client.model)
        output_tokens = count_tokens_estimate(response, client.model)

        tracker.add_usage(input_tokens, output_tokens, client.model)

        print(f"  - '{q[:30]}...' -> {output_tokens} tokens")

    print(f"\n--- Usage Summary ---")
    print(f"Total requests: {tracker.stats.requests}")
    print(f"Total tokens: {tracker.total_tokens:,}")
    print(f"Estimated cost: ${tracker.total_cost:.6f}")


# =============================================================================
# Demo 6: Async Timeout Handling
# =============================================================================


async def demo_timeout_handling():
    """Handle timeouts with async requests."""
    print("\n" + "=" * 60)
    print("DEMO 6: Async Timeout Handling")
    print("=" * 60)

    if not AVAILABLE_PROVIDERS:
        print("No providers available. Skipping.")
        return

    provider_name = next(iter(AVAILABLE_PROVIDERS))
    factory = AVAILABLE_PROVIDERS[provider_name]

    print(f"\nUsing provider: {provider_name}")

    client = factory()

    print("\nSending request with 30s timeout...")

    try:
        response = await asyncio.wait_for(
            client.chat_async("Say hello in one word."),
            timeout=30.0,
        )
        print(f"Response: {response}")

    except asyncio.TimeoutError:
        print("Request timed out after 30s")

    print("\nDemo: Very short timeout (0.001s) - expected to fail:")
    try:
        response = await asyncio.wait_for(
            client.chat_async("Say hello."),
            timeout=0.001,
        )
        print(f"Response: {response}")
    except asyncio.TimeoutError:
        print("  Request timed out (expected)")


# =============================================================================
# Main
# =============================================================================


async def main():
    """Run all demos."""
    print("=" * 60)
    print("AI Skills Async Usage Demo")
    print("=" * 60)

    print("\nChecking available providers...")
    check_providers()

    if not AVAILABLE_PROVIDERS:
        print("\nNo providers available!")
        print("Set API keys or install Ollama to run demos.")
        print("\nExample:")
        print("  export OPENAI_API_KEY='sk-...'")
        print("  # or")
        print("  ollama pull llama3.1")
        return

    print(f"\nUsing {len(AVAILABLE_PROVIDERS)} provider(s)")

    # Run demos
    await demo_basic_async()
    await demo_concurrent_requests()
    await demo_async_streaming()
    await demo_multi_provider()
    await demo_async_with_tracking()
    await demo_timeout_handling()

    print("\n" + "=" * 60)
    print("All demos completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
