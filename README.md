# Tectonic

Multi-host environment provisioning and management for macOS and Linux.

## Layers

```
Layer 4: Services        launchd/systemd + command wrappers
Layer 3: Data            rsync over Tailscale
Layer 2: Configuration   chezmoi
Layer 1: Software        tectonic CLI
Layer 0: Infrastructure  1Password + Tailscale
```

See [architecture.md](docs/architecture.md) for details.

## Quick Start

After Layer 0 is in place (Homebrew/apt, 1Password, Tailscale):

```bash
brew install uv          # or: curl -LsSf https://astral.sh/uv/install.sh | sh
git clone <repo> && cd tectonic
uv run tectonic install
chezmoi init --source ~/workspace/infra/tectonic/home --apply
```

## CLI

```
tectonic
├── * deploy <host> <command...>     Execute tectonic command on a remote host
│   └── [--dry-run]                  Show commands without executing
│
├── * broadcast <command...>         Execute tectonic command on all reachable hosts
│   └── [--dry-run]                  Show commands without executing
│
├── install                          Detect hostname, install matching modules
│   ├── all                          Install every registered module
│   ├── module <name>                Install a single module by name
│   └── list                         List available modules
│
├── sync [host]                      Push workspace data to remote hosts via rsync
│   ├── [--dry-run]                  Show what would be synced
│   └── [--delete]                   Delete files on target not present locally
│
└── services                         Deploy all services for current host
    ├── list                         List services with configuration details
    ├── status                       Show runtime status
    ├── load <name>                  Install and load a service
    └── unload <name>               Unload and remove a service
```

## Modules

| Module | Contents |
|--------|----------|
| `base` | curl, git, vim, neovim, htop, tree, unzip |
| `shell` | zsh, starship, plugins |
| `dev-c` | gcc, cmake, gdb, ninja |
| `dev-python` | uv |
| `dev-node` | Node.js LTS, pnpm |
| `apps-docker` | Docker |

## Docs

- [architecture.md](docs/architecture.md) — layered model, repo layout, module system
- [hardware.md](docs/hardware/hardware.md) — machine fleet
- [naming.md](docs/naming.md) — naming conventions
