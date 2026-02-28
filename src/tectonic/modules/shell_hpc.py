from pathlib import Path

from tectonic.core import process, ui

LOCAL_BIN = Path.home() / ".local" / "bin"


def install_chezmoi() -> None:
    if process.is_installed("chezmoi"):
        ui.info("chezmoi already installed")
        return

    ui.step("Installing chezmoi")
    process.run_shell(f'sh -c "$(curl -fsLS get.chezmoi.io)" -- -b {LOCAL_BIN}')
    ui.ok("chezmoi installed")


def install_starship() -> None:
    if process.is_installed("starship"):
        ui.info("starship already installed")
        return

    ui.step("Installing starship")
    process.run_shell(f"curl -fsSL https://starship.rs/install.sh | sh -s -- -b {LOCAL_BIN} -y")
    ui.ok("starship installed")


def run() -> None:
    ui.section("Shell Environment (HPC)")

    LOCAL_BIN.mkdir(parents=True, exist_ok=True)

    install_chezmoi()
    install_starship()

    ui.ok("HPC shell environment configured")
