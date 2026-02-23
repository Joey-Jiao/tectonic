from pathlib import Path
from typing import Any

from yaml import safe_load


class ConfigService:
    def __init__(self, config_dir: str | Path = "configs"):
        self._config_dir = Path(config_dir)
        self._cache: dict[tuple[str, str], dict[str, Any] | None] = {}
        self._folders: set[str] = set()
        self._scan_config_tree()

    def _scan_config_tree(self) -> None:
        if not self._config_dir.exists():
            return
        for item in self._config_dir.iterdir():
            if item.is_dir():
                self._folders.add(item.name)
                for yaml_file in item.glob("*.yaml"):
                    self._cache[(item.name, yaml_file.stem)] = None
            elif item.suffix == ".yaml":
                self._cache[("", item.stem)] = None

    def _load_file(self, folder: str, file: str) -> dict[str, Any]:
        key = (folder, file)
        if key not in self._cache:
            return {}
        if self._cache[key] is None:
            if folder:
                path = self._config_dir / folder / f"{file}.yaml"
            else:
                path = self._config_dir / f"{file}.yaml"
            with open(path) as f:
                self._cache[key] = safe_load(f) or {}
        return self._cache[key]  # type: ignore[return-value]

    def get(self, keys: str, default: Any = None) -> Any:
        parts = keys.split(".")
        if len(parts) < 2:
            return default
        folder, file, *yaml_path = parts
        if folder in self._folders:
            content = self._load_file(folder, file)
            return self._traverse(content, yaml_path, default)
        file = parts[0]
        yaml_path = parts[1:]
        content = self._load_file("", file)
        return self._traverse(content, yaml_path, default)

    def _traverse(self, data: dict[str, Any], path: list[str], default: Any) -> Any:
        value: Any = data
        for key in path:
            if not isinstance(value, dict):
                return default
            value = value.get(key)
            if value is None:
                return default
        return value

    def list_files(self, folder: str = "") -> list[str]:
        return [f for (fo, f) in self._cache if fo == folder]
