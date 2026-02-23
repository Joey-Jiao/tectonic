import plistlib

import pytest

from tectonic.core.host import resolve_services
from tectonic.core.service import ServiceDef, _generate_plist, _generate_unit


SAMPLE_SERVICES_CONFIG = {
    "services": {
        "mcp-server": {
            "program": "/opt/homebrew/bin/node",
            "args": ["server.js"],
            "working_directory": "~/workspace/mcp-server",
            "env": {"PORT": "3000"},
            "keep_alive": True,
            "run_at_load": True,
            "hosts": ["campbell"],
        },
        "backup-agent": {
            "program": "/usr/bin/rsync",
            "args": ["--daemon"],
            "hosts": ["granite"],
        },
        "monitoring": {
            "program": "/usr/local/bin/monitor",
            "interval": 300,
            "hosts": ["campbell", "granite"],
        },
    },
}


class TestResolveServices:
    def test_single_host_match(self):
        result = resolve_services("campbell", SAMPLE_SERVICES_CONFIG)
        assert "mcp-server" in result
        assert "monitoring" in result
        assert "backup-agent" not in result

    def test_different_host(self):
        result = resolve_services("granite", SAMPLE_SERVICES_CONFIG)
        assert "backup-agent" in result
        assert "monitoring" in result
        assert "mcp-server" not in result

    def test_no_match(self):
        result = resolve_services("everest", SAMPLE_SERVICES_CONFIG)
        assert result == {}

    def test_empty_config(self):
        result = resolve_services("campbell", {"services": {}})
        assert result == {}

    def test_missing_services_key(self):
        result = resolve_services("campbell", {})
        assert result == {}


class TestServiceDef:
    def test_from_yaml_full(self):
        data = SAMPLE_SERVICES_CONFIG["services"]["mcp-server"]
        svc = ServiceDef.from_yaml("mcp-server", data)
        assert svc.name == "mcp-server"
        assert svc.program == "/opt/homebrew/bin/node"
        assert svc.args == ["server.js"]
        assert svc.working_directory == "~/workspace/mcp-server"
        assert svc.env == {"PORT": "3000"}
        assert svc.keep_alive is True
        assert svc.run_at_load is True
        assert svc.interval is None

    def test_from_yaml_minimal(self):
        svc = ServiceDef.from_yaml("test", {"program": "/usr/bin/test", "hosts": ["h"]})
        assert svc.program == "/usr/bin/test"
        assert svc.args == []
        assert svc.working_directory is None
        assert svc.env == {}
        assert svc.keep_alive is False
        assert svc.run_at_load is True

    def test_from_yaml_with_interval(self):
        data = SAMPLE_SERVICES_CONFIG["services"]["monitoring"]
        svc = ServiceDef.from_yaml("monitoring", data)
        assert svc.interval == 300
        assert svc.keep_alive is False

    def test_label(self):
        svc = ServiceDef(name="mcp-server", program="/bin/test")
        assert svc.label == "dev.joeyjiao.mcp-server"


class TestGeneratePlist:
    def test_basic_plist(self):
        svc = ServiceDef(name="test", program="/usr/bin/test", args=["--flag"])
        raw = _generate_plist(svc)
        plist = plistlib.loads(raw)
        assert plist["Label"] == "dev.joeyjiao.test"
        assert plist["ProgramArguments"] == ["/usr/bin/test", "--flag"]
        assert plist["RunAtLoad"] is True

    def test_plist_with_env(self):
        svc = ServiceDef(name="test", program="/bin/p", env={"FOO": "bar"})
        plist = plistlib.loads(_generate_plist(svc))
        assert plist["EnvironmentVariables"] == {"FOO": "bar"}

    def test_plist_with_keep_alive(self):
        svc = ServiceDef(name="test", program="/bin/p", keep_alive=True)
        plist = plistlib.loads(_generate_plist(svc))
        assert plist["KeepAlive"] is True

    def test_plist_without_keep_alive(self):
        svc = ServiceDef(name="test", program="/bin/p", keep_alive=False)
        plist = plistlib.loads(_generate_plist(svc))
        assert "KeepAlive" not in plist

    def test_plist_with_interval(self):
        svc = ServiceDef(name="test", program="/bin/p", interval=60)
        plist = plistlib.loads(_generate_plist(svc))
        assert plist["StartInterval"] == 60

    def test_plist_working_directory(self):
        svc = ServiceDef(name="test", program="/bin/p", working_directory="/tmp/work")
        plist = plistlib.loads(_generate_plist(svc))
        assert plist["WorkingDirectory"] == "/tmp/work"


class TestGenerateUnit:
    def test_basic_unit(self):
        svc = ServiceDef(name="test", program="/usr/bin/test", args=["--flag"])
        unit = _generate_unit(svc)
        assert "ExecStart=/usr/bin/test --flag" in unit
        assert "Description=tectonic service: test" in unit
        assert "WantedBy=default.target" in unit

    def test_unit_with_env(self):
        svc = ServiceDef(name="test", program="/bin/p", env={"FOO": "bar"})
        unit = _generate_unit(svc)
        assert "Environment=FOO=bar" in unit

    def test_unit_with_keep_alive(self):
        svc = ServiceDef(name="test", program="/bin/p", keep_alive=True)
        unit = _generate_unit(svc)
        assert "Restart=always" in unit

    def test_unit_without_keep_alive(self):
        svc = ServiceDef(name="test", program="/bin/p", keep_alive=False)
        unit = _generate_unit(svc)
        assert "Restart" not in unit

    def test_unit_working_directory(self):
        svc = ServiceDef(name="test", program="/bin/p", working_directory="/tmp/work")
        unit = _generate_unit(svc)
        assert "WorkingDirectory=/tmp/work" in unit


class TestInstallService:
    def test_install_creates_plist(self, tmp_path, monkeypatch):
        monkeypatch.setattr("tectonic.core.distro.is_macos", lambda: True)
        monkeypatch.setattr("tectonic.config.DIR_LAUNCHAGENTS", tmp_path)

        svc = ServiceDef(name="test-svc", program="/bin/test")
        from tectonic.core.service import install_service
        result = install_service(svc)

        assert result is True
        plist_file = tmp_path / "dev.joeyjiao.test-svc.plist"
        assert plist_file.exists()
        content = plistlib.loads(plist_file.read_bytes())
        assert content["Label"] == "dev.joeyjiao.test-svc"

    def test_install_skips_unchanged(self, tmp_path, monkeypatch):
        monkeypatch.setattr("tectonic.core.distro.is_macos", lambda: True)
        monkeypatch.setattr("tectonic.config.DIR_LAUNCHAGENTS", tmp_path)

        svc = ServiceDef(name="test-svc", program="/bin/test")
        from tectonic.core.service import install_service
        install_service(svc)
        result = install_service(svc)
        assert result is False

    def test_install_creates_unit(self, tmp_path, monkeypatch):
        monkeypatch.setattr("tectonic.core.distro.is_macos", lambda: False)
        monkeypatch.setattr("tectonic.config.DIR_SYSTEMD_USER", tmp_path)

        svc = ServiceDef(name="test-svc", program="/bin/test")
        from tectonic.core.service import install_service
        result = install_service(svc)

        assert result is True
        unit_file = tmp_path / "dev.joeyjiao.test-svc.service"
        assert unit_file.exists()
        assert "ExecStart=/bin/test" in unit_file.read_text()

    def test_install_unit_skips_unchanged(self, tmp_path, monkeypatch):
        monkeypatch.setattr("tectonic.core.distro.is_macos", lambda: False)
        monkeypatch.setattr("tectonic.config.DIR_SYSTEMD_USER", tmp_path)

        svc = ServiceDef(name="test-svc", program="/bin/test")
        from tectonic.core.service import install_service
        install_service(svc)
        result = install_service(svc)
        assert result is False
