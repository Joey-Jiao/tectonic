import os
import shutil
from pathlib import Path

from tectonic import config
from tectonic.core import distro, process, ui


def install_zsh() -> None:
    if process.is_installed("zsh"):
        ui.info("zsh already installed")
        return

    d = distro.detect()
    distro.pkg_install(["zsh"])


def install_starship() -> None:
    if process.is_installed("starship"):
        ui.info("starship already installed")
        return

    d = distro.detect()
    if d.pkg_mgr == "brew":
        distro.pkg_install(["starship"])
    else:
        ui.step("Installing starship")
        url = config.configs.get("urls.starship")
        process.run_shell(f"curl -fsSL {url} | sh -s -- -y")

    ui.ok("starship installed")


def set_default_shell() -> None:
    zsh_path = shutil.which("zsh")
    if zsh_path is None:
        ui.error("zsh not found in PATH")
        return

    current_shell = os.environ.get("SHELL", "")
    if current_shell == zsh_path:
        ui.info("Default shell is already zsh")
        return

    ui.step("Setting default shell to zsh")

    if distro.is_macos():
        process.run(["chsh", "-s", zsh_path])
    else:
        shells = Path("/etc/shells").read_text()
        if zsh_path not in shells:
            process.run_shell(f"echo '{zsh_path}' | sudo tee -a /etc/shells")
        user = os.environ.get("USER", "")
        process.run(["sudo", "chsh", "-s", zsh_path, user])

    ui.ok("Default shell set to zsh (re-login required)")


def run() -> None:
    ui.section("Shell Environment")

    install_zsh()
    install_starship()
    set_default_shell()

    ui.ok("Shell environment configured")
