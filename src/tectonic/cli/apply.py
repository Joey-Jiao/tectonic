import typer

from tectonic import config
from tectonic.cli import dotfiles as dotfiles_cmd
from tectonic.cli import packages as packages_cmd
from tectonic.cli import repos as repos_cmd
from tectonic.cli import services as services_cmd
from tectonic.core import host, ui


def apply() -> None:
    """Converge current host to declared state."""
    hostname = host.get_hostname()

    try:
        hosts_config = host.load_hosts(config.configs)
        host.find_host(hostname, hosts_config)
    except (FileNotFoundError, KeyError) as e:
        ui.error(f"Host resolution failed: {e}")
        raise typer.Exit(code=1)

    ui.section(f"Apply: {hostname}")

    packages_cmd.packages()
    repos_cmd.repos()
    dotfiles_cmd.dotfiles()
    services_cmd.deploy()

    ui.section("Apply Complete")
    ui.ok("Host converged to declared state")
