from unittest.mock import patch

import yaml
from typer.testing import CliRunner

from tectonic import modules
from tectonic.cli import app

runner = CliRunner()


class TestHelp:
    def test_main_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Environment Setup CLI Tool" in result.stdout

    def test_install_help(self):
        result = runner.invoke(app, ["install", "--help"])
        assert result.exit_code == 0


class TestInstallList:
    def test_list_modules(self):
        result = runner.invoke(app, ["install", "list"])
        assert result.exit_code == 0
        for name in modules.list_modules():
            assert name in result.stdout


class TestInstallModule:
    def test_invalid_module(self):
        result = runner.invoke(app, ["install", "module", "nonexistent"])
        assert result.exit_code == 1
        assert "Unknown module" in result.stdout


class TestHostAwareInstall:
    def test_unknown_host(self, tmp_path):
        hosts_file = tmp_path / "hosts.yml"
        hosts_file.write_text(yaml.dump({
            "presets": {"test": ["base"]},
            "hosts": {"otherhost": {"preset": "test"}},
        }))

        with patch("tectonic.commands.install.host.get_hostname", return_value="unknownhost"), \
             patch("tectonic.commands.install.config.HOSTS_FILE", hosts_file):
            result = runner.invoke(app, ["install"])

        assert result.exit_code == 1
        assert "not found" in result.stdout

    def test_host_aware_install(self, tmp_path):
        hosts_file = tmp_path / "hosts.yml"
        hosts_file.write_text(yaml.dump({
            "presets": {"test": ["base", "shell"]},
            "hosts": {"testhost": {"preset": "test"}},
        }))

        installed: list[str] = []

        with patch("tectonic.commands.install.host.get_hostname", return_value="testhost"), \
             patch("tectonic.commands.install.config.HOSTS_FILE", hosts_file), \
             patch("tectonic.commands.install._install_modules") as mock_install:
            mock_install.side_effect = lambda names, **kwargs: installed.extend(names)
            result = runner.invoke(app, ["install"])

        assert result.exit_code == 0
        assert "testhost" in result.stdout
        assert installed == ["base", "shell"]

    def test_missing_hosts_file(self, tmp_path):
        missing = tmp_path / "nonexistent.yml"

        with patch("tectonic.commands.install.host.get_hostname", return_value="anyhost"), \
             patch("tectonic.commands.install.config.HOSTS_FILE", missing):
            result = runner.invoke(app, ["install"])

        assert result.exit_code == 1
        assert "not found" in result.stdout

    def test_hpc_host_skips_sudo(self, tmp_path):
        hosts_file = tmp_path / "hosts.yml"
        hosts_file.write_text(yaml.dump({
            "presets": {"hpc": ["shell-hpc"]},
            "hosts": {
                "pioneer": {
                    "preset": "hpc",
                    "user": "axj770",
                    "aliases": ["hpc5"],
                    "hpc": {"scratch": "/scratch/users/axj770", "lmod_pkg": "/usr/local/lmod/lmod"},
                },
            },
        }))

        call_kwargs: dict = {}

        with patch("tectonic.commands.install.host.get_hostname", return_value="hpc5"), \
             patch("tectonic.commands.install.config.HOSTS_FILE", hosts_file), \
             patch("tectonic.commands.install._install_modules") as mock_install:
            mock_install.side_effect = lambda names, **kw: call_kwargs.update(kw)
            result = runner.invoke(app, ["install"])

        assert result.exit_code == 0
        assert "pioneer" in result.stdout
        assert call_kwargs.get("skip_sudo") is True

    def test_alias_resolves_to_tectonic_name(self, tmp_path):
        hosts_file = tmp_path / "hosts.yml"
        hosts_file.write_text(yaml.dump({
            "presets": {"hpc": ["shell-hpc"]},
            "hosts": {
                "pioneer": {
                    "preset": "hpc",
                    "user": "axj770",
                    "aliases": ["hpc5", "hpc6"],
                    "hpc": {"scratch": "/scratch"},
                },
            },
        }))

        with patch("tectonic.commands.install.host.get_hostname", return_value="hpc6"), \
             patch("tectonic.commands.install.config.HOSTS_FILE", hosts_file), \
             patch("tectonic.commands.install._install_modules"):
            result = runner.invoke(app, ["install"])

        assert result.exit_code == 0
        assert "pioneer" in result.stdout
