import getpass

from tectonic import config
from tectonic.core import distro, process, ui


def install_linux() -> None:
    d = distro.detect()
    packages = config.configs.get(f"packages.apps.{d.pkg_mgr}", [])

    if not packages:
        ui.warn(f"No app packages defined for {d.pkg_mgr}")
        return

    distro.pkg_install(packages)

    ui.step("Adding user to docker group")
    user = getpass.getuser()
    process.run(["sudo", "usermod", "-aG", "docker", user])

    ui.step("Enabling docker service")
    process.run(["sudo", "systemctl", "enable", "docker"])
    process.run(["sudo", "systemctl", "start", "docker"])

    ui.ok("Docker installed (re-login required for group permissions)")


def install_macos() -> None:
    ui.step("Installing Docker Desktop via Homebrew")
    process.run(["brew", "install", "--cask", "docker"])
    ui.ok("Docker Desktop installed (open Docker.app to start)")


def run() -> None:
    ui.section("Docker")

    if process.is_installed("docker"):
        ui.info("Docker already installed")
        return

    if distro.is_macos():
        install_macos()
    else:
        install_linux()
