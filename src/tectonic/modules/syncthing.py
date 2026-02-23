from tectonic import config
from tectonic.core import distro, process, ui


def _start_service() -> None:
    d = distro.detect()

    if d.pkg_mgr == "brew":
        process.run(["brew", "services", "start", "syncthing"])
    else:
        process.run(["sudo", "systemctl", "enable", "--now", "syncthing@" + process.run(
            ["whoami"], capture=True,
        ).stdout.strip()])


def run() -> None:
    ui.section("Syncthing")

    d = distro.detect()
    packages = config.configs.get(f"packages.syncthing.{d.pkg_mgr}", [])

    if not packages:
        ui.warn(f"No Syncthing packages defined for {d.pkg_mgr}")
        return

    distro.pkg_install(packages)
    _start_service()

    ui.ok("Syncthing installed and running")
