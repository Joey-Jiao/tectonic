import typer

from tectonic import config, modules
from tectonic.core import distro, host, process, ui

app = typer.Typer()


def activate_sudo() -> None:
    ui.step("Requesting sudo access")
    process.run_interactive(["sudo", "-v"])


def _install_modules(names: list[str], skip_sudo: bool = False) -> None:
    if not skip_sudo:
        activate_sudo()
    distro.detect()

    for name in names:
        modules.run_module(name)

    ui.section("Setup Complete")
    ui.ok("All modules have been installed")
    ui.info("You may need to re-login for some changes to take effect")


@app.command(name="list")
def list_modules() -> None:
    """List available modules."""
    ui.info("Available modules:")
    for name in modules.list_modules():
        ui.console.print(f"  - {name}")


@app.command(name="all")
def install_all() -> None:
    """Install all modules."""
    ui.section("Environment Setup")
    _install_modules(modules.list_modules())


@app.command(name="module")
def install_module(
    name: str = typer.Argument(help="Module name to install"),
) -> None:
    """Install a single module by name."""
    if name not in modules.MODULES:
        ui.error(f"Unknown module: {name}")
        ui.info("Available modules:")
        for m in modules.list_modules():
            ui.console.print(f"  - {m}")
        raise typer.Exit(code=1)

    ui.section(f"Installing module: {name}")
    activate_sudo()
    distro.detect()
    modules.run_module(name)
    ui.ok(f"Module '{name}' installed")


@app.callback(invoke_without_command=True)
def default(ctx: typer.Context) -> None:
    """Install system modules. Defaults to host-aware install."""
    if ctx.invoked_subcommand is not None:
        return

    hostname = host.get_hostname()
    try:
        hosts_config = host.load_hosts(config.HOSTS_FILE)
        tectonic_name, host_entry = host.find_host(hostname, hosts_config)
        resolved = host.resolve_modules(hostname, hosts_config)
    except FileNotFoundError:
        ui.error(f"Hosts file not found: {config.HOSTS_FILE}")
        raise typer.Exit(code=1)
    except KeyError as e:
        ui.error(str(e))
        ui.info("Use 'tectonic install all' or 'tectonic install module <name>' instead")
        raise typer.Exit(code=1)

    is_hpc = "hpc" in host_entry

    ui.section(f"Host-aware Setup: {tectonic_name}")
    ui.info(f"Modules: {', '.join(resolved)}")
    _install_modules(resolved, skip_sudo=is_hpc)
