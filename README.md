# Tectonic

Multi-host environment provisioning and management for macOS and Linux.

## Layers

```
Layer 4: Services        launchd/systemd
Layer 3: Data            Syncthing
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

```bash
tectonic install          # detect hostname, install matching modules
tectonic install <module> # install a single module
tectonic install --list   # list available modules
```

## Modules

| Module | Contents |
|--------|----------|
| `base` | curl, git, vim, neovim, htop, tree, unzip |
| `shell` | zsh, starship, plugins |
| `dev-c` | gcc, cmake, gdb, ninja |
| `dev-python` | uv |
| `dev-node` | Node.js LTS, pnpm |
| `syncthing` | Syncthing |
| `apps-docker` | Docker |

## Docs

- [architecture.md](docs/architecture.md) — layered model, repo layout, module system
- [hardware.md](docs/hardware/hardware.md) — machine fleet
- [naming.md](docs/naming.md) — naming conventions
