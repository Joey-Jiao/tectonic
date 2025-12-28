from typing import Annotated

import typer

from tectonic import config
from tectonic.commands import dotfiles, install, plugins
from tectonic.core import ui

app = typer.Typer(
    name="tectonic",
    help="Linux Setup CLI Tool",
    no_args_is_help=True,
)


@app.callback()
def main(
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed output"),
    ] = False,
) -> None:
    """Linux Setup CLI Tool."""
    ui.init(config.LOG_FILE, verbose=verbose)


app.add_typer(install.app, name="install", help="Install system modules")
app.add_typer(plugins.app, name="plugins", help="Manage zsh plugins")
app.add_typer(dotfiles.app, name="dotfiles", help="Manage dotfiles")

if __name__ == "__main__":
    app()
