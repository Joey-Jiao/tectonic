from tectonic import config
from tectonic.core import distro, process, ui


def run() -> None:
    ui.section("Node.js Development Environment")

    d = distro.detect()
    packages = config.configs.get(f"packages.dev-node.{d.pkg_mgr}", [])

    if not packages:
        ui.warn(f"No Node.js packages defined for {d.pkg_mgr}")
        return

    distro.pkg_install(packages)

    if process.is_installed("node"):
        result = process.run(["node", "--version"], capture=True)
        ui.info(f"Node.js: {result.stdout.strip()}")

    ui.ok("Node.js development environment installed")
