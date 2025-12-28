import os
import subprocess
from pathlib import Path

from tectonic import config
from tectonic.core import distro, fs, process, ui


def install_zsh() -> None:
    if process.is_installed("zsh"):
        ui.info("zsh already installed")
        return

    d = distro.detect()
    packages = config.PKGS_SHELL.get(d.pkg_mgr, ["zsh"])
    distro.pkg_install(packages)


def install_starship() -> None:
    if process.is_installed("starship"):
        ui.info("starship already installed")
        return

    d = distro.detect()
    if d.pkg_mgr in ("pacman", "brew"):
        return

    ui.step("Installing starship")
    process.run_shell(f"curl -fsSL {config.URL_STARSHIP_INSTALL} | sh -s -- -y")
    ui.ok("starship installed")


def init_submodules() -> None:
    gitmodules = config.TECTONIC_ROOT / ".gitmodules"
    if not gitmodules.exists():
        return

    test_plugin = config.DOTFILES_DIR / "local" / "share" / "zsh" / "plugins" / "zsh-autosuggestions" / "zsh-autosuggestions.zsh"
    if test_plugin.exists():
        return

    ui.step("Initializing git submodules")
    process.run(
        ["git", "submodule", "update", "--init", "--depth=1"],
        cwd=config.TECTONIC_ROOT,
    )
    ui.ok("Submodules initialized")


def install_plugins() -> None:
    src_dir = config.DOTFILES_DIR / "local" / "share" / "zsh" / "plugins"

    init_submodules()

    if not src_dir.exists():
        ui.error(f"Plugins source directory not found: {src_dir}")
        return

    fs.ensure_dir(config.DIR_ZSH_PLUGINS)

    for plugin_dir in src_dir.iterdir():
        if not plugin_dir.is_dir():
            continue

        name = plugin_dir.name
        dest = config.DIR_ZSH_PLUGINS / name

        if dest.exists():
            ui.info(f"Plugin already installed: {name}")
            continue

        ui.step(f"Installing plugin: {name}")
        fs.copy_dir(plugin_dir, dest)
        ui.ok(f"Plugin installed: {name}")


def setup_dotfiles() -> None:
    ui.step("Setting up zsh dotfiles (XDG)")

    # Ensure target directories exist
    fs.ensure_dir(config.DIR_ZSH_CONFIG / "zshrc.d")
    fs.ensure_dir(config.DIR_ZSH_CACHE)

    # ~/
    fs.copy(
        config.DOTFILES_DIR / "home" / ".zshenv",
        Path.home() / ".zshenv",
    )

    # ~/.config/
    fs.copy_tree(
        config.DOTFILES_DIR / "config",
        config.XDG_CONFIG_HOME,
    )

    ui.ok("Zsh dotfiles configured")


def set_default_shell() -> None:
    zsh_path = subprocess.run(
        ["which", "zsh"],
        capture_output=True,
        text=True,
    ).stdout.strip()

    current_shell = os.environ.get("SHELL", "")
    if current_shell == zsh_path:
        ui.info("Default shell is already zsh")
        return

    ui.step("Setting default shell to zsh")

    if distro.is_macos():
        process.run(["chsh", "-s", zsh_path])
    else:
        shells = open("/etc/shells").read()
        if zsh_path not in shells:
            process.run_shell(f"echo '{zsh_path}' | sudo tee -a /etc/shells")
        user = os.environ.get("USER", "")
        process.run(["sudo", "chsh", "-s", zsh_path, user])

    ui.ok("Default shell set to zsh (re-login required)")


def run() -> None:
    ui.section("Shell Environment (XDG + Starship)")

    install_zsh()
    install_starship()
    install_plugins()
    setup_dotfiles()
    set_default_shell()

    ui.ok("Shell environment configured")
