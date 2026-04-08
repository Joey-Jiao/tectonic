from enum import Enum
from pathlib import Path
from typing import Annotated

import typer
import yaml

from tectonic import config, modules
from tectonic.core import distro, host, process, repos, services, ui


class Step(str, Enum):
    packages = "packages"
    repos = "repos"
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


def _run_repos(hostname: str) -> None:
    ui.section("Repos")

    with config.PULL_FILE.open() as f:
        cfg = yaml.safe_load(f) or {}

    root = Path(cfg.get("root", "~/workspace")).expanduser()
    matched = repos.resolve_repos(hostname, cfg)

    if not matched:
        ui.info("No repos defined for this host")
        return

    for name, url in matched.items():
        repos.sync_repo(root, name, url)


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

    for name, defn in matched.items():
        svc = services.ServiceDef.from_yaml(name, defn)
        updated = services.install_service(svc)
        if updated:
            installed, running = services.service_status(svc)
            if svc.type == "daemon" and installed and not running:
                services.load_service(svc)

    stale = services.find_stale_services(set(matched.keys()))
    for svc in stale:
        ui.info(f"Removing stale service: {svc.name}")
        services.unload_service(svc)

    ui.ok("Services deployed")


def apply(
    step: Annotated[
        Step | None,
        typer.Option("--step", "-s", help="Run only a specific step"),
    ] = None,
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

    steps = [step] if step else [Step.packages, Step.repos, Step.dotfiles, Step.services]

    if Step.packages in steps:
        _run_packages(hostname)
    if Step.repos in steps:
        _run_repos(hostname)
    if Step.dotfiles in steps:
        _run_dotfiles()
    if Step.services in steps:
        _run_services(hostname)

    ui.section("Apply Complete")
    ui.ok("Host converged to declared state")
