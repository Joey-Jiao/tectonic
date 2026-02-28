from collections.abc import Callable

from tectonic.modules import base, shell, shell_hpc, syncthing
from tectonic.modules.apps import docker
from tectonic.modules.dev import c, node, python

MODULES: dict[str, Callable[[], None]] = {
    "base": base.run,
    "shell": shell.run,
    "shell-hpc": shell_hpc.run,
    "syncthing": syncthing.run,
    "dev-c": c.run,
    "dev-python": python.run,
    "dev-node": node.run,
    "apps-docker": docker.run,
}


def run_module(name: str) -> None:
    if name not in MODULES:
        raise ValueError(f"Unknown module: {name}")
    MODULES[name]()


def list_modules() -> list[str]:
    return list(MODULES.keys())
