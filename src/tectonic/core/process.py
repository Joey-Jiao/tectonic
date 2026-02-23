import shutil
import subprocess
from pathlib import Path

from tectonic.core import ui


def _exec(
    cmd: list[str],
    check: bool = True,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    if ui.is_verbose():
        return subprocess.run(cmd, check=check, text=True, cwd=cwd)

    result = subprocess.run(
        cmd, check=check, capture_output=True, text=True, cwd=cwd,
    )
    ui.log_cmd_output(result.stdout)
    if result.stderr:
        ui.log_cmd_output(result.stderr)
    return result


def run(
    cmd: list[str],
    check: bool = True,
    capture: bool = False,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    ui.info(f"Running: {' '.join(cmd)}")

    if capture:
        result = subprocess.run(
            cmd, check=check, capture_output=True, text=True, cwd=cwd,
        )
        ui.log_cmd_output(result.stdout)
        if result.stderr:
            ui.log_cmd_output(result.stderr)
        return result

    return _exec(cmd, check=check, cwd=cwd)


def run_quiet(cmd: list[str], cwd: Path | None = None) -> bool:
    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True, cwd=cwd,
        )
        ui.log_cmd_output(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        ui.log_cmd_output(e.stdout or "")
        ui.log_cmd_output(e.stderr or "")
        return False


def run_interactive(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    ui.info(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, text=True)


def is_installed(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def run_shell(script: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    ui.info("Running shell script")
    return _exec(["bash", "-c", script], check=check)
