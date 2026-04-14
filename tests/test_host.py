import pytest
import yaml

from tectonic.base import ConfigService
from tectonic.core import host

SAMPLE_CONFIG = {
    "presets": {
        "workstation": ["base", "shell", "dev-c", "dev-python", "dev-node"],
        "server": ["base", "shell", "dev-python"],
        "hpc": ["shell-hpc"],
    },
    "hosts": {
        "everest": {"preset": "workstation", "user": "blank"},
        "campbell": {"preset": "server", "extra": ["dev-node"], "user": "blank"},
        "granite": {"preset": "workstation", "extra": ["apps-docker"], "user": "blank"},
        "pioneer": {
            "preset": "hpc",
            "user": "axj770",
            "aliases": ["hpc5", "hpc6", "hpc7", "hpc8", "hpctransfer1"],
            "hpc": {
                "scratch": "/scratch/users/axj770",
                "lmod_pkg": "/usr/local/lmod/lmod",
                "modules": ["gcc", "git", "python", "tmux"],
            },
        },
    },
}


class TestFindHost:
    def test_direct_match(self):
        name, entry = host.find_host("everest", SAMPLE_CONFIG)
        assert name == "everest"
        assert entry["preset"] == "workstation"

    def test_alias_match(self):
        name, entry = host.find_host("hpc5", SAMPLE_CONFIG)
        assert name == "pioneer"
        assert entry["user"] == "axj770"

    def test_unknown_host(self):
        with pytest.raises(KeyError, match="unknownhost"):
            host.find_host("unknownhost", SAMPLE_CONFIG)


class TestResolveModules:
    def test_workstation(self):
        result = host.resolve_modules("everest", SAMPLE_CONFIG)
        assert result == ["base", "shell", "dev-c", "dev-python", "dev-node"]

    def test_server_with_extra(self):
        result = host.resolve_modules("campbell", SAMPLE_CONFIG)
        assert result == ["base", "shell", "dev-python", "dev-node"]

    def test_workstation_with_extra(self):
        result = host.resolve_modules("granite", SAMPLE_CONFIG)
        assert result == ["base", "shell", "dev-c", "dev-python", "dev-node", "apps-docker"]

    def test_hpc_preset(self):
        result = host.resolve_modules("pioneer", SAMPLE_CONFIG)
        assert result == ["shell-hpc"]

    def test_hpc_via_alias(self):
        result = host.resolve_modules("hpc6", SAMPLE_CONFIG)
        assert result == ["shell-hpc"]


class TestLoadHosts:
    def test_load_hosts(self, tmp_path):
        hosts_file = tmp_path / "hosts.yaml"
        hosts_file.write_text(yaml.dump(SAMPLE_CONFIG))

        configs = ConfigService(config_dir=tmp_path)
        result = host.load_hosts(configs)
        assert "presets" in result
        assert "hosts" in result
        assert "everest" in result["hosts"]

    def test_load_hosts_empty(self, tmp_path):
        configs = ConfigService(config_dir=tmp_path)
        result = host.load_hosts(configs)
        assert result == {"presets": {}, "hosts": {}}


class TestGetHostname:
    def test_returns_string(self):
        result = host.get_hostname()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_returns_short_name(self):
        result = host.get_hostname()
        assert "." not in result
