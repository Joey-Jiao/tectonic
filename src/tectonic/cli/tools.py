from pathlib import Path
from typing import Annotated

import typer

from tectonic import config
from tectonic.core import tools as core_tools, ui


def tools(
    list_tools: Annotated[
        bool,
        typer.Option("--list", "-l", help="List declared tools"),
    ] = False,
    status: Annotated[
        bool,
        typer.Option("--status", "-s", help="Show source + wrapper status"),
    ] = False,
) -> None:
    """Install and update CLI tools."""
    root = Path(config.configs.get("tools.root", "~/workspace")).expanduser()
    defined = config.configs.get("tools.tools", {})

    if not defined:
        ui.info("No tools defined")
        return

    if list_tools:
        for name, defn in defined.items():
            ui.console.print(f"  [bold]{name}[/bold]  [dim]{defn.get('repo', '')}[/dim]")
        return

    if status:
        for name, defn in defined.items():
            src, wrap = core_tools.tool_status(name, defn, root)
            src_color = {"missing": "red", "dirty": "yellow", "clean": "green"}[src]
            wrap_color = {"missing": "red", "stale": "yellow", "ok": "green"}[wrap]
            ui.console.print(
                f"  {name}: source [{src_color}]{src}[/{src_color}], "
                f"wrapper [{wrap_color}]{wrap}[/{wrap_color}]"
            )
        return

    ui.section("Tools")
    for name, defn in defined.items():
        core_tools.install_tool(name, defn, root)
    ui.ok("Tools ready")
