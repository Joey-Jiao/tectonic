import socket
from dataclasses import dataclass
from typing import Any

from tectonic.base import ConfigService


@dataclass
class DeployTarget:
    name: str
    user: str
    ssh_host: str


def get_hostname() -> str:
    return socket.gethostname().split(".")[0].lower()


def load_hosts(configs: ConfigService) -> dict[str, Any]:
    return {
        "presets": configs.get("hosts.presets", {}),
        "hosts": configs.get("hosts.hosts", {}),
    }


def resolve_deploy_targets(hosts_config: dict[str, Any]) -> list[DeployTarget]:
    current = get_hostname()
    hosts = hosts_config.get("hosts", {})
    targets = []
    for name, entry in hosts.items():
        if name == current:
            continue
        if entry.get("preset") == "hpc":
            continue
        ssh_host = entry.get("ssh_host")
        if not ssh_host:
            continue
        targets.append(DeployTarget(
            name=name,
            user=entry["user"],
            ssh_host=ssh_host,
        ))
    return targets


def find_host(hostname: str, hosts_config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    hosts = hosts_config.get("hosts", {})
    if hostname in hosts:
        return hostname, hosts[hostname]
    for name, entry in hosts.items():
        if hostname in entry.get("aliases", []):
            return name, entry
    raise KeyError(f"Host '{hostname}' not found in hosts config")


def resolve_services(hostname: str, configs: Any) -> dict[str, Any]:
    if isinstance(configs, ConfigService):
        result: dict[str, Any] = {}
        for name in configs.list_files("services"):
            defn = configs.get(f"services.{name}", {})
            if hostname in defn.get("hosts", []):
                result[name] = defn
        return result
    result = {}
    for name, definition in configs.get("services", {}).items():
        if hostname in definition.get("hosts", []):
            result[name] = definition
    return result


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
