from typing import Annotated

import typer

from tectonic import config
from tectonic.cli import apply, deploy, services, sync
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
app.add_typer(services.app, name="services", help="Inspect host services")

app.command(name="sync")(sync.sync)

_extra_args = {"allow_extra_args": True, "allow_interspersed_args": False}
app.command(name="deploy", context_settings=_extra_args)(deploy.deploy)
app.command(name="broadcast", context_settings=_extra_args)(deploy.broadcast)
