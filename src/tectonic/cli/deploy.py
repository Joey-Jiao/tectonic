from typing import Annotated

import typer

from tectonic import config
from tectonic.core import host, process, ui

TECTONIC_PREFIX = "tectonic repos; tectonic"


def _run_on_targets(
    targets: list[host.DeployTarget],
    args: list[str],
    dry_run: bool,
) -> None:
    if not args:
        ui.error("No command specified")
        raise typer.Exit(code=1)

    if not targets:
        ui.info("No deploy targets found")
        return

    remote_cmd = f"{TECTONIC_PREFIX} {' '.join(args)}"

    for target in targets:
        ssh_dest = f"{target.user}@{target.ssh_host}"

        if dry_run:
            ui.step(f"[dry-run] {target.name}: ssh {ssh_dest} \"{remote_cmd}\"")
            continue

        ui.step(f"{target.name}")
        try:
            process.run_interactive(["ssh", "-t", ssh_dest, remote_cmd])
            ui.ok(f"{target.name} done")
        except Exception as e:
            ui.error(f"{target.name} failed: {e}")


def deploy(
    ctx: typer.Context,
    hostname: str = typer.Argument(help="Target host name"),
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show commands without executing"),
    ] = False,
) -> None:
    """Execute a tectonic command on a remote host via SSH."""
    hosts_config = host.load_hosts(config.configs)
    targets = host.resolve_deploy_targets(hosts_config)

    targets = [t for t in targets if t.name == hostname]
    if not targets:
        ui.error(f"Host '{hostname}' is not a valid deploy target")
        raise typer.Exit(code=1)

    ui.section(f"Deploy: {hostname}")
    _run_on_targets(targets, ctx.args, dry_run)


def broadcast(
    ctx: typer.Context,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show commands without executing"),
    ] = False,
) -> None:
    """Execute a tectonic command on all reachable remote hosts."""
    hosts_config = host.load_hosts(config.configs)
    targets = host.resolve_deploy_targets(hosts_config)

    ui.section("Broadcast")
    _run_on_targets(targets, ctx.args, dry_run)
