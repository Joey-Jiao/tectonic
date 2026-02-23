from tectonic import config
from tectonic.core import distro, ui


def run() -> None:
    ui.section("Base System Packages")

    d = distro.detect()
    packages = config.configs.get(f"packages.base.{d.pkg_mgr}", [])

    if not packages:
        ui.warn(f"No base packages defined for {d.pkg_mgr}")
        return

    distro.pkg_update()
    distro.pkg_install(packages)

    ui.ok("Base packages installed")
