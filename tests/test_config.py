import pytest
from pathlib import Path

from tectonic import config


class TestPaths:
    def test_project_root_exists(self):
        assert config.TECTONIC_ROOT.exists()
        assert (config.TECTONIC_ROOT / "pyproject.toml").exists()

    def test_dotfiles_dir_exists(self):
        assert config.DOTFILES_DIR.exists()
        assert config.DOTFILES_DIR == config.TECTONIC_ROOT / "dotfiles"

    def test_xdg_paths_are_under_home(self):
        home = Path.home()
        assert config.XDG_CONFIG_HOME == home / ".config"
        assert config.XDG_DATA_HOME == home / ".local" / "share"
        assert config.XDG_CACHE_HOME == home / ".cache"

    def test_zsh_paths(self):
        assert config.DIR_ZSH_CONFIG == config.XDG_CONFIG_HOME / "zsh"
        assert config.DIR_ZSH_DATA == config.XDG_DATA_HOME / "zsh"
        assert config.DIR_ZSH_CACHE == config.XDG_CACHE_HOME / "zsh"
        assert config.DIR_ZSH_PLUGINS == config.DIR_ZSH_DATA / "plugins"

    def test_tool_paths(self):
        assert config.DIR_LOCAL == Path.home() / ".local"
        assert config.DIR_MINIFORGE == config.DIR_LOCAL / "miniforge"
        assert config.DIR_NVM == config.DIR_LOCAL / "nvm"


class TestUrls:
    def test_urls_are_strings(self):
        assert isinstance(config.URL_NVM_INSTALL, str)
        assert isinstance(config.URL_MINIFORGE, str)
        assert isinstance(config.URL_STARSHIP_INSTALL, str)

    def test_urls_are_https(self):
        assert config.URL_NVM_INSTALL.startswith("https://")
        assert config.URL_MINIFORGE.startswith("https://")
        assert config.URL_STARSHIP_INSTALL.startswith("https://")


class TestPackages:
    def test_pkgs_base_has_common_managers(self):
        assert "apt" in config.PKGS_BASE
        assert "pacman" in config.PKGS_BASE
        assert "dnf" in config.PKGS_BASE
        assert "brew" in config.PKGS_BASE

    def test_pkgs_shell_has_zsh(self):
        for mgr, packages in config.PKGS_SHELL.items():
            assert "zsh" in packages, f"zsh missing for {mgr}"

    def test_available_modules(self):
        expected = ["base", "shell", "dev-c", "dev-python", "dev-node", "apps-docker"]
        assert config.AVAILABLE_MODULES == expected
