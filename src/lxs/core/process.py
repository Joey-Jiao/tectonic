import shutil
import subprocess
from pathlib import Path

from lxs.core import ui


def run(
    cmd: list[str],
    check: bool = True,
    capture: bool = False,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a command, logging output based on verbosity."""
    ui.info(f"Running: {' '.join(cmd)}")

    if capture:
        # Always capture when explicitly requested
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=True,
            text=True,
            cwd=cwd,
        )
        ui.log_cmd_output(result.stdout)
        if result.stderr:
            ui.log_cmd_output(result.stderr)
        return result

    if ui.is_verbose():
        # Verbose mode: show output in real-time
        result = subprocess.run(
            cmd,
            check=check,
            text=True,
            cwd=cwd,
        )
        return result
    else:
        # Quiet mode: capture and log to file only
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=True,
            text=True,
            cwd=cwd,
        )
        ui.log_cmd_output(result.stdout)
        if result.stderr:
            ui.log_cmd_output(result.stderr)
        return result


def run_quiet(cmd: list[str], cwd: Path | None = None) -> bool:
    """Run a command silently, return success status."""
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd=cwd,
        )
        ui.log_cmd_output(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        ui.log_cmd_output(e.stdout or "")
        ui.log_cmd_output(e.stderr or "")
        return False


def run_interactive(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a command interactively (allows user input like passwords)."""
    ui.info(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, text=True)


def is_installed(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def run_shell(script: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a shell script with bash, logging output based on verbosity."""
    ui.info(f"Running shell script")

    if ui.is_verbose():
        return subprocess.run(
            ["bash", "-c", script],
            check=check,
            text=True,
        )
    else:
        result = subprocess.run(
            ["bash", "-c", script],
            check=check,
            capture_output=True,
            text=True,
        )
        ui.log_cmd_output(result.stdout)
        if result.stderr:
            ui.log_cmd_output(result.stderr)
        return result
