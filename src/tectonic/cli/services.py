import typer

from tectonic import config
from tectonic.core import host, services as core_services, ui

app = typer.Typer()


def _load_services() -> dict[str, core_services.ServiceDef]:
    hostname = host.get_hostname()
    matched = host.resolve_services(hostname, config.configs)
    return {name: core_services.ServiceDef.from_yaml(name, defn) for name, defn in matched.items()}


def deploy() -> None:
    """Deploy all services for current host."""
    hostname = host.get_hostname()

    ui.section("Services")

    matched = host.resolve_services(hostname, config.configs)

    for name, defn in matched.items():
        svc = core_services.ServiceDef.from_yaml(name, defn)
        core_services.install_service(svc)
        if svc.type == "daemon":
            installed, running = core_services.service_status(svc)
            if installed and running:
                core_services.restart_service(svc)
            elif installed:
                core_services.load_service(svc)

    stale = core_services.find_stale_services(set(matched.keys()))
    for svc in stale:
        ui.info(f"Removing stale service: {svc.name}")
        core_services.unload_service(svc)

    ui.ok("Services deployed")


@app.command(name="list")
def list_services() -> None:
    """List all services defined for current host."""
    loaded = _load_services()
    if not loaded:
        ui.info(f"No services defined for host: {host.get_hostname()}")
        return

    for svc in loaded.values():
        ui.console.print(f"  [bold]{svc.name}[/bold]  [dim]{svc.type}[/dim]")
        if svc.type == "daemon":
            cmd = svc.program
            if svc.args:
                cmd += " " + " ".join(svc.args)
            ui.console.print(f"    exec: {cmd}")
            ui.console.print(f"    path: {svc.service_path}")
        else:
            ui.console.print(f"    exec: {svc.exec_cmd}")
            ui.console.print(f"    path: {svc.bin_path}")


@app.command(name="status")
def status() -> None:
    """Show runtime status of services for current host."""
    loaded = _load_services()
    if not loaded:
        ui.info(f"No services defined for host: {host.get_hostname()}")
        return

    for svc in loaded.values():
        installed, running = core_services.service_status(svc)
        if svc.type == "command":
            state = "[green]installed[/green]" if installed else "[dim]not installed[/dim]"
        elif running:
            state = "[green]running[/green]"
        elif installed:
            state = "[yellow]stopped[/yellow]"
        else:
            state = "[dim]not installed[/dim]"
        ui.console.print(f"  {svc.name} ({svc.type}): {state}")


@app.callback(invoke_without_command=True)
def default(ctx: typer.Context) -> None:
    """Deploy and inspect host services."""
    if ctx.invoked_subcommand is not None:
        return
    deploy()
