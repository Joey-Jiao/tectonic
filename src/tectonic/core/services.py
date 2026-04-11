import os
import plistlib
import shutil
import stat
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tectonic import config
from tectonic.core import distro, fs, process, ui

DIR_BIN = Path.home() / ".local" / "bin"


@dataclass
class ServiceDef:
    name: str
    type: str = "daemon"
    program: str = ""
    args: list[str] = field(default_factory=list)
    working_directory: str | None = None
    env: dict[str, str] = field(default_factory=dict)
    keep_alive: bool = True
    run_at_load: bool = True
    interval: int | None = None
    exec_cmd: str = ""

    @classmethod
    def from_yaml(cls, name: str, data: dict[str, Any]) -> "ServiceDef":
        svc_type = data.get("type", "daemon")
        if svc_type == "command":
            return cls(name=name, type="command", exec_cmd=data["exec"])
        return cls(
            name=name,
            type="daemon",
            program=data["program"],
            args=data.get("args", []),
            working_directory=data.get("working_directory"),
            env=data.get("env", {}),
            keep_alive=data.get("keep_alive", True),
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

    @property
    def bin_path(self) -> Path:
        return DIR_BIN / self.name


def _resolve_program(program: str) -> str:
    expanded = str(Path(program).expanduser())
    if os.path.isabs(expanded):
        return expanded
    resolved = shutil.which(program)
    if resolved:
        return resolved
    return program


def _generate_plist(svc: ServiceDef) -> bytes:
    program = _resolve_program(svc.program)
    args = [str(Path(a).expanduser()) if "~" in a else a for a in svc.args]
    plist: dict[str, Any] = {
        "Label": svc.label,
        "ProgramArguments": [program, *args],
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


def _generate_wrapper(svc: ServiceDef) -> str:
    return f"#!/bin/sh\nexec {svc.exec_cmd} \"$@\"\n"


def install_service(svc: ServiceDef) -> bool:
    if svc.type == "command":
        return _install_command(svc)
    return _install_daemon(svc)


def _install_daemon(svc: ServiceDef) -> bool:
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


def _install_command(svc: ServiceDef) -> bool:
    path = svc.bin_path
    content = _generate_wrapper(svc)
    if path.exists() and path.read_text() == content:
        ui.info(f"Command already up to date: {svc.name}")
        return False
    fs.ensure_dir(path.parent)
    path.write_text(content)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    ui.ok(f"Installed command: {path}")
    return True


def load_service(svc: ServiceDef) -> None:
    if svc.type == "command":
        _install_command(svc)
        return
    path = svc.service_path
    if not path.exists():
        _install_daemon(svc)
    if distro.is_macos():
        uid = os.getuid()
        process.run(["launchctl", "bootstrap", f"gui/{uid}", str(path)])
    else:
        process.run(["systemctl", "--user", "enable", "--now", svc.label])
    ui.ok(f"Loaded service: {svc.name}")


def restart_service(svc: ServiceDef) -> None:
    if svc.type == "command":
        return
    if distro.is_macos():
        uid = os.getuid()
        process.run(
            ["launchctl", "kickstart", "-k", f"gui/{uid}/{svc.label}"],
            check=False,
        )
    else:
        process.run(["systemctl", "--user", "restart", svc.label], check=False)
    ui.ok(f"Restarted service: {svc.name}")


def unload_service(svc: ServiceDef) -> None:
    if svc.type == "command":
        path = svc.bin_path
        if path.exists():
            path.unlink()
            ui.ok(f"Removed command: {path}")
        return
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


LABEL_PREFIX = "dev.joeyjiao."


def find_stale_services(active_names: set[str]) -> list[ServiceDef]:
    stale: list[ServiceDef] = []

    if distro.is_macos():
        for path in config.DIR_LAUNCHAGENTS.glob(f"{LABEL_PREFIX}*.plist"):
            name = path.stem.removeprefix(LABEL_PREFIX)
            if name not in active_names:
                stale.append(ServiceDef(name=name, type="daemon"))
    else:
        for path in config.DIR_SYSTEMD_USER.glob(f"{LABEL_PREFIX}*.service"):
            name = path.stem.removeprefix(LABEL_PREFIX)
            if name not in active_names:
                stale.append(ServiceDef(name=name, type="daemon"))

    for path in DIR_BIN.glob("*"):
        if not path.is_file():
            continue
        try:
            content = path.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        if content.startswith("#!/bin/sh\nexec ") and path.name not in active_names:
            stale.append(ServiceDef(name=path.name, type="command"))

    return stale


def service_status(svc: ServiceDef) -> tuple[bool, bool]:
    if svc.type == "command":
        return svc.bin_path.exists(), False
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
