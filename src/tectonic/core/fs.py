import shutil
from datetime import datetime
from pathlib import Path

from tectonic.core import ui


def ensure_dir(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True)
        ui.info(f"Created directory: {path}")


def backup(path: Path, backup_dir: Path | None = None) -> Path | None:
    if not path.exists() or path.is_symlink():
        return None

    if backup_dir is None:
        backup_dir = Path.home() / ".dotfiles.backup"

    ensure_dir(backup_dir)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = backup_dir / f"{path.name}.{timestamp}"
    shutil.copy2(path, backup_path)
    ui.info(f"Backed up: {path} -> {backup_path}")
    return backup_path


def symlink(src: Path, dst: Path, do_backup: bool = True) -> None:
    if not src.exists():
        ui.error(f"Source not found: {src}")
        return

    if dst.is_symlink():
        current = dst.resolve()
        if current == src.resolve():
            ui.info(f"Already linked: {dst} -> {src}")
            return
        dst.unlink()
    elif dst.exists():
        if do_backup:
            backup(dst)
        dst.unlink()

    dst.symlink_to(src)
    ui.ok(f"Linked: {dst} -> {src}")


def files_equal(src: Path, dst: Path) -> bool:
    """Compare two files by content."""
    if src.stat().st_size != dst.stat().st_size:
        return False
    return src.read_bytes() == dst.read_bytes()


def copy(src: Path, dst: Path, do_backup: bool = True) -> None:
    if not src.exists():
        ui.error(f"Source not found: {src}")
        return

    if dst.exists():
        if files_equal(src, dst):
            ui.info(f"Already up to date: {dst}")
            return
        if do_backup:
            backup(dst)

    ensure_dir(dst.parent)
    shutil.copy2(src, dst)
    ui.ok(f"Copied: {src} -> {dst}")


def copy_dir(src: Path, dst: Path) -> None:
    if not src.is_dir():
        ui.error(f"Source is not a directory: {src}")
        return

    if dst.exists():
        ui.info(f"Directory already exists: {dst}")
        return

    shutil.copytree(src, dst)
    ui.ok(f"Copied directory: {src} -> {dst}")


def copy_tree(src: Path, dst: Path, do_backup: bool = True) -> None:
    if not src.is_dir():
        ui.error(f"Source is not a directory: {src}")
        return

    for item in src.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(src)
            dest_file = dst / rel_path
            ensure_dir(dest_file.parent)
            copy(item, dest_file, do_backup=do_backup)
