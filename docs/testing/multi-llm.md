# Multi-LLM Acceptance Testing

Ai Skills includes comprehensive acceptance tests to validate consistent behavior across different LLM providers. This ensures skills work identically regardless of which AI system invokes them.

## Supported Providers

| Provider | Interface | Test Client |
|----------|-----------|-------------|
| **Claude** | MCP (Model Context Protocol) | `ClaudeMCPClient` |
| **OpenAI/ChatGPT** | Function Calling (REST API) | `OpenAIFunctionClient` |
| **Google Gemini** | Function Calling (simulated) | `GeminiFunctionClient` |
| **Ollama** | Python SDK (direct) | `OllamaLocalClient` |

## Running Tests

```bash
# Run all multi-LLM tests
pytest tests/integration/test_multi_llm.py -v

# Run specific provider tests
pytest tests/integration/test_multi_llm.py::TestClaudeMCPIntegration -v
pytest tests/integration/test_multi_llm.py::TestOpenAIFunctionCalling -v
pytest tests/integration/test_multi_llm.py::TestGeminiFunctionCalling -v
pytest tests/integration/test_multi_llm.py::TestOllamaLocalIntegration -v

# Run cross-provider consistency tests
pytest tests/integration/test_multi_llm.py::TestCrossProviderConsistency -v
```

## Test Categories

### Cross-Provider Consistency Tests

These tests ensure all providers behave identically:

- **`test_all_providers_can_list_skills`**: All providers return the same skill catalog
- **`test_all_providers_can_read_same_skill`**: Content is identical across providers
- **`test_all_providers_apply_variables_consistently`**: Template variables render the same
- **`test_all_providers_search_returns_results`**: Search behavior is consistent
- **`test_all_providers_handle_missing_skill_gracefully`**: Error handling is uniform

### Provider-Specific Tests

Each provider has dedicated tests for its unique integration:

#### Claude MCP
- Tool call format validation
- Metadata in responses
- Variable handling via MCP protocol

#### OpenAI Function Calling
- Tool definition format (`/openai/tools` endpoint)
- Function call/response format
- All functions work correctly

#### Gemini Function Calling
- `functionResponse` format validation
- Simulated Gemini protocol compliance

#### Ollama Local
- Direct Python SDK access
- Token count reporting
- Local-first search

### Provider-Agnostic Tests

Ensure skills don't contain provider-specific bias:

- No Claude/ChatGPT/Gemini-specific instructions in skill content
- Consistent error messages
- Identical default values

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Test Infrastructure                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ BaseLLMClient│  │  SkillResult │  │ SearchResult │       │
│  │   (ABC)      │  │  (dataclass) │  │  (dataclass) │       │
│  └──────┬───────┘  └──────────────┘  └──────────────┘       │
│         │                                                    │
│    ┌────┴────┬──────────┬──────────┐                        │
│    ▼         ▼          ▼          ▼                        │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                        │
│ │Claude│ │OpenAI│ │Gemini│ │Ollama│                        │
│ │ MCP  │ │  Fn  │ │  Fn  │ │Local │                        │
│ └──────┘ └──────┘ └──────┘ └──────┘                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Adding a New Provider

To add tests for a new LLM provider:

1. **Create a client class** implementing `BaseLLMClient`:

```python
class NewProviderClient(BaseLLMClient):
    @property
    def provider_name(self) -> str:
        return "new_provider"

    def use_skill(self, context: str, variables: dict | None = None) -> SkillResult:
        # Implement provider-specific logic
        ...

    def search_skills(self, query: str, limit: int = 10) -> SearchResult:
        ...

    def read_skill(self, name: str, variables: dict | None = None) -> SkillResult:
        ...

    def list_skills(self) -> list[dict]:
        ...
```

2. **Add a fixture**:

```python
@pytest.fixture
def new_provider_client(multi_llm_setup) -> NewProviderClient:
    return NewProviderClient(
        manager=multi_llm_setup["manager"],
        router=multi_llm_setup["router"],
        registry=multi_llm_setup["registry"],
    )
```

3. **Update `all_clients` fixture** to include the new provider

4. **Add provider-specific tests** if needed

## Best Practices for Provider-Agnostic Skills

When writing skills that work across all providers:

1. **Avoid provider-specific instructions**:
   ```markdown
   # Bad
   When Claude processes this skill, it should...

   # Good
   When processing this skill, the AI should...
   ```

2. **Use standard variable syntax**:
   ```yaml
   variables:
     language:
       type: string
       default: python
   ```

3. **Test with multiple providers** before publishing:
   ```bash
   pytest tests/integration/test_multi_llm.py -v
   ```

4. **Document any provider-specific behavior** in the skill's README

## Continuous Integration

Add to your CI pipeline:

```yaml
# .github/workflows/test.yml
- name: Run Multi-LLM Tests
  run: |
    pip install .[test]
    pytest tests/integration/test_multi_llm.py -v --tb=short
```

## Related Documentation

- [Claude Desktop Integration](../integrations/claude_desktop.md)
- [OpenAI/ChatGPT Integration](../integrations/chatgpt.md)
- [Gemini Integration](../integrations/gemini.md)
- [Ollama Integration](../integrations/ollama.md)
