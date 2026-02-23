from pathlib import Path

from tectonic import config


class TestPaths:
    def test_project_root_exists(self):
        assert config.TECTONIC_ROOT.exists()
        assert (config.TECTONIC_ROOT / "pyproject.toml").exists()

    def test_configs_dir_exists(self):
        assert config.CONFIGS_DIR.exists()
        assert config.CONFIGS_DIR == config.TECTONIC_ROOT / "configs"

    def test_hosts_file_path(self):
        assert config.HOSTS_FILE == config.CONFIGS_DIR / "hosts.yml"

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

    def test_local_dir(self):
        assert config.DIR_LOCAL == Path.home() / ".local"

    def test_arch_and_system(self):
        assert isinstance(config.ARCH, str)
        assert isinstance(config.SYSTEM, str)

    def test_available_modules(self):
        assert "base" in config.AVAILABLE_MODULES
        assert "shell" in config.AVAILABLE_MODULES
        assert "dev-python" in config.AVAILABLE_MODULES


class TestConfigService:
    def test_configs_instance_exists(self):
        assert config.configs is not None

    def test_packages_base(self):
        packages = config.configs.get("packages.base.brew")
        assert isinstance(packages, list)
        assert "git" in packages

    def test_packages_dev_node(self):
        assert "nodejs" in config.configs.get("packages.dev-node.apt", [])
        assert "node" in config.configs.get("packages.dev-node.brew", [])

    def test_packages_pacman_preserved(self):
        assert config.configs.get("packages.base.pacman") is not None
        assert config.configs.get("packages.dev-c.pacman") is not None

    def test_urls(self):
        starship_url = config.configs.get("urls.starship")
        assert isinstance(starship_url, str)
        assert starship_url.startswith("https://")
