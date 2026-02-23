import typer
import yaml

from tectonic import config
from tectonic.core import host, service, ui

app = typer.Typer()


def _load_services() -> dict[str, service.ServiceDef]:
    hostname = host.get_hostname()
    with config.SERVICES_FILE.open() as f:
        data = yaml.safe_load(f) or {}
    matched = host.resolve_services(hostname, data)
    return {name: service.ServiceDef.from_yaml(name, defn) for name, defn in matched.items()}


@app.command(name="status")
def status() -> None:
    """List service status for current host."""
    services = _load_services()
    if not services:
        hostname = host.get_hostname()
        ui.info(f"No services defined for host: {hostname}")
        return

    for svc in services.values():
        installed, running = service.service_status(svc)
        if running:
            state = "[green]running[/green]"
        elif installed:
            state = "[yellow]stopped[/yellow]"
        else:
            state = "[dim]not installed[/dim]"
        ui.console.print(f"  {svc.name}: {state}")


@app.command(name="load")
def load(name: str = typer.Argument(help="Service name to load")) -> None:
    """Install and load a single service."""
    services = _load_services()
    if name not in services:
        ui.error(f"Service '{name}' not found for this host")
        raise typer.Exit(code=1)

    svc = services[name]
    service.install_service(svc)
    service.load_service(svc)


@app.command(name="unload")
def unload(name: str = typer.Argument(help="Service name to unload")) -> None:
    """Unload and remove a single service."""
    services = _load_services()
    if name not in services:
        ui.error(f"Service '{name}' not found for this host")
        raise typer.Exit(code=1)

    service.unload_service(services[name])


@app.callback(invoke_without_command=True)
def default(ctx: typer.Context) -> None:
    """Manage host services. Defaults to deploying all services for current host."""
    if ctx.invoked_subcommand is not None:
        return

    hostname = host.get_hostname()
    services = _load_services()

    if not services:
        ui.info(f"No services defined for host: {hostname}")
        return

    ui.section(f"Services: {hostname}")
    for svc in services.values():
        updated = service.install_service(svc)
        if updated:
            installed, running = service.service_status(svc)
            if installed and not running:
                service.load_service(svc)
        else:
            ui.info(f"Service '{svc.name}' unchanged, skipping reload")

    ui.ok("All services deployed")
