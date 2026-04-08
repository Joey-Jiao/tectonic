from tectonic import config
from tectonic.core import process, ui


def dotfiles() -> None:
    """Apply dotfiles via chezmoi."""
    ui.section("Dotfiles")

    if not process.is_installed("chezmoi"):
        ui.info("chezmoi not found, skipping dotfiles")
        return

    source = str(config.CHEZMOI_SOURCE)
    chezmoi_config = config.XDG_CONFIG_HOME / "chezmoi" / "chezmoi.toml"

    if chezmoi_config.exists():
        process.run_interactive(["chezmoi", "apply", "--source", source, "--force"])
    else:
        process.run_interactive(["chezmoi", "init", "--source", source, "--apply"])

    ui.ok("Dotfiles applied")
