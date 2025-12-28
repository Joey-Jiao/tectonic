import platform
from pathlib import Path

TECTONIC_ROOT = Path(__file__).parent.parent.parent
DOTFILES_DIR = TECTONIC_ROOT / "dotfiles"

XDG_CONFIG_HOME = Path.home() / ".config"
XDG_DATA_HOME = Path.home() / ".local" / "share"
XDG_CACHE_HOME = Path.home() / ".cache"

LOG_FILE = TECTONIC_ROOT / "logs" / "tectonic.log"

DIR_ZSH_CONFIG = XDG_CONFIG_HOME / "zsh"
DIR_ZSH_DATA = XDG_DATA_HOME / "zsh"
DIR_ZSH_CACHE = XDG_CACHE_HOME / "zsh"
DIR_ZSH_PLUGINS = DIR_ZSH_DATA / "plugins"

DIR_LOCAL = Path.home() / ".local"
DIR_MINIFORGE = DIR_LOCAL / "miniforge"
DIR_NVM = DIR_LOCAL / "nvm"

ARCH = platform.machine()
SYSTEM = platform.system()

ARCH_CONDA = {
    "x86_64": "x86_64",
    "aarch64": "aarch64",
    "arm64": "arm64",
}.get(ARCH, ARCH)

OS_CONDA = "MacOSX" if SYSTEM == "Darwin" else "Linux"

URL_NVM_INSTALL = "https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh"
URL_MINIFORGE = f"https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-{OS_CONDA}-{ARCH_CONDA}.sh"
URL_STARSHIP_INSTALL = "https://starship.rs/install.sh"

PKGS_BASE: dict[str, list[str]] = {
    "apt": ["curl", "wget", "git", "vim", "neovim", "htop", "tree", "unzip"],
    "pacman": ["curl", "wget", "git", "vim", "neovim", "htop", "tree", "unzip"],
    "dnf": ["curl", "wget", "git", "vim", "neovim", "htop", "tree", "unzip"],
    "brew": ["curl", "wget", "git", "vim", "neovim", "htop", "tree", "unzip"],
}

PKGS_SHELL: dict[str, list[str]] = {
    "apt": ["zsh"],
    "pacman": ["zsh", "starship"],
    "dnf": ["zsh"],
    "brew": ["zsh", "starship"],
}

PKGS_DEV_C: dict[str, list[str]] = {
    "apt": [
        "build-essential", "cmake", "gdb", "autoconf",
        "automake", "libtool", "bison", "ninja-build",
    ],
    "pacman": [
        "base-devel", "cmake", "gdb", "autoconf",
        "automake", "libtool", "bison", "ninja",
    ],
    "dnf": [
        "gcc", "gcc-c++", "make", "cmake", "gdb",
        "autoconf", "automake", "libtool", "bison", "ninja-build",
    ],
    "brew": [
        "gcc", "cmake", "gdb", "autoconf",
        "automake", "libtool", "bison", "ninja",
    ],
}

PKGS_APPS: dict[str, list[str]] = {
    "apt": ["docker.io", "docker-compose"],
    "pacman": ["docker", "docker-compose"],
    "dnf": ["docker", "docker-compose"],
    "brew": [],
}

AVAILABLE_MODULES = ["base", "shell", "dev-c", "dev-python", "dev-node", "apps-docker"]
