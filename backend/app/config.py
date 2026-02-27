import os
from pathlib import Path
from typing import Any

import yaml


class Config:
    _instance = None
    _config: dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        config_path = Path(__file__).parent.parent / "config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            self._config = yaml.safe_load(f)

    def reload(self) -> None:
        self._load_config()

    @property
    def config_path(self) -> Path:
        return Path(__file__).parent.parent / "config.yaml"

    def save(self) -> None:
        with open(self.config_path, "w") as f:
            yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)

    def update_config(self, new_config: dict[str, Any]) -> None:
        self._config = new_config
        self.save()
        self.reload()

    @property
    def app(self) -> dict[str, Any]:
        return self._config.get("app", {})

    @property
    def host(self) -> str:
        return self.app.get("host", "0.0.0.0")

    @property
    def port(self) -> int:
        return self.app.get("port", 5000)

    @property
    def auth(self) -> dict[str, Any]:
        return self._config.get("auth", {})

    @property
    def api_key(self) -> str:
        return self.auth.get("api_key", "")

    @property
    def default_provider(self) -> str:
        return self._config.get("default_provider", "openai")

    @property
    def timeout(self) -> int:
        return self._config.get("timeout", 120)

    @property
    def providers(self) -> dict[str, dict[str, Any]]:
        return self._config.get("providers", {})

    def get_provider_config(self, name: str) -> dict[str, Any]:
        provider = self.providers.get(name, {}).copy()
        if "default_model" not in provider:
            provider["default_model"] = self.get_default_model(name)
        return provider

    @property
    def storage(self) -> dict[str, Any]:
        return self._config.get("storage", {})

    @property
    def data_dir(self) -> Path:
        dir_name = self.storage.get("data_dir", "./data")
        return Path(__file__).parent.parent.parent / dir_name

    @property
    def context_dir(self) -> Path:
        return self.data_dir / "context"

    def get_context_files(self) -> list[str]:
        self.context_dir.mkdir(parents=True, exist_ok=True)
        return sorted([f.name for f in self.context_dir.glob("*.md")])

    def get_context_file(self, filename: str) -> str | None:
        filepath = self.context_dir / filename
        if not filepath.exists():
            return None
        return filepath.read_text(encoding="utf-8")

    def save_context_file(self, filename: str, content: str) -> None:
        filepath = self.context_dir / filename
        filepath.write_text(content, encoding="utf-8")

    def get_default_model(self, provider: str) -> str:
        return self.providers.get(provider, {}).get("default_model", "")

    @property
    def context_config(self) -> dict[str, Any]:
        return self._config.get("context", {})

    def get_enabled_context_files(self) -> list[str]:
        return self.context_config.get("enabled_files", [])

    def set_enabled_context_files(self, files: list[str]) -> None:
        if "context" not in self._config:
            self._config["context"] = {}
        self._config["context"]["enabled_files"] = files
        self.save()

    def create_context_file(self, filename: str, content: str = "") -> None:
        if not filename.endswith(".md"):
            filename = filename + ".md"
        filepath = self.context_dir / filename
        if filepath.exists():
            raise FileExistsError(f"File already exists: {filename}")
        filepath.write_text(content, encoding="utf-8")

    def delete_context_file(self, filename: str) -> None:
        filepath = self.context_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filename}")
        filepath.unlink()
        enabled = self.get_enabled_context_files()
        if filename in enabled:
            enabled.remove(filename)
            self.set_enabled_context_files(enabled)

    def rename_context_file(self, old_name: str, new_name: str) -> None:
        if not new_name.endswith(".md"):
            new_name = new_name + ".md"
        old_path = self.context_dir / old_name
        new_path = self.context_dir / new_name
        if not old_path.exists():
            raise FileNotFoundError(f"File not found: {old_name}")
        if new_path.exists():
            raise FileExistsError(f"File already exists: {new_name}")
        old_path.rename(new_path)
        enabled = self.get_enabled_context_files()
        if old_name in enabled:
            enabled = [new_name if f == old_name else f for f in enabled]
            self.set_enabled_context_files(enabled)

    @property
    def summarizer_config(self) -> dict[str, Any]:
        return self._config.get("summarizer", {})

    @property
    def summarizer_provider(self) -> str:
        return self.summarizer_config.get("provider", "openai")

    @property
    def summarizer_model(self) -> str:
        return self.summarizer_config.get("model", "gpt-4o-mini")

    @property
    def summarizer_prompt_source(self) -> str:
        return self.summarizer_config.get("prompt_source", "SUMMARIZER.md")

    @property
    def summarizer_temperature(self) -> float:
        return self.summarizer_config.get("temperature", 0.3)

    @property
    def summarization_config(self) -> dict[str, Any]:
        return self._config.get("summarization", {})

    @property
    def default_messages_interval(self) -> int:
        return self.summarization_config.get("default_messages_interval", 10)


config = Config()
