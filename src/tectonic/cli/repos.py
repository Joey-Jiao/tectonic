from pathlib import Path
from typing import Annotated

import typer

from tectonic import config
from tectonic.core import host, repos as core_repos, ui


def repos(
    list_repos: Annotated[
        bool,
        typer.Option("--list", "-l", help="List repos for current host"),
    ] = False,
    status: Annotated[
        bool,
        typer.Option("--status", "-s", help="Show repo status"),
    ] = False,
) -> None:
    """Clone and pull repos declared for current host."""
    hostname = host.get_hostname()
    root = Path(config.configs.get("repos.root", "~/workspace")).expanduser()
    matched = core_repos.resolve_repos(hostname, config.configs.get("repos.repos", {}))

    if not matched:
        ui.info(f"No repos defined for host: {hostname}")
        return

    if list_repos:
        for name, url in matched.items():
            ui.console.print(f"  [bold]{name}[/bold]  [dim]{url}[/dim]")
        return

    if status:
        for name in matched:
            state = core_repos.repo_status(root, name)
            if state == "missing":
                label = "[red]missing[/red]"
            elif state == "dirty":
                label = "[yellow]dirty[/yellow]"
            else:
                label = "[green]clean[/green]"
            ui.console.print(f"  {name}: {label}")
        return

    ui.section("Repos")
    for name, url in matched.items():
        core_repos.sync_repo(root, name, url)
