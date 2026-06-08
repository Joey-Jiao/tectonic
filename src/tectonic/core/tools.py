from pathlib import Path
from typing import Any

from tectonic.core import fs, process, ui

DIR_BIN = Path.home() / ".local" / "bin"


def _wrapper_content(name: str, path: Path) -> str:
    return f'#!/bin/sh\nexec uv run --project {path} {name} "$@"\n'


def _pull_skip_reason(stderr: str) -> str:
    text = stderr.lower()
    if "would be overwritten" in text or "uncommitted" in text or "local changes" in text:
        return "uncommitted changes"
    if "not possible to fast-forward" in text or "diverged" in text or "non-fast-forward" in text:
        return "diverged from upstream"
    if "no tracking information" in text or "no upstream" in text:
        return "no upstream configured"
    return "pull failed"


def ensure_source(name: str, repo: str, path: Path) -> None:
    if not path.exists():
        ui.step(f"Cloning {name}")
        fs.ensure_dir(path.parent)
        process.run(["git", "clone", repo, str(path)])
        ui.ok(f"{name}: cloned")
        return

    result = process.run(
        ["git", "pull", "--ff-only"], cwd=path, check=False, capture=True,
    )
    if result.returncode == 0:
        ui.ok(f"{name}: pulled")
    else:
        ui.warn(f"{name}: skipping pull ({_pull_skip_reason(result.stderr)})")


def ensure_wrapper(name: str, path: Path) -> None:
    bin_path = DIR_BIN / name
    content = _wrapper_content(name, path)
    if bin_path.exists() and bin_path.read_text() == content:
        ui.info(f"{name}: wrapper up to date")
        return
    fs.ensure_dir(bin_path.parent)
    bin_path.write_text(content)
    bin_path.chmod(0o755)
    ui.ok(f"{name}: wrapper installed")


def install_tool(name: str, defn: dict[str, Any], root: Path) -> None:
    path = root / defn["path"]
    ensure_source(name, defn["repo"], path)
    ensure_wrapper(name, path)


def tool_status(name: str, defn: dict[str, Any], root: Path) -> tuple[str, str]:
    path = root / defn["path"]
    if not path.exists():
        source = "missing"
    else:
        result = process.run(
            ["git", "status", "--porcelain"], cwd=path, check=False, capture=True,
        )
        source = "dirty" if result.stdout.strip() else "clean"

    bin_path = DIR_BIN / name
    if not bin_path.exists():
        wrapper = "missing"
    elif bin_path.read_text() == _wrapper_content(name, path):
        wrapper = "ok"
    else:
        wrapper = "stale"

    return source, wrapper
