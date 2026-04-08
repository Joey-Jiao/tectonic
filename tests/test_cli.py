from unittest.mock import patch

import yaml
from typer.testing import CliRunner

from tectonic.cli import app

runner = CliRunner()


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

    def test_repos_help(self):
        result = runner.invoke(app, ["repos", "--help"])
        assert result.exit_code == 0

    def test_dotfiles_help(self):
        result = runner.invoke(app, ["dotfiles", "--help"])
        assert result.exit_code == 0

    def test_services_help(self):
        result = runner.invoke(app, ["services", "--help"])
        assert result.exit_code == 0
        assert "list" in result.stdout
        assert "status" in result.stdout


class TestApply:
    def test_unknown_host(self, tmp_path):
        hosts_file = tmp_path / "hosts.yml"
        hosts_file.write_text(yaml.dump({
            "presets": {"test": ["base"]},
            "hosts": {"otherhost": {"preset": "test"}},
        }))

        with patch("tectonic.cli.apply.host.get_hostname", return_value="unknownhost"), \
             patch("tectonic.cli.apply.config.HOSTS_FILE", hosts_file):
            result = runner.invoke(app, ["apply"])

        assert result.exit_code == 1

    def test_apply_runs_all_steps(self, tmp_path):
        hosts_file = tmp_path / "hosts.yml"
        hosts_file.write_text(yaml.dump({
            "presets": {"test": ["base", "shell"]},
            "hosts": {"testhost": {"preset": "test"}},
        }))

        with patch("tectonic.cli.apply.host.get_hostname", return_value="testhost"), \
             patch("tectonic.cli.apply.config.HOSTS_FILE", hosts_file), \
             patch("tectonic.cli.apply.packages_cmd.packages") as mock_pkg, \
             patch("tectonic.cli.apply.repos_cmd.pull_local") as mock_repos, \
             patch("tectonic.cli.apply.dotfiles_cmd.dotfiles") as mock_dot, \
             patch("tectonic.cli.apply.services_cmd.deploy") as mock_svc:
            result = runner.invoke(app, ["apply"])

        assert result.exit_code == 0
        mock_pkg.assert_called_once()
        mock_repos.assert_called_once()
        mock_dot.assert_called_once()
        mock_svc.assert_called_once()

    def test_hpc_host_resolves_alias(self, tmp_path):
        hosts_file = tmp_path / "hosts.yml"
        hosts_file.write_text(yaml.dump({
            "presets": {"hpc": ["shell-hpc"]},
            "hosts": {
                "pioneer": {
                    "preset": "hpc",
                    "user": "axj770",
                    "aliases": ["hpc5", "hpc6"],
                    "hpc": {"scratch": "/scratch", "lmod_pkg": "/usr/local/lmod/lmod"},
                },
            },
        }))

        with patch("tectonic.cli.apply.host.get_hostname", return_value="hpc6"), \
             patch("tectonic.cli.apply.config.HOSTS_FILE", hosts_file), \
             patch("tectonic.cli.apply.packages_cmd.packages"), \
             patch("tectonic.cli.apply.repos_cmd.pull_local"), \
             patch("tectonic.cli.apply.dotfiles_cmd.dotfiles"), \
             patch("tectonic.cli.apply.services_cmd.deploy"):
            result = runner.invoke(app, ["apply"])

        assert result.exit_code == 0
