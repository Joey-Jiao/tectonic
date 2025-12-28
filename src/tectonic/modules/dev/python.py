import tempfile

from tectonic import config
from tectonic.core import fs, process, ui


def activate_conda() -> None:
    if config.DIR_MINIFORGE.exists():
        conda_bin = config.DIR_MINIFORGE / "bin" / "conda"
        result = process.run(
            [str(conda_bin), "shell.bash", "hook"],
            capture=True,
        )
        if result.returncode == 0:
            process.run_shell(result.stdout)


def run() -> None:
    ui.section("Python Development Environment (Miniforge)")

    if config.DIR_MINIFORGE.exists():
        ui.info(f"Miniforge already installed at {config.DIR_MINIFORGE}")
        return

    fs.ensure_dir(config.DIR_LOCAL)

    with tempfile.NamedTemporaryFile(suffix=".sh", delete=False) as f:
        installer = f.name

    ui.step("Downloading Miniforge")
    process.run(["curl", "-fsSL", config.URL_MINIFORGE, "-o", installer])
    process.run(["chmod", "+x", installer])

    ui.step(f"Installing Miniforge to {config.DIR_MINIFORGE}")
    process.run([installer, "-b", "-p", str(config.DIR_MINIFORGE)])

    import os
    os.unlink(installer)

    conda_bin = config.DIR_MINIFORGE / "bin" / "conda"
    ui.info(f"Conda version: {process.run([str(conda_bin), '--version'], capture=True).stdout.strip()}")
    ui.ok(f"Miniforge installed at {config.DIR_MINIFORGE}")
