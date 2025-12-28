from tectonic import config
from tectonic.core import distro, process, ui


def run() -> None:
    ui.section("C/C++ Development Environment")

    d = distro.detect()
    packages = config.PKGS_DEV_C.get(d.pkg_mgr, [])

    if not packages:
        ui.warn(f"No C/C++ packages defined for {d.pkg_mgr}")
        return

    distro.pkg_install(packages)

    if process.is_installed("gcc"):
        result = process.run(["gcc", "--version"], capture=True)
        ui.info(f"GCC: {result.stdout.splitlines()[0]}")

    if process.is_installed("cmake"):
        result = process.run(["cmake", "--version"], capture=True)
        ui.info(f"CMake: {result.stdout.splitlines()[0]}")

    ui.ok("C/C++ development environment installed")
