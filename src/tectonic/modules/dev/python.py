from tectonic.core import process, ui


def run() -> None:
    ui.section("Python Development Environment (uv)")

    ui.step("Installing Python via uv")
    process.run(["uv", "python", "install"])

    result = process.run(["uv", "--version"], capture=True)
    ui.info(f"uv: {result.stdout.strip()}")

    result = process.run(["uv", "python", "list", "--only-installed"], capture=True)
    ui.info(f"Installed Python versions:\n{result.stdout.strip()}")

    ui.ok("Python development environment installed")
