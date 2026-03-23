import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class DeployTarget:
    name: str
    user: str
    ssh_host: str


def get_hostname() -> str:
    return socket.gethostname().split(".")[0].lower()


def load_hosts(path: Path) -> dict[str, Any]:
    with path.open() as f:
        data: dict[str, Any] = yaml.safe_load(f)
    return data


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
    raise KeyError(f"Host '{hostname}' not found in hosts.yml")


def resolve_services(hostname: str, services_config: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, definition in services_config.get("services", {}).items():
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
