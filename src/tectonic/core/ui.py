from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()

# Global state
_log_file: Path | None = None
_verbose: bool = False


def init(log_file: Path, verbose: bool = False) -> None:
    """Initialize UI with log file and verbosity setting."""
    global _log_file, _verbose
    _log_file = log_file
    _verbose = verbose

    # Ensure log directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Clear log file
    log_file.write_text("")


def is_verbose() -> bool:
    return _verbose


def _log(msg: str) -> None:
    """Write message to log file."""
    if _log_file is None:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _log_file.open("a") as f:
        f.write(f"[{timestamp}] {msg}\n")


def info(msg: str) -> None:
    _log(f"[INFO] {msg}")
    if _verbose:
        console.print(f"[blue][INFO][/blue]  {msg}")


def ok(msg: str) -> None:
    _log(f"[OK] {msg}")
    console.print(f"[green][OK][/green]    {msg}")


def warn(msg: str) -> None:
    _log(f"[WARN] {msg}")
    console.print(f"[yellow][WARN][/yellow]  {msg}")


def error(msg: str) -> None:
    _log(f"[ERROR] {msg}")
    console.print(f"[red][ERROR][/red] {msg}")


def step(msg: str) -> None:
    _log(f"[STEP] {msg}")
    console.print(f"[cyan]>>>[/cyan] {msg}")


def section(title: str) -> None:
    _log(f"===== {title} =====")
    console.print()
    console.print(Panel(title, style="cyan", expand=False))
    console.print()


def log_cmd_output(output: str) -> None:
    """Log command output to file, optionally display if verbose."""
    if output:
        _log(output)
        if _verbose:
            console.print(output)
