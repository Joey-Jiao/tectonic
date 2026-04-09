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
uv run tectonic apply
```

## CLI

```
tectonic
│
│ Local (current host only, use deploy/broadcast for remote)
├── apply                           Converge: packages → repos → dotfiles → services
├── packages                        Install packages based on host preset
├── repos                           Clone missing and pull existing repos
│   ├── [--list]                    List declared repos
│   └── [--status]                  Show repo status (missing/dirty/clean)
├── dotfiles                        Apply dotfiles via chezmoi
├── services                        Deploy services, remove stale ones
│   ├── list                        List services with configuration details
│   └── status                      Show runtime status
│
│ Remote
├── * deploy <host> <command...>    Run any tectonic command on a remote host
│   └── [--dry-run]                 Show commands without executing
├── * broadcast <command...>        Run any tectonic command on all remote hosts
│   └── [--dry-run]                 Show commands without executing
│
│ Data
└── sync [host]                     Push workspace data via rsync (default: all hosts)
    ├── [--dry-run]                 Show what would be synced
    └── [--delete]                  Delete files on target not present locally
```

## Modules

Modules are internal to `packages` — not exposed as CLI commands. The host's preset in `hosts.yml` determines which modules run.

| Module | Contents |
|--------|----------|
| `base` | curl, git, vim, neovim, htop, tree, unzip |
| `shell` | zsh, starship, plugins |
| `dev-c` | gcc, cmake, gdb, ninja |
| `dev-python` | uv |
| `dev-node` | Node.js LTS, pnpm |
| `apps-docker` | Docker |

## Docs

- [architecture.md](docs/architecture.md) — layered model, repo layout, apply flow
- [hardware.md](docs/hardware/hardware.md) — machine fleet
- [naming.md](docs/naming.md) — naming conventions
