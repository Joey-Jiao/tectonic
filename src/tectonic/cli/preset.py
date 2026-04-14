from pathlib import Path
from typing import Annotated

import typer

from tectonic import config
from tectonic.core import host, process, repos, ui


def _check_requirements(reqs: dict) -> bool:
    if not reqs:
        return True

    repo_names = reqs.get("repos", [])
    if repo_names:
        root = Path(config.configs.get("repos.root", "~/workspace")).expanduser()
        all_ready = True
        for name in repo_names:
            ready, reason = repos.repo_ready(root, name)
            if ready:
                ui.ok(f"{name}")
            else:
                ui.error(f"{name}: {reason}")
                all_ready = False
        if not all_ready:
            return False

    return True


def preset(
    name: str = typer.Argument(None, help="Preset name to run"),
    list_presets: Annotated[
        bool,
        typer.Option("--list", "-l", help="List available presets"),
    ] = False,
) -> None:
    """Run a predefined workflow."""
    if list_presets or name is None:
        names = config.configs.list_files("preset")
        if not names:
            ui.info("No presets defined")
            return
        for n in names:
            desc = config.configs.get(f"preset.{n}.description", "")
            ui.console.print(f"  [bold]{n}[/bold]  [dim]{desc}[/dim]")
        return

    steps = config.configs.get(f"preset.{name}.steps")
    if not steps:
        ui.error(f"Preset '{name}' not found")
        raise typer.Exit(code=1)

    reqs = config.configs.get(f"preset.{name}.requirements", {})
    desc = config.configs.get(f"preset.{name}.description", name)

    ui.section(f"Preset: {desc}")

    if reqs:
        ui.step("Checking requirements")
        if not _check_requirements(reqs):
            ui.error("Requirements not met")
            raise typer.Exit(code=1)

    for step in steps:
        ui.step(f"$ {step}")
        process.run_interactive(["zsh", "-c", step])

    ui.ok("Preset complete")
