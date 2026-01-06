# Ai Skills Python SDK

The **Ai Skills SDK** allows you to integrate skill management directly into your Python custom agents and applications.

## 📦 Installation

```bash
pip install aiskills
```

## 🚀 Quick Start

```python
from aiskills import SkillManager

# Initialize manager (points to default ~/.aiskills or local .aiskills)
manager = SkillManager()

# 1. Search for skills
results = manager.search("calculate fibonacci")
best_skill = results[0]

print(f"Found skill: {best_skill.name}")

# 2. Read and Render a skill
# This resolves templates, includes, and variables
rendered = manager.read_skill(
    "python-math", 
    variables={"complexity": "medium"}
)

print(rendered.content)
```

## 📚 Core Classes

### `SkillManager`
The main entry point.
-   `search(query: str, limit: int = 5) -> List[SkillMatch]`
-   `read_skill(name: str, variables: Dict = None) -> RenderedSkill`
-   `list_skills() -> List[SkillManifest]`
-   `add_skill_source(path: str)`

### `Skill`
Represents a loaded skill.
-   `name`: Unique identifier
-   `description`: Human-readable description
-   `content`: Raw markdown content
-   `metadata`: Dictionary of YAML frontmatter

## 🔗 Advanced Usage

### Using Custom Storage
```python
from aiskills import SkillManager, FileProperties

# Use a custom directory for skills
manager = SkillManager(storage_path="./my-agent-skills")
```

### Direct Vector Search (Low Level)
```python
# Access the underlying search engine
results = manager.search_engine.query(
    text="database optimization",
    n_results=3,
    where={"tag": "sql"}
)
```
