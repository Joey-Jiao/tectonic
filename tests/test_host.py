import pytest
import yaml

from tectonic.core import host

SAMPLE_CONFIG = {
    "presets": {
        "workstation": ["base", "shell", "dev-c", "dev-python", "dev-node"],
        "server": ["base", "shell", "dev-python"],
    },
    "hosts": {
        "everest": {"preset": "workstation", "user": "blank"},
        "campbell": {"preset": "server", "extra": ["dev-node"], "user": "blank"},
        "granite": {"preset": "workstation", "extra": ["apps-docker"], "user": "blank"},
    },
}


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
