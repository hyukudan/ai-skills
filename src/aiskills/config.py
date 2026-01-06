"""Configuration management for aiskills."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from .constants import GLOBAL_BASE


class EmbeddingConfig(BaseModel):
    """Configuration for embedding provider."""

    provider: Literal["fastembed", "openai", "none"] = "fastembed"
    model: str = "BAAI/bge-small-en-v1.5"
    api_key: str | None = None
    base_url: str | None = None


class VectorStoreConfig(BaseModel):
    """Configuration for vector store."""

    provider: Literal["chroma", "none"] = "chroma"
    path: Path | None = None  # Uses default if None


class StorageConfig(BaseModel):
    """Configuration for storage paths."""

    global_dir: Path = Field(default_factory=lambda: GLOBAL_BASE)
    project_dir: str = ".aiskills"  # Relative to cwd


class SearchConfig(BaseModel):
    """Configuration for search behavior."""

    semantic_weight: float = 0.7  # Weight for semantic search (vs text)
    default_limit: int = 10
    cache_ttl_seconds: int = 300


class AppConfig(BaseModel):
    """Main application configuration."""

    storage: StorageConfig = Field(default_factory=StorageConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)

    # Behavior flags
    auto_install_deps: bool = True
    validate_on_load: bool = True
    use_cache: bool = True


# Global config instance (lazy loaded)
_config: AppConfig | None = None


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def load_config(config_path: Path | None = None) -> AppConfig:
    """Load configuration from file or use defaults.

    Priority:
    1. Explicit config_path
    2. Project config (.aiskills/aiskills.yaml)
    3. Global config (~/.aiskills/aiskills.yaml)
    4. Defaults
    """
    import yaml

    search_paths = []

    if config_path:
        search_paths.append(config_path)
    else:
        # Project config
        search_paths.append(Path.cwd() / ".aiskills" / "aiskills.yaml")
        # Global config
        search_paths.append(GLOBAL_BASE / "aiskills.yaml")

    for path in search_paths:
        if path.exists():
            with open(path) as f:
                data = yaml.safe_load(f) or {}
                return AppConfig(**data)

    return AppConfig()


def set_config(config: AppConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config
