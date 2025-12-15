import difflib
from pathlib import Path
from typing import Annotated

import typer

from lxs import config
from lxs.core import fs, ui

app = typer.Typer(no_args_is_help=True)


DOTFILE_TREES = [
    ("home", Path.home()),
    ("config", config.XDG_CONFIG_HOME),
    ("local", config.DIR_LOCAL),
]


def get_dotfile_mappings() -> list[tuple[Path, Path]]:
    """Return list of (source, destination) pairs for all managed dotfiles."""
    mappings = []

    for src_name, dst_base in DOTFILE_TREES:
        src_dir = config.DOTFILES_DIR / src_name
        if not src_dir.exists():
            continue

        for src_file in src_dir.rglob("*"):
            if src_file.is_file():
                rel_path = src_file.relative_to(src_dir)
                dst_file = dst_base / rel_path
                mappings.append((src_file, dst_file))

    return mappings


def file_diff(src: Path, dst: Path) -> list[str] | None:
    """Return unified diff between two text files. Returns None for binary files."""
    if not src.exists():
        return [f"Source not found: {src}"]
    if not dst.exists():
        return [f"Destination not found: {dst}"]

    try:
        src_lines = src.read_text().splitlines(keepends=True)
        dst_lines = dst.read_text().splitlines(keepends=True)
    except UnicodeDecodeError:
        return None  # Binary file

    return list(difflib.unified_diff(
        dst_lines,
        src_lines,
        fromfile=str(dst),
        tofile=str(src),
    ))


@app.command()
def status() -> None:
    """Show status of managed dotfiles."""
    mappings = get_dotfile_mappings()

    modified = []
    missing = []
    up_to_date = []

    for src, dst in mappings:
        if not src.exists():
            continue

        if not dst.exists():
            missing.append((src, dst))
        elif dst.is_symlink():
            modified.append((src, dst, "symlink (will be replaced)"))
        elif not fs.files_equal(src, dst):
            modified.append((src, dst, "modified"))
        else:
            up_to_date.append((src, dst))

    if missing:
        ui.section("Missing (will be created)")
        for src, dst in missing:
            ui.console.print(f"  [yellow]+[/yellow] {dst}")

    if modified:
        ui.section("Modified (will be updated)")
        for src, dst, reason in modified:
            ui.console.print(f"  [red]~[/red] {dst} ({reason})")

    if up_to_date:
        ui.section("Up to date")
        for src, dst in up_to_date:
            ui.console.print(f"  [green]✓[/green] {dst}")

    if not missing and not modified:
        ui.ok("All dotfiles are up to date")


@app.command()
def diff() -> None:
    """Show diff between source and deployed dotfiles."""
    mappings = get_dotfile_mappings()
    has_diff = False

    for src, dst in mappings:
        if not src.exists() or not dst.exists():
            continue

        if dst.is_symlink():
            ui.console.print(f"\n[yellow]{dst}[/yellow]: is a symlink -> {dst.resolve()}")
            has_diff = True
            continue

        if not fs.files_equal(src, dst):
            has_diff = True
            diff_lines = file_diff(src, dst)
            if diff_lines is None:
                ui.console.print(f"\n[bold]{dst}[/bold]: [dim]binary file differs[/dim]")
            elif diff_lines:
                ui.console.print(f"\n[bold]{dst}[/bold]:")
                for line in diff_lines:
                    if line.startswith("+") and not line.startswith("+++"):
                        ui.console.print(f"[green]{line.rstrip()}[/green]")
                    elif line.startswith("-") and not line.startswith("---"):
                        ui.console.print(f"[red]{line.rstrip()}[/red]")
                    else:
                        ui.console.print(line.rstrip())

    if not has_diff:
        ui.ok("No differences found")


@app.command()
def sync(
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite without prompting"),
    ] = False,
) -> None:
    """Sync dotfiles from source to destination."""
    mappings = get_dotfile_mappings()

    synced = 0
    for src, dst in mappings:
        if not src.exists():
            ui.warn(f"Source not found: {src}")
            continue

        needs_update = False

        if not dst.exists():
            needs_update = True
        elif dst.is_symlink():
            needs_update = True
            dst.unlink()
        elif not fs.files_equal(src, dst):
            needs_update = True

        if needs_update:
            fs.copy(src, dst, do_backup=not force)
            synced += 1

    if synced:
        ui.ok(f"Synced {synced} file(s)")
    else:
        ui.ok("All dotfiles already up to date")
