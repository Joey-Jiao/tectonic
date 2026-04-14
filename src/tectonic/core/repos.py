from pathlib import Path
from typing import Any

from tectonic.core import process, ui


def resolve_repos(hostname: str, repos: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for name, defn in repos.items():
        if hostname in defn.get("hosts", []):
            result[name] = defn["url"]
    return result


def sync_repo(root: Path, name: str, url: str) -> None:
    path = root / name
    if path.exists():
        process.run(["git", "reset", "--hard", "HEAD"], cwd=path)
        process.run(["git", "pull", "--ff-only"], cwd=path)
        ui.ok(f"{name}")
    else:
        ui.step(f"Cloning {name}")
        path.parent.mkdir(parents=True, exist_ok=True)
        process.run(["git", "clone", url, str(path)])
        ui.ok(f"{name}")


def repo_status(root: Path, name: str) -> str:
    path = root / name
    if not path.exists():
        return "missing"
    result = process.run(
        ["git", "status", "--porcelain"], cwd=path, check=False, capture=True,
    )
    if result.stdout.strip():
        return "dirty"
    return "clean"
