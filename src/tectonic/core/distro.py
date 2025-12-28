import platform
from dataclasses import dataclass
from pathlib import Path

from tectonic.core import process, ui


@dataclass
class Distro:
    id: str
    id_like: str
    version: str
    name: str
    pkg_mgr: str


_distro: Distro | None = None


def _detect_macos() -> Distro:
    version = platform.mac_ver()[0]
    return Distro(
        id="macos",
        id_like="darwin",
        version=version,
        name=f"macOS {version}",
        pkg_mgr="brew",
    )


def _detect_linux() -> Distro:
    os_release = Path("/etc/os-release")
    if not os_release.exists():
        ui.warn("Cannot detect distribution: /etc/os-release not found")
        return Distro(
            id="unknown",
            id_like="",
            version="",
            name="Unknown",
            pkg_mgr="",
        )

    info: dict[str, str] = {}
    for line in os_release.read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            info[key] = value.strip('"')

    distro_id = info.get("ID", "unknown")
    id_like = info.get("ID_LIKE", "")

    pkg_mgr = ""
    if distro_id in ("ubuntu", "debian", "linuxmint", "pop"):
        pkg_mgr = "apt"
    elif distro_id in ("arch", "manjaro", "endeavouros"):
        pkg_mgr = "pacman"
    elif distro_id == "fedora":
        pkg_mgr = "dnf"
    elif distro_id in ("centos", "rhel", "rocky", "almalinux"):
        pkg_mgr = "yum"
    elif "debian" in id_like:
        pkg_mgr = "apt"
    elif "arch" in id_like:
        pkg_mgr = "pacman"
    elif "fedora" in id_like:
        pkg_mgr = "dnf"

    return Distro(
        id=distro_id,
        id_like=id_like,
        version=info.get("VERSION_ID", ""),
        name=info.get("PRETTY_NAME", distro_id),
        pkg_mgr=pkg_mgr,
    )


def detect() -> Distro:
    global _distro
    if _distro is not None:
        return _distro

    if platform.system() == "Darwin":
        _distro = _detect_macos()
    else:
        _distro = _detect_linux()

    ui.info(f"Detected: {_distro.name} (pkg: {_distro.pkg_mgr})")
    return _distro


def pkg_update() -> None:
    d = detect()
    ui.step("Updating package database")

    match d.pkg_mgr:
        case "apt":
            process.run(["sudo", "apt", "update"])
        case "pacman":
            process.run(["sudo", "pacman", "-Sy"])
        case "dnf":
            process.run_quiet(["sudo", "dnf", "check-update"])
        case "yum":
            process.run_quiet(["sudo", "yum", "check-update"])
        case "brew":
            process.run(["brew", "update"])


def pkg_install(packages: list[str]) -> None:
    if not packages:
        return

    d = detect()
    ui.step(f"Installing: {' '.join(packages)}")

    match d.pkg_mgr:
        case "apt":
            process.run(["sudo", "apt", "install", "-y", *packages])
        case "pacman":
            process.run(["sudo", "pacman", "-S", "--noconfirm", "--needed", *packages])
        case "dnf":
            process.run(["sudo", "dnf", "install", "-y", *packages])
        case "yum":
            process.run(["sudo", "yum", "install", "-y", *packages])
        case "brew":
            process.run(["brew", "install", *packages])


def pkg_installed(package: str) -> bool:
    d = detect()

    match d.pkg_mgr:
        case "apt":
            return process.run_quiet(["dpkg", "-l", package])
        case "pacman":
            return process.run_quiet(["pacman", "-Qi", package])
        case "dnf" | "yum":
            return process.run_quiet(["rpm", "-q", package])
        case "brew":
            return process.run_quiet(["brew", "list", package])

    return False


def is_macos() -> bool:
    return platform.system() == "Darwin"
