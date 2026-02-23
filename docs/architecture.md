# Architecture

tectonic is a single repository for all environment-related concerns across multiple machines. The system is organized into five layers, each building on the ones below it.

## Layers

```
Layer 4: Services        launchd/systemd (MCP server, long-running processes)
Layer 3: Data            Syncthing (workspace, misc, archive)
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
| 3 — Data | Syncthing | User data (code, documents, archives) | Layer 0 |
| 4 — Services | launchd / systemd | Long-running processes | Layer 0-2 |

Layer 3 (Data) and Layers 1-2 (Software, Configuration) are independent of each other — both only require Layer 0. Services at Layer 4 typically need software installed and configured before they can run.

## Repository Layout

```
tectonic/
├── configs/                  # Externalized configuration (packages, URLs, host registry)
│   ├── hosts.yml             # Machine registry and desired state
│   ├── packages/             # Per-module package lists (YAML)
│   ├── urls.yaml
│   └── syncignore
├── home/                     # chezmoi source directory (Layer 2)
│   ├── .chezmoidata/          # symlinks to configs/ for chezmoi template data
│   ├── dot_zshenv
│   ├── dot_config/
│   │   ├── zsh/
│   │   ├── git/
│   │   ├── starship.toml
│   │   └── 1Password/ssh/
│   └── dot_ssh/
├── src/tectonic/             # Python environment manager (Layer 1)
│   ├── cli.py
│   ├── config.py
│   ├── base/                 # ConfigService (reads configs/ YAML)
│   ├── core/
│   │   ├── distro.py
│   │   ├── process.py
│   │   ├── fs.py
│   │   ├── host.py
│   │   └── ui.py
│   └── modules/
│       ├── __init__.py       # Module registry
│       ├── base.py
│       ├── shell.py
│       ├── syncthing.py
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

The machine registry (`configs/hosts.yml`). Each host declares a preset (a named set of modules) and optional extra modules. The tectonic CLI reads the current hostname, looks it up in `hosts.yml`, and installs the corresponding modules.

```yaml
presets:
  workstation: [base, shell, syncthing, dev-c, dev-python, dev-node]
  server: [base, shell, syncthing, dev-python]

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

Each module is a Python file with a `run()` entry point, registered in `modules/__init__.py`.

| Module | Path | Contents |
|--------|------|----------|
| `base` | `modules/base.py` | curl, git, vim, neovim, htop, tree, unzip |
| `shell` | `modules/shell.py` | zsh, starship, plugins, dotfiles |
| `dev-c` | `modules/dev/c.py` | gcc, cmake, gdb, ninja |
| `dev-python` | `modules/dev/python.py` | uv (Python version management + venv + package install) |
| `dev-node` | `modules/dev/node.py` | Node.js LTS via package manager |
| `syncthing` | `modules/syncthing.py` | Syncthing |
| `apps-docker` | `modules/apps/docker.py` | Docker |

## CLI

| Command | Behavior |
|---------|----------|
| `tectonic install` | Detect hostname, look up preset in hosts.yml, install matching modules |
| `tectonic install all` | Install every registered module |
| `tectonic install <module>` | Install a single module by name |
| `tectonic install --list` | List available modules |

## Bootstrap Flow

After Layer 0 is complete (Homebrew/apt, 1Password, Tailscale), a new machine only needs:

```bash
# macOS: brew install uv  |  Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
git clone <repo> && cd tectonic && uv run tectonic install
chezmoi init --source ~/workspace/infra/tectonic/home --apply
```

Then as needed: Syncthing pairing (Layer 3, manual one-time), launchd/systemd services (Layer 4).
