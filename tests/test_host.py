import pytest
import yaml

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
        assert entry["user"] == "blank"

    def test_alias_match(self):
        name, entry = host.find_host("hpc5", SAMPLE_CONFIG)
        assert name == "pioneer"
        assert entry["user"] == "axj770"

    def test_alias_match_all_nodes(self):
        for alias in ["hpc5", "hpc6", "hpc7", "hpc8", "hpctransfer1"]:
            name, _ = host.find_host(alias, SAMPLE_CONFIG)
            assert name == "pioneer"

    def test_unknown_host(self):
        with pytest.raises(KeyError, match="not found"):
            host.find_host("unknown", SAMPLE_CONFIG)

    def test_hpc_entry_has_hpc_field(self):
        _, entry = host.find_host("pioneer", SAMPLE_CONFIG)
        assert "hpc" in entry
        assert entry["hpc"]["scratch"] == "/scratch/users/axj770"


class TestResolveModules:
    def test_workstation_preset(self):
        result = host.resolve_modules("everest", SAMPLE_CONFIG)
        assert result == ["base", "shell", "dev-c", "dev-python", "dev-node"]

    def test_server_with_extra(self):
        result = host.resolve_modules("campbell", SAMPLE_CONFIG)
        assert result == ["base", "shell", "dev-python", "dev-node"]

    def test_workstation_with_extra(self):
        result = host.resolve_modules("granite", SAMPLE_CONFIG)
        assert result == ["base", "shell", "dev-c", "dev-python", "dev-node", "apps-docker"]

    def test_extra_no_duplicates(self):
        config = {
            "presets": {"test": ["base", "shell"]},
            "hosts": {"myhost": {"preset": "test", "extra": ["shell", "dev-c"]}},
        }
        result = host.resolve_modules("myhost", config)
        assert result == ["base", "shell", "dev-c"]

    def test_unknown_host(self):
        with pytest.raises(KeyError, match="not found"):
            host.resolve_modules("unknown", SAMPLE_CONFIG)

    def test_hpc_preset(self):
        result = host.resolve_modules("pioneer", SAMPLE_CONFIG)
        assert result == ["shell-hpc"]

    def test_hpc_via_alias(self):
        result = host.resolve_modules("hpc6", SAMPLE_CONFIG)
        assert result == ["shell-hpc"]


class TestLoadHosts:
    def test_load_hosts(self, tmp_path):
        hosts_file = tmp_path / "hosts.yml"
        hosts_file.write_text(yaml.dump(SAMPLE_CONFIG))

        result = host.load_hosts(hosts_file)
        assert "presets" in result
        assert "hosts" in result
        assert "everest" in result["hosts"]

    def test_load_hosts_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            host.load_hosts(tmp_path / "nonexistent.yml")


class TestGetHostname:
    def test_returns_string(self):
        result = host.get_hostname()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_returns_short_name(self):
        result = host.get_hostname()
        assert "." not in result
