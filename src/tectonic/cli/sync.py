from glob import glob
from pathlib import Path
from typing import Annotated

import typer
import yaml

from tectonic import config
from tectonic.core import host, process, ui

SYNC_CONFIG = config.CONFIGS_DIR / "sync.yaml"


def _load_sync_config() -> dict:
    with SYNC_CONFIG.open() as f:
        return yaml.safe_load(f) or {}


def _expand_paths(root: Path, patterns: list[str]) -> list[Path]:
    paths = []
    for pattern in patterns:
        matches = sorted(glob(str(root / pattern)))
        paths.extend(Path(m) for m in matches if Path(m).is_dir())
    return paths


def _resolve_targets(cfg: dict, target_filter: str | None = None) -> list[tuple[Path, list[Path]]]:
    results = []
    for target in cfg.get("targets", []):
        root = Path(target["root"]).expanduser()
        if target_filter and root.name != target_filter:
            continue
        if not root.is_dir():
            ui.warn(f"Sync root does not exist, skipping: {root}")
            continue
        patterns = target.get("paths")
        if patterns:
            paths = _expand_paths(root, patterns)
        else:
            paths = [root]
        if paths:
            results.append((root, paths))
    return results


def _read_ignore_files(directory: Path, ignore_files: list[str]) -> list[str]:
    patterns: list[str] = []
    for name in ignore_files:
        ignore_path = directory / name
        if not ignore_path.is_file():
            continue
        for line in ignore_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.append(line)
    return patterns


def _rsync(src: Path, dest_host: str, dest_path: Path, excludes: list[str],
           ignore_files: list[str], delete: bool, dry_run: bool) -> bool:
    all_excludes = excludes + _read_ignore_files(src, ignore_files)
    cmd = ["rsync", "-avz"]
    for pattern in all_excludes:
        cmd.extend(["--exclude", pattern])
    if delete:
        cmd.append("--delete")
    if dry_run:
        cmd.append("--dry-run")
    cmd.append(f"{src}/")
    cmd.append(f"{dest_host}:{dest_path}/")

    try:
        process.run_interactive(cmd)
        return True
    except Exception as e:
        ui.error(f"rsync failed: {e}")
        return False


def sync(
    hostname: str = typer.Argument(None, help="Target host (default: all)"),
    root: Annotated[
        str | None,
        typer.Option("--root", "-r", help="Sync root name (e.g. workspace, misc)"),
    ] = None,
    delete: Annotated[
        bool,
        typer.Option("--delete", help="Delete files on target that don't exist locally"),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show what would be synced without executing"),
    ] = False,
) -> None:
    """Push workspace data to remote hosts via rsync."""
    cfg = _load_sync_config()
    excludes = cfg.get("exclude", [])
    ignore_files = cfg.get("ignore_files", [])
    resolved = _resolve_targets(cfg, root)

    if not resolved:
        ui.info("No sync targets resolved")
        return

    hosts_config = host.load_hosts(config.HOSTS_FILE)
    targets = host.resolve_deploy_targets(hosts_config)

    if hostname:
        targets = [t for t in targets if t.name == hostname]
        if not targets:
            ui.error(f"Host '{hostname}' is not a valid sync target")
            raise typer.Exit(code=1)

    if not targets:
        ui.info("No sync targets found")
        return

    ui.section("Sync" + (" (dry-run)" if dry_run else ""))

    for target in targets:
        ssh_dest = f"{target.user}@{target.ssh_host}"
        ui.step(f"{target.name}")
        for root, paths in resolved:
            for path in paths:
                if path == root:
                    label = root.name
                else:
                    label = str(path.relative_to(root))
                ui.info(f"  {label}")
                _rsync(path, ssh_dest, path, excludes, ignore_files, delete, dry_run)

    ui.ok("Sync complete")
