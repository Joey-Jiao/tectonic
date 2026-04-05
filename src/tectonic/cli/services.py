import typer
import yaml

from tectonic import config
from tectonic.core import host, services, ui

app = typer.Typer()


def _load_services() -> dict[str, services.ServiceDef]:
    hostname = host.get_hostname()
    with config.SERVICES_FILE.open() as f:
        data = yaml.safe_load(f) or {}
    matched = host.resolve_services(hostname, data)
    return {name: services.ServiceDef.from_yaml(name, defn) for name, defn in matched.items()}


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
        installed, running = services.service_status(svc)
        if svc.type == "command":
            state = "[green]installed[/green]" if installed else "[dim]not installed[/dim]"
        elif running:
            state = "[green]running[/green]"
        elif installed:
            state = "[yellow]stopped[/yellow]"
        else:
            state = "[dim]not installed[/dim]"
        ui.console.print(f"  {svc.name} ({svc.type}): {state}")


@app.command(name="load")
def load(name: str = typer.Argument(help="Service name to load")) -> None:
    """Install and load a single service."""
    loaded = _load_services()
    if name not in loaded:
        ui.error(f"Service '{name}' not found for this host")
        raise typer.Exit(code=1)

    svc = loaded[name]
    services.install_service(svc)
    services.load_service(svc)


@app.command(name="unload")
def unload(name: str = typer.Argument(help="Service name to unload")) -> None:
    """Unload and remove a single service."""
    loaded = _load_services()
    if name not in loaded:
        ui.error(f"Service '{name}' not found for this host")
        raise typer.Exit(code=1)

    services.unload_service(loaded[name])


@app.callback(invoke_without_command=True)
def default(ctx: typer.Context) -> None:
    """Manage host services. Defaults to deploying all services for current host."""
    if ctx.invoked_subcommand is not None:
        return

    hostname = host.get_hostname()
    loaded = _load_services()

    if not loaded:
        ui.info(f"No services defined for host: {hostname}")
        return

    ui.section(f"Services: {hostname}")
    for svc in loaded.values():
        updated = services.install_service(svc)
        if updated:
            installed, running = services.service_status(svc)
            if svc.type == "daemon" and installed and not running:
                services.load_service(svc)
        else:
            ui.info(f"Service '{svc.name}' unchanged, skipping")

    ui.ok("All services deployed")
