import os
import plistlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tectonic import config
from tectonic.core import distro, fs, process, ui


@dataclass
class ServiceDef:
    name: str
    program: str
    args: list[str] = field(default_factory=list)
    working_directory: str | None = None
    env: dict[str, str] = field(default_factory=dict)
    keep_alive: bool = False
    run_at_load: bool = True
    interval: int | None = None

    @classmethod
    def from_yaml(cls, name: str, data: dict[str, Any]) -> "ServiceDef":
        return cls(
            name=name,
            program=data["program"],
            args=data.get("args", []),
            working_directory=data.get("working_directory"),
            env=data.get("env", {}),
            keep_alive=data.get("keep_alive", False),
            run_at_load=data.get("run_at_load", True),
            interval=data.get("interval"),
        )

    @property
    def label(self) -> str:
        return f"dev.joeyjiao.{self.name}"

    @property
    def plist_path(self) -> Path:
        return config.DIR_LAUNCHAGENTS / f"{self.label}.plist"

    @property
    def unit_path(self) -> Path:
        return config.DIR_SYSTEMD_USER / f"{self.label}.service"

    @property
    def service_path(self) -> Path:
        if distro.is_macos():
            return self.plist_path
        return self.unit_path


def _generate_plist(svc: ServiceDef) -> bytes:
    plist: dict[str, Any] = {
        "Label": svc.label,
        "ProgramArguments": [svc.program, *svc.args],
        "RunAtLoad": svc.run_at_load,
    }
    if svc.working_directory:
        plist["WorkingDirectory"] = str(Path(svc.working_directory).expanduser())
    if svc.env:
        plist["EnvironmentVariables"] = svc.env
    if svc.keep_alive:
        plist["KeepAlive"] = True
    if svc.interval is not None:
        plist["StartInterval"] = svc.interval
    plist["StandardOutPath"] = str(Path.home() / "Library" / "Logs" / f"{svc.label}.log")
    plist["StandardErrorPath"] = str(Path.home() / "Library" / "Logs" / f"{svc.label}.err.log")
    return plistlib.dumps(plist)


def _generate_unit(svc: ServiceDef) -> str:
    lines = ["[Unit]", f"Description=tectonic service: {svc.name}", ""]
    lines.append("[Service]")
    lines.append("Type=simple")
    exec_start = svc.program
    if svc.args:
        exec_start += " " + " ".join(svc.args)
    lines.append(f"ExecStart={exec_start}")
    if svc.working_directory:
        lines.append(f"WorkingDirectory={Path(svc.working_directory).expanduser()}")
    for key, val in svc.env.items():
        lines.append(f"Environment={key}={val}")
    if svc.keep_alive:
        lines.append("Restart=always")
    lines.append("")
    lines.append("[Install]")
    lines.append("WantedBy=default.target")
    lines.append("")
    return "\n".join(lines)


def install_service(svc: ServiceDef) -> bool:
    path = svc.service_path
    if distro.is_macos():
        content = _generate_plist(svc)
        if path.exists() and path.read_bytes() == content:
            ui.info(f"Service already up to date: {svc.name}")
            return False
        fs.ensure_dir(path.parent)
        path.write_bytes(content)
    else:
        content_str = _generate_unit(svc)
        if path.exists() and path.read_text() == content_str:
            ui.info(f"Service already up to date: {svc.name}")
            return False
        fs.ensure_dir(path.parent)
        path.write_text(content_str)
    ui.ok(f"Installed service file: {path}")
    return True


def load_service(svc: ServiceDef) -> None:
    path = svc.service_path
    if not path.exists():
        install_service(svc)
    if distro.is_macos():
        uid = os.getuid()
        process.run(["launchctl", "bootstrap", f"gui/{uid}", str(path)])
    else:
        process.run(["systemctl", "--user", "enable", "--now", svc.label])
    ui.ok(f"Loaded service: {svc.name}")


def unload_service(svc: ServiceDef) -> None:
    path = svc.service_path
    if distro.is_macos():
        uid = os.getuid()
        process.run(["launchctl", "bootout", f"gui/{uid}/{svc.label}"], check=False)
    else:
        process.run(["systemctl", "--user", "disable", "--now", svc.label], check=False)
    if path.exists():
        path.unlink()
        ui.ok(f"Removed service file: {path}")
    ui.ok(f"Unloaded service: {svc.name}")


def service_status(svc: ServiceDef) -> tuple[bool, bool]:
    installed = svc.service_path.exists()
    running = False
    if not installed:
        return installed, running
    if distro.is_macos():
        uid = os.getuid()
        result = process.run(
            ["launchctl", "print", f"gui/{uid}/{svc.label}"],
            check=False, capture=True,
        )
        running = result.returncode == 0
    else:
        running = process.run_quiet(
            ["systemctl", "--user", "is-active", "--quiet", svc.label],
        )
    return installed, running
