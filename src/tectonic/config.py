import platform
from pathlib import Path

from tectonic.base import ConfigService

TECTONIC_ROOT = Path(__file__).parent.parent.parent
CONFIGS_DIR = TECTONIC_ROOT / "configs"
HOSTS_FILE = CONFIGS_DIR / "hosts.yml"

XDG_CONFIG_HOME = Path.home() / ".config"
XDG_DATA_HOME = Path.home() / ".local" / "share"
XDG_CACHE_HOME = Path.home() / ".cache"

LOG_FILE = TECTONIC_ROOT / "logs" / "tectonic.log"

DIR_ZSH_CONFIG = XDG_CONFIG_HOME / "zsh"
DIR_ZSH_DATA = XDG_DATA_HOME / "zsh"
DIR_ZSH_CACHE = XDG_CACHE_HOME / "zsh"
DIR_ZSH_PLUGINS = DIR_ZSH_DATA / "plugins"

DIR_LOCAL = Path.home() / ".local"
DIR_LAUNCHAGENTS = Path.home() / "Library" / "LaunchAgents"
DIR_SYSTEMD_USER = XDG_CONFIG_HOME / "systemd" / "user"

SERVICES_FILE = CONFIGS_DIR / "services.yaml"

ARCH = platform.machine()
SYSTEM = platform.system()

AVAILABLE_MODULES = [
    "base", "shell", "shell-hpc", "syncthing",
    "dev-c", "dev-python", "dev-node", "apps-docker",
]

configs = ConfigService(config_dir=CONFIGS_DIR)
