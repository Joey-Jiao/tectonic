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
