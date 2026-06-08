from typing import Annotated

import typer

from tectonic import config
from tectonic.cli import apply, dotfiles, packages, tools
from tectonic.core import ui

app = typer.Typer(
    name="tectonic",
    help="Environment Setup CLI Tool",
    no_args_is_help=True,
)


@app.callback()
def main(
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed output"),
    ] = False,
) -> None:
    ui.init(config.LOG_FILE, verbose=verbose)


app.command(name="apply")(apply.apply)
app.command(name="packages")(packages.packages)
app.command(name="dotfiles")(dotfiles.dotfiles)
app.command(name="tools")(tools.tools)
