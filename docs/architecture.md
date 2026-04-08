# Architecture

tectonic is a single repository for all environment-related concerns across multiple machines. The system is organized into five layers, each building on the ones below it.

## Layers

```
Layer 4: Services        launchd/systemd + command wrappers
Layer 3: Data            rsync over Tailscale
Layer 2: Configuration   chezmoi (dotfiles, config files)
Layer 1: Software        tectonic CLI (packages, tools, runtimes)
Layer 0: Infrastructure  1Password (identity, secrets) + Tailscale (network)
```

Each layer has a single owner and a clear boundary:

| Layer | Owner | Manages | Depends On |
|-------|-------|---------|------------|
| 0 — Infrastructure | 1Password, Tailscale | Identity, secrets, network mesh | bare OS |
| 1 — Software | tectonic CLI (`src/tectonic/`) | Installed packages, tools, runtimes | Layer 0 |
| 2 — Configuration | chezmoi (`home/`) | Dotfiles, config files in `$HOME` | Layer 1 |
| 3 — Data | rsync over Tailscale | User data (datasets, resources) | Layer 0 |
| 4 — Services | launchd / systemd + wrappers | Daemons and command wrappers | Layer 0-2 |

Layer 3 (Data) and Layers 1-2 (Software, Configuration) are independent of each other — both only require Layer 0. Services at Layer 4 typically need software installed and configured before they can run.

## Repository Layout

```
tectonic/
├── configs/                  # Externalized configuration
│   ├── hosts.yml             # Machine registry and desired state
│   ├── packages/             # Per-module package lists (YAML)
│   ├── services.yaml         # Service definitions (daemons + commands)
│   ├── pull.yaml             # Repo declarations per host
│   ├── sync.yaml             # Sync paths and ignore files for rsync
│   └── urls.yaml
├── home/                     # chezmoi source directory (Layer 2)
│   ├── .chezmoidata/         # symlinks to configs/ for chezmoi template data
│   ├── dot_zshenv
│   ├── dot_claude/           # Claude Code config (CLAUDE.md, mcp.json, settings.json)
│   ├── dot_config/
│   │   ├── zsh/
│   │   ├── git/
│   │   ├── starship.toml
│   │   └── 1Password/ssh/
│   └── dot_ssh/
├── src/tectonic/             # Python environment manager (Layer 1)
│   ├── config.py
│   ├── base/                 # ConfigService (reads configs/ YAML)
│   ├── cli/                  # CLI commands and app entry point
│   │   ├── __init__.py       # App definition and command registration
│   │   ├── apply.py          # Orchestration (packages → repos → dotfiles → services)
│   │   ├── packages.py       # Package installation
│   │   ├── repos.py          # Repo clone/pull
│   │   ├── dotfiles.py       # Chezmoi apply
│   │   ├── services.py       # Read-only service inspection (list, status)
│   │   ├── sync.py           # rsync-based data push
│   │   └── deploy.py         # deploy + broadcast
│   ├── core/
│   │   ├── distro.py
│   │   ├── process.py
│   │   ├── fs.py
│   │   ├── host.py
│   │   ├── repos.py          # Repo resolution, clone/pull, status
│   │   ├── services.py
│   │   └── ui.py
│   └── modules/              # Internal install modules (not exposed in CLI)
│       ├── __init__.py       # Module registry
│       ├── base.py
│       ├── shell.py
│       ├── dev/
│       │   ├── c.py
│       │   ├── python.py
│       │   └── node.py
│       └── apps/
│           └── docker.py
├── docs/
├── tests/
└── pyproject.toml
```

## hosts.yml

The machine registry (`configs/hosts.yml`). Each host declares a preset (a named set of modules) and optional extra modules. `tectonic apply` reads the current hostname, looks it up in `hosts.yml`, and converges to the declared state.

```yaml
presets:
  workstation: [base, shell, dev-c, dev-python, dev-node]
  server: [base, shell, dev-python]

hosts:
  everest:
    preset: workstation
    user: blank
  campbell:
    preset: server
    extra: [dev-node]
    user: blank
  granite:
    preset: workstation
    extra: [apps-docker]
    user: blank
```

## Module System

Each module is a Python file with a `run()` entry point, registered in `modules/__init__.py`. Modules are internal to the `apply` pipeline — they are not exposed as CLI commands.

| Module | Path | Contents |
|--------|------|----------|
| `base` | `modules/base.py` | curl, git, vim, neovim, htop, tree, unzip |
| `shell` | `modules/shell.py` | zsh, starship, plugins, dotfiles |
| `dev-c` | `modules/dev/c.py` | gcc, cmake, gdb, ninja |
| `dev-python` | `modules/dev/python.py` | uv (Python version management + venv + package install) |
| `dev-node` | `modules/dev/node.py` | Node.js LTS via package manager |
| `apps-docker` | `modules/apps/docker.py` | Docker |

## Apply Pipeline

`tectonic apply` converges the current host to its declared state by orchestrating four steps:

```
1. packages      resolve host preset → run matching modules
2. repos         clone missing repos, pull existing (from pull.yaml)
3. dotfiles      chezmoi apply --source home/ --force
4. services      install/load services, remove stale ones
```

Each step is idempotent and available as a standalone command.

## CLI

| Command | Behavior |
|---------|----------|
| `tectonic apply` | Converge current host (packages → repos → dotfiles → services) |
| `tectonic packages` | Install packages for current host |
| `tectonic repos [host]` | Clone and pull repos (default: all hosts) |
| `tectonic dotfiles` | Apply dotfiles via chezmoi |
| `tectonic services` | Deploy services for current host |
| `tectonic services list` | List services with configuration details |
| `tectonic services status` | Show runtime status |
| `tectonic sync [host]` | Push workspace data to remote hosts via rsync |
| `tectonic deploy <host> <cmd...>` | Execute tectonic command on a remote host via SSH |
| `tectonic broadcast <cmd...>` | Execute tectonic command on all reachable remote hosts |

## Repos

`tectonic repos` manages git repos declared in `configs/pull.yaml`:

```yaml
root: ~/workspace

repos:
  infra/tectonic:
    url: git@github.com:Joey-Jiao/tectonic.git
    hosts: [blanc, everest, campbell, granite]
  infra/strata:
    url: git@github.com:Joey-Jiao/strata.git
    hosts: [blanc, campbell]
```

Repos are resolved relative to `root`. Missing repos are cloned, existing repos are pulled (`--ff-only`). Also runs as part of `tectonic apply`. Use `tectonic repos --list` and `tectonic repos --status` for inspection.

## Sync

`tectonic sync` pushes workspace data via rsync. Configured in `configs/sync.yaml`:

- **exclude**: global patterns always excluded (`.DS_Store`, `*.log`, etc.)
- **ignore_files**: per-directory ignore files (`.gitignore`, `.syncignore`) — if present in a sync target directory, patterns inside are also excluded
- **targets**: root directories and path globs to sync

## Deploy

`tectonic deploy` and `tectonic broadcast` run commands on remote hosts via SSH. Before executing, the remote tectonic repo is reset and pulled to ensure the latest code is used.

## Bootstrap Flow

After Layer 0 is complete (Homebrew/apt, 1Password, Tailscale), a new machine only needs:

```bash
# macOS: brew install uv  |  Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
git clone <repo> && cd tectonic
uv run tectonic apply
```

The first `apply` installs packages (including chezmoi), clones declared repos, applies dotfiles, and deploys services (including the `tectonic` wrapper at `~/.local/bin/tectonic`). After that, just `tectonic apply`.
