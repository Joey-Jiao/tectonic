# Naming Conventions

## Machines

Named after mountains. Always lowercase. The name serves as hostname, Tailscale node name, `hosts.yaml` key, and SSH config `Host`.

Current fleet: blanc, everest, campbell, granite (macOS workstations / server), pioneer (HPC).

### Setting the Hostname

Set before installing Tailscale (it uses hostname as node name).

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
| `shell-*` | `shell-hpc` | Shell variants for special environments |

Module names map directly to file paths: `dev-python` lives at `modules/dev/python.py`, `shell-hpc` at `modules/shell_hpc.py`. Modules are internal to `tectonic packages` and not exposed as CLI commands.

## Tools

Tools (declared in `configs/tools.yaml`) take the unprefixed binary name as their key. The key serves as:

- The map key in `tools.yaml`
- The wrapper filename in `~/.local/bin/<name>`
- The binary name passed to `uv run --project <path> <name>`

So `strata` is the binary, the wrapper, and the key — always the same string.

## Config Constants

Constants in `src/tectonic/config.py` use a prefix to denote their category:

| Prefix | Purpose | Examples |
|--------|---------|----------|
| `DIR_` | Directory paths | `DIR_ZSH_CONFIG`, `DIR_LOCAL` |
| (bare) | Single global identifiers | `ARCH`, `SYSTEM`, `LOG_FILE`, `CHEZMOI_SOURCE` |

## Presets

Preset names in `hosts.yaml` describe machine roles. Always lowercase: `workstation`, `server`, `hpc`.
