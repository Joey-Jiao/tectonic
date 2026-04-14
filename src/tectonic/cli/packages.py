from tectonic import config, modules
from tectonic.core import distro, host, process, ui


def packages() -> None:
    """Install packages for current host."""
    hostname = host.get_hostname()
    hosts_config = host.load_hosts(config.configs)
    _, host_entry = host.find_host(hostname, hosts_config)
    resolved = host.resolve_modules(hostname, hosts_config)
    is_hpc = "hpc" in host_entry

    ui.section("Packages")
    ui.info(f"Modules: {', '.join(resolved)}")

    if not is_hpc:
        ui.step("Requesting sudo access")
        process.run_interactive(["sudo", "-v"])

    distro.detect()
    for name in resolved:
        modules.run_module(name)
