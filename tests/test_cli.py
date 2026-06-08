from unittest.mock import patch

import yaml
from typer.testing import CliRunner

from tectonic.base import ConfigService
from tectonic.cli import app

runner = CliRunner()


def _make_configs(tmp_path, data: dict) -> ConfigService:
    hosts_file = tmp_path / "hosts.yaml"
    hosts_file.write_text(yaml.dump(data))
    return ConfigService(config_dir=tmp_path)


class TestHelp:
    def test_main_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Environment Setup CLI Tool" in result.stdout

    def test_apply_help(self):
        result = runner.invoke(app, ["apply", "--help"])
        assert result.exit_code == 0
        assert "Converge" in result.stdout

    def test_packages_help(self):
        result = runner.invoke(app, ["packages", "--help"])
        assert result.exit_code == 0

    def test_tools_help(self):
        result = runner.invoke(app, ["tools", "--help"])
        assert result.exit_code == 0

    def test_dotfiles_help(self):
        result = runner.invoke(app, ["dotfiles", "--help"])
        assert result.exit_code == 0


class TestApply:
    def test_unknown_host(self, tmp_path):
        configs = _make_configs(tmp_path, {
            "presets": {"test": ["base"]},
            "hosts": {"otherhost": {"preset": "test"}},
        })

        with patch("tectonic.cli.apply.host.get_hostname", return_value="unknownhost"), \
             patch("tectonic.cli.apply.config.configs", configs):
            result = runner.invoke(app, ["apply"])

        assert result.exit_code == 1

    def test_apply_runs_all_steps(self, tmp_path):
        configs = _make_configs(tmp_path, {
            "presets": {"test": ["base", "shell"]},
            "hosts": {"testhost": {"preset": "test"}},
        })

        with patch("tectonic.cli.apply.host.get_hostname", return_value="testhost"), \
             patch("tectonic.cli.apply.config.configs", configs), \
             patch("tectonic.cli.apply.packages_cmd.packages") as mock_pkg, \
             patch("tectonic.cli.apply.dotfiles_cmd.dotfiles") as mock_dot, \
             patch("tectonic.cli.apply.tools_cmd.tools") as mock_tools:
            result = runner.invoke(app, ["apply"])

        assert result.exit_code == 0
        mock_pkg.assert_called_once()
        mock_dot.assert_called_once()
        mock_tools.assert_called_once()

    def test_hpc_host_resolves_alias(self, tmp_path):
        configs = _make_configs(tmp_path, {
            "presets": {"hpc": ["shell-hpc"]},
            "hosts": {
                "pioneer": {
                    "preset": "hpc",
                    "user": "axj770",
                    "aliases": ["hpc5", "hpc6"],
                    "hpc": {"scratch": "/scratch", "lmod_pkg": "/usr/local/lmod/lmod"},
                },
            },
        })

        with patch("tectonic.cli.apply.host.get_hostname", return_value="hpc6"), \
             patch("tectonic.cli.apply.config.configs", configs), \
             patch("tectonic.cli.apply.packages_cmd.packages"), \
             patch("tectonic.cli.apply.dotfiles_cmd.dotfiles"), \
             patch("tectonic.cli.apply.tools_cmd.tools"):
            result = runner.invoke(app, ["apply"])

        assert result.exit_code == 0
