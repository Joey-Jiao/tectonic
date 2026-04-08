from pathlib import Path
from typing import Annotated

import typer
import yaml

from tectonic import config
from tectonic.cli.deploy import TECTONIC_PREFIX
from tectonic.core import host, process, repos as core_repos, ui


def _load_repos_config() -> dict:
    with config.PULL_FILE.open() as f:
        return yaml.safe_load(f) or {}


def pull_local(cfg: dict, hostname: str) -> None:
    root = Path(cfg.get("root", "~/workspace")).expanduser()
    matched = core_repos.resolve_repos(hostname, cfg)

    if not matched:
        ui.info(f"No repos defined for host: {hostname}")
        return

    for name, url in matched.items():
        core_repos.sync_repo(root, name, url)


def _pull_remote(target: host.DeployTarget) -> None:
    ssh_dest = f"{target.user}@{target.ssh_host}"
    remote_cmd = f"{TECTONIC_PREFIX} repos"
    try:
        process.run_interactive(["ssh", "-t", ssh_dest, remote_cmd])
        ui.ok(f"{target.name} done")
    except Exception as e:
        ui.error(f"{target.name} failed: {e}")


def repos(
    hostname: str = typer.Argument(None, help="Target host (default: all)"),
    list_repos: Annotated[
        bool,
        typer.Option("--list", "-l", help="List repos for target host"),
    ] = False,
    status: Annotated[
        bool,
        typer.Option("--status", "-s", help="Show repo status"),
    ] = False,
) -> None:
    """Clone and pull repos declared for a host."""
    cfg = _load_repos_config()
    local_hostname = host.get_hostname()
    root = Path(cfg.get("root", "~/workspace")).expanduser()

    if list_repos or status:
        target_hostname = hostname or local_hostname
        matched = core_repos.resolve_repos(target_hostname, cfg)
        if not matched:
            ui.info(f"No repos defined for host: {target_hostname}")
            return
        if list_repos:
            for name, url in matched.items():
                ui.console.print(f"  [bold]{name}[/bold]  [dim]{url}[/dim]")
        elif status:
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

    hosts_config = host.load_hosts(config.HOSTS_FILE)
    targets = host.resolve_deploy_targets(hosts_config)

    if hostname:
        if hostname == local_hostname:
            pull_local(cfg, local_hostname)
            return
        targets = [t for t in targets if t.name == hostname]
        if not targets:
            ui.error(f"Host '{hostname}' is not a valid target")
            raise typer.Exit(code=1)
        for target in targets:
            ui.step(f"{target.name}")
            _pull_remote(target)
        return

    ui.step(local_hostname)
    pull_local(cfg, local_hostname)

    for target in targets:
        ui.step(f"{target.name}")
        _pull_remote(target)
