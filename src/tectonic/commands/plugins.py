import typer

from tectonic import config
from tectonic.core import ui

app = typer.Typer()


@app.callback(invoke_without_command=True)
def list() -> None:
    """List installed zsh plugins."""
    plugins_dir = config.DIR_ZSH_PLUGINS

    if not plugins_dir.exists():
        ui.warn("No plugins installed yet")
        return

    ui.info("Installed plugins:")
    for plugin in plugins_dir.iterdir():
        if plugin.is_dir():
            ui.console.print(f"  - {plugin.name}")
