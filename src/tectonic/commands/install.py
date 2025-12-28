import typer

from tectonic import modules
from tectonic.core import distro, process, ui

app = typer.Typer(no_args_is_help=True)


def activate_sudo() -> None:
    """Prompt for sudo password upfront to cache credentials."""
    ui.step("Requesting sudo access")
    process.run_interactive(["sudo", "-v"])


@app.command()
def list() -> None:
    """List available modules."""
    ui.info("Available modules:")
    for name in modules.list_modules():
        ui.console.print(f"  - {name}")


@app.command(name="all")
def install_all() -> None:
    """Install all modules."""
    ui.section("Linux Setup")
    activate_sudo()
    distro.detect()

    for name in modules.list_modules():
        modules.run_module(name)

    ui.section("Setup Complete")
    ui.ok("All modules have been installed")
    ui.info("You may need to re-login for some changes to take effect")
