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

A single `apply` converges the host to the declared state: pulls the repo, installs packages, clones/pulls declared repos, applies dotfiles via chezmoi, and deploys services.

## CLI

```
tectonic
├── apply                           Converge current host to declared state
│   └── [--step packages|repos|dotfiles|services]
│
├── pull [host]                      Pull all repos (default: all hosts)
│   ├── [--list]                    List declared repos
│   └── [--status]                  Show repo status (missing/dirty/clean)
│
├── sync [host]                     Push workspace data to remote hosts via rsync
│   ├── [--dry-run]                 Show what would be synced
│   └── [--delete]                  Delete files on target not present locally
│
├── * deploy <host> <command...>    Execute tectonic command on a remote host
│   └── [--dry-run]                 Show commands without executing
│
├── * broadcast <command...>        Execute tectonic command on all reachable hosts
│   └── [--dry-run]                 Show commands without executing
│
└── services                        Inspect host services
    ├── list                        List services with configuration details
    └── status                      Show runtime status
```

## Modules

Modules are internal to `apply` -- they are not exposed as CLI commands. The host's preset in `hosts.yml` determines which modules run.

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
