import pytest
from typer.testing import CliRunner

from tectonic.cli import app

runner = CliRunner()


class TestHelp:
    def test_main_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Linux Setup CLI Tool" in result.stdout

    def test_install_help(self):
        result = runner.invoke(app, ["install", "--help"])
        assert result.exit_code == 0
        assert "Install system modules" in result.stdout

    def test_dotfiles_help(self):
        result = runner.invoke(app, ["dotfiles", "--help"])
        assert result.exit_code == 0
        assert "Manage dotfiles" in result.stdout


class TestInstallList:
    def test_list_modules(self):
        result = runner.invoke(app, ["install", "list"])
        assert result.exit_code == 0
        assert "base" in result.stdout
        assert "shell" in result.stdout
        assert "dev-c" in result.stdout
        assert "dev-python" in result.stdout
        assert "dev-node" in result.stdout
        assert "apps-docker" in result.stdout

    def test_install_no_args_shows_help(self):
        result = runner.invoke(app, ["install"])
        assert "Usage" in result.stdout
