# Troubleshooting Guide

Common issues and solutions when using AI Skills with LLM providers.

---

## Installation Issues

### "No module named 'openai'" (or other provider)

**Problem:** Provider SDK not installed.

**Solution:** Install the specific provider package:
```bash
# For specific providers
pip install aiskills[openai]
pip install aiskills[anthropic]
pip install aiskills[gemini]
pip install aiskills[ollama]

# Or install all
pip install aiskills[llms]
```

### "No module named 'chromadb'" or embedding errors

**Problem:** Vector store dependencies missing.

**Solution:**
```bash
pip install aiskills[embeddings]
# or
pip install chromadb fastembed
```

---

## API Key Issues

### "API key not found" / "Authentication failed"

**Problem:** API key not set or invalid.

**Solutions:**

1. **Set environment variable:**
   ```bash
   # OpenAI
   export OPENAI_API_KEY="sk-..."

   # Anthropic
   export ANTHROPIC_API_KEY="sk-ant-..."

   # Gemini
   export GEMINI_API_KEY="..."
   # or
   export GOOGLE_API_KEY="..."
   ```

2. **Pass directly to client:**
   ```python
   from aiskills.integrations import create_openai_client

   client = create_openai_client(api_key="sk-...")
   ```

3. **Check key validity:**
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/
   - Google: https://aistudio.google.com/app/apikey

---

## Rate Limiting

### "Rate limit exceeded" / 429 errors

**Problem:** Too many requests to the API.

**Solutions:**

1. **Built-in retry handles this automatically:**
   ```python
   from aiskills.integrations import create_openai_client

   # Retry is automatic with exponential backoff
   client = create_openai_client()
   response = client.chat("...")  # Will retry on 429
   ```

2. **Catch and handle manually:**
   ```python
   from aiskills.integrations import RateLimitError

   try:
       response = client.chat("...")
   except RateLimitError as e:
       print(f"Rate limited. Retry after {e.retry_after}s")
   ```

3. **Reduce request frequency:**
   - Add delays between requests
   - Use batch processing
   - Upgrade API tier

---

## Ollama Issues

### "Ollama model not found"

**Problem:** Model not pulled locally.

**Solution:**
```bash
# List available models
ollama list

# Pull the model
ollama pull llama3.1
ollama pull mistral
ollama pull codellama
```

### "Connection refused" to Ollama

**Problem:** Ollama server not running.

**Solution:**
```bash
# Start Ollama server
ollama serve

# Or check if running
curl http://localhost:11434/api/tags
```

### "Tool calling not working" with Ollama

**Problem:** Model doesn't support tool calling.

**Solution:** Use a tool-capable model:
```python
from aiskills.integrations import create_ollama_client

# Tool-capable models
client = create_ollama_client(model="llama3.1")      # Recommended
client = create_ollama_client(model="mistral-nemo")
client = create_ollama_client(model="mixtral")

# Or use prompt injection for non-tool models
client = create_ollama_client(model="codellama", use_tools=False)
response = client.chat_with_skill("python debugging", "Fix this code...")
```

---

## Gemini Issues

### "Quota exceeded" with Gemini

**Problem:** Free tier limits reached.

**Solutions:**
1. Wait for quota reset (daily)
2. Enable billing in Google Cloud Console
3. Use a different provider as fallback

### "Function calling not working" with Gemini

**Problem:** Gemini handles function calling differently.

**Note:** Gemini uses automatic function calling internally. The SDK handles this:
```python
from aiskills.integrations import create_gemini_client

client = create_gemini_client(auto_function_calling=True)  # Default
response = client.chat("Help me debug Python")  # Tools called automatically
```

---

## Tool Execution Errors

### "Unknown tool: xyz"

**Problem:** Calling a tool that doesn't exist.

**Solution:** Check available tools:
```python
from aiskills.integrations import get_openai_tools

tools = get_openai_tools()
for tool in tools:
    print(tool["function"]["name"])

# Available tools:
# - use_skill
# - skill_search
# - skill_read
# - skill_list
# - skill_browse
```

### "Missing required parameter"

**Problem:** Tool called without required arguments.

**Solution:**
```python
from aiskills.integrations import ToolValidationError

try:
    result = client.execute_tool("use_skill", {})  # Missing 'context'
except ToolValidationError as e:
    print(f"Missing: {e.invalid_args}")  # ['context']
```

---

## Skill Issues

### "No skills found"

**Problem:** Skills not installed or indexed.

**Solutions:**

1. **Check installed skills:**
   ```python
   skills = client.list_skills()
   print(f"Found {len(skills)} skills")
   ```

2. **Install example skills:**
   ```bash
   aiskills install examples/skills/
   ```

3. **Rebuild index:**
   ```bash
   aiskills index --rebuild
   ```

### "Skill content is empty"

**Problem:** Skill file exists but has no content.

**Solution:** Check the skill file:
```bash
aiskills show skill-name
```

---

## Async Issues

### "coroutine was never awaited"

**Problem:** Forgot to await async method.

**Solution:**
```python
import asyncio
from aiskills.integrations import create_openai_client

async def main():
    client = create_openai_client()

    # Wrong - missing await
    # response = client.chat_async("Hello")

    # Correct
    response = await client.chat_async("Hello")
    print(response)

asyncio.run(main())
```

### "Event loop already running"

**Problem:** Running asyncio.run() inside Jupyter/IPython.

**Solution:**
```python
# In Jupyter, use await directly (no asyncio.run)
client = create_openai_client()
response = await client.chat_async("Hello")

# Or use nest_asyncio
import nest_asyncio
nest_asyncio.apply()
```

---

## Performance Issues

### Slow response times

**Solutions:**

1. **Use streaming:**
   ```python
   for chunk in client.chat_stream("..."):
       print(chunk, end="", flush=True)
   ```

2. **Use faster models:**
   - OpenAI: `gpt-4o-mini` instead of `gpt-4`
   - Anthropic: `claude-3-haiku` instead of `opus`
   - Gemini: `gemini-1.5-flash` instead of `pro`

3. **Use async for concurrent requests:**
   ```python
   import asyncio

   async def query_multiple():
       tasks = [
           client.chat_async("Question 1"),
           client.chat_async("Question 2"),
       ]
       return await asyncio.gather(*tasks)
   ```

### High costs

**Solutions:**

1. **Track usage:**
   ```python
   from aiskills.integrations import UsageTracker

   tracker = UsageTracker()
   tracker.add_usage(input_tokens, output_tokens, "gpt-4")
   print(f"Total cost: ${tracker.total_cost:.4f}")
   ```

2. **Use cheaper models:**
   - `gpt-4o-mini`: ~50x cheaper than `gpt-4`
   - `claude-3-haiku`: ~60x cheaper than `opus`
   - Ollama: Free (local)

3. **Use skill browsing first:**
   ```python
   # Browse (cheap) before loading full skill (expensive)
   skills = client.browse_skills(context="debugging")
   if skills:
       result = client.read_skill(skills[0]["name"])
   ```

---

## Debugging Tips

### Enable logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("aiskills")
logger.setLevel(logging.DEBUG)
```

### Check provider response

```python
# Get raw response for debugging
client = create_openai_client(auto_execute=False)
response = client.get_completion_with_skills(
    messages=[{"role": "user", "content": "..."}]
)
print(response)  # Raw API response
```

### Validate tool arguments

```python
from aiskills.integrations import validate_tool_arguments, get_tool_schema

schema = get_tool_schema("use_skill")
if schema:
    required, params = schema
    validated = validate_tool_arguments(
        "use_skill",
        {"context": "debug python"},
        required,
        params,
    )
```

---

## Getting Help

1. **Check documentation:**
   - [Examples README](../examples/README.md)
   - [Provider Comparison](provider-comparison.md)

2. **Report issues:**
   - GitHub: https://github.com/hyukudan/ai-skills/issues

3. **Common error codes:**
   | Code | Meaning | Action |
   |------|---------|--------|
   | 401 | Invalid API key | Check credentials |
   | 429 | Rate limited | Wait and retry |
   | 500 | Server error | Retry later |
   | 503 | Service unavailable | Check provider status |
