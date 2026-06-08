import socket
from typing import Any

from tectonic.base import ConfigService


def get_hostname() -> str:
    return socket.gethostname().split(".")[0].lower()


def load_hosts(configs: ConfigService) -> dict[str, Any]:
    return {
        "presets": configs.get("hosts.presets", {}),
        "hosts": configs.get("hosts.hosts", {}),
    }


def find_host(hostname: str, hosts_config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    hosts = hosts_config.get("hosts", {})
    if hostname in hosts:
        return hostname, hosts[hostname]
    for name, entry in hosts.items():
        if hostname in entry.get("aliases", []):
            return name, entry
    raise KeyError(f"Host '{hostname}' not found in hosts config")


def resolve_modules(hostname: str, hosts_config: dict[str, Any]) -> list[str]:
    _, host_entry = find_host(hostname, hosts_config)
    presets = hosts_config.get("presets", {})

    preset_name = host_entry.get("preset", "")
    modules = list(presets.get(preset_name, []))

    extra = host_entry.get("extra", [])
    for mod in extra:
        if mod not in modules:
            modules.append(mod)

    return modules
