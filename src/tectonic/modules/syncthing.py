from pathlib import Path

from tectonic import config
from tectonic.core import distro, fs, process, ui

SYNCIGNORE_SRC = config.CONFIGS_DIR / "syncignore"
SYNCIGNORE_DST = Path.home() / "workspace" / ".syncignore"


def _start_service() -> None:
    d = distro.detect()

    if d.pkg_mgr == "brew":
        process.run(["brew", "services", "start", "syncthing"])
    else:
        process.run(["sudo", "systemctl", "enable", "--now", "syncthing@" + process.run(
            ["whoami"], capture=True,
        ).stdout.strip()])


def _deploy_syncignore() -> None:
    if not SYNCIGNORE_DST.parent.is_dir():
        return
    fs.copy(SYNCIGNORE_SRC, SYNCIGNORE_DST, do_backup=False)


def run() -> None:
    ui.section("Syncthing")

    d = distro.detect()
    packages = config.configs.get(f"packages.syncthing.{d.pkg_mgr}", [])

    if not packages:
        ui.warn(f"No Syncthing packages defined for {d.pkg_mgr}")
        return

    distro.pkg_install(packages)
    _start_service()
    _deploy_syncignore()

    ui.ok("Syncthing installed and running")
