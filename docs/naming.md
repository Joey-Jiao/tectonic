# Naming Conventions

## Machines

Named after mountains. Always lowercase. The name serves as hostname, Tailscale node name, `hosts.yml` key, and SSH config `Host`.

Current fleet: everest, campbell, granite.

### Setting the Hostname

Set before installing any services (Tailscale uses hostname as node name).

**macOS** — three values, all set to the same name:

```bash
sudo scutil --set HostName <name>       # DNS, SSH, hostname command, uname -n
sudo scutil --set LocalHostName <name>  # Bonjour / mDNS (.local)
sudo scutil --set ComputerName <name>   # Finder, AirDrop, System Settings
```

**Linux** — one command plus hosts file:

```bash
sudo hostnamectl set-hostname <name>    # writes /etc/hostname, sets kernel hostname
```

Verify `/etc/hosts` contains `127.0.1.1 <name>`. Reopen terminal to see changes.

## Modules

Format: `<category>-<name>` for categorized modules, or a bare `<name>` for foundational ones.

| Pattern | Examples | Description |
|---------|----------|-------------|
| bare | `base`, `shell` | Foundational modules, no category prefix |
| `dev-*` | `dev-c`, `dev-python`, `dev-node` | Development languages and toolchains |
| `apps-*` | `apps-docker` | Application-level software |

Module names map directly to file paths: `dev-python` lives at `modules/dev/python.py`.

## Config Constants

Constants in `src/tectonic/config.py` use a prefix to denote their category:

| Prefix | Purpose | Examples |
|--------|---------|----------|
| `DIR_` | Directory paths | `DIR_ZSH_CONFIG`, `DIR_MINIFORGE` |
| `URL_` | Download/install URLs | `URL_NVM_INSTALL`, `URL_STARSHIP_INSTALL` |
| `PKGS_` | Package lists | `PKGS_BASE`, `PKGS_DEV_C` |
| `ARCH_` | Architecture identifiers | `ARCH_CONDA`, `ARCH` |
| `OS_` | OS identifiers | `OS_CONDA`, `SYSTEM` |

## Presets

Preset names in `hosts.yml` describe machine roles. Always lowercase: `workstation`, `server`.
