from enum import Enum
from typing import Annotated

import typer
import yaml

from tectonic import config, modules
from tectonic.core import distro, host, process, services, ui


class Step(str, Enum):
    packages = "packages"
    dotfiles = "dotfiles"
    services = "services"


def _run_packages(hostname: str) -> None:
    ui.section("Packages")

    hosts_config = host.load_hosts(config.HOSTS_FILE)
    _, host_entry = host.find_host(hostname, hosts_config)
    resolved = host.resolve_modules(hostname, hosts_config)
    is_hpc = "hpc" in host_entry

    ui.info(f"Modules: {', '.join(resolved)}")

    if not is_hpc:
        ui.step("Requesting sudo access")
        process.run_interactive(["sudo", "-v"])

    distro.detect()
    for name in resolved:
        modules.run_module(name)


def _run_dotfiles() -> None:
    ui.section("Dotfiles")

    if not process.is_installed("chezmoi"):
        ui.info("chezmoi not found, skipping dotfiles")
        return

    source = str(config.CHEZMOI_SOURCE)
    chezmoi_config = config.XDG_CONFIG_HOME / "chezmoi" / "chezmoi.toml"

    if chezmoi_config.exists():
        process.run_interactive(["chezmoi", "apply", "--source", source, "--force"])
    else:
        process.run_interactive(["chezmoi", "init", "--source", source, "--apply"])

    ui.ok("Dotfiles applied")


def _run_services(hostname: str) -> None:
    ui.section("Services")

    with config.SERVICES_FILE.open() as f:
        data = yaml.safe_load(f) or {}

    matched = host.resolve_services(hostname, data)
    if not matched:
        ui.info("No services defined for this host")
        return

    for name, defn in matched.items():
        svc = services.ServiceDef.from_yaml(name, defn)
        updated = services.install_service(svc)
        if updated:
            installed, running = services.service_status(svc)
            if svc.type == "daemon" and installed and not running:
                services.load_service(svc)

    ui.ok("Services deployed")


def _pull_repo() -> None:
    ui.section("Pull")
    result = process.run(["git", "pull", "--ff-only"], cwd=config.TECTONIC_ROOT, check=False)
    if result.returncode == 0:
        ui.ok("Repository updated")
    else:
        ui.info("Pull skipped (local changes or no remote), continuing with current state")


def apply(
    step: Annotated[
        Step | None,
        typer.Option("--step", "-s", help="Run only a specific step"),
    ] = None,
    no_pull: Annotated[
        bool,
        typer.Option("--no-pull", help="Skip git pull"),
    ] = False,
) -> None:
    """Converge current host to declared state."""
    hostname = host.get_hostname()

    try:
        host.load_hosts(config.HOSTS_FILE)
        host.find_host(hostname, host.load_hosts(config.HOSTS_FILE))
    except (FileNotFoundError, KeyError) as e:
        ui.error(f"Host resolution failed: {e}")
        raise typer.Exit(code=1)

    ui.section(f"Apply: {hostname}")

    if not no_pull:
        _pull_repo()

    steps = [step] if step else [Step.packages, Step.dotfiles, Step.services]

    if Step.packages in steps:
        _run_packages(hostname)
    if Step.dotfiles in steps:
        _run_dotfiles()
    if Step.services in steps:
        _run_services(hostname)

    ui.section("Apply Complete")
    ui.ok("Host converged to declared state")
