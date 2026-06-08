# Tectonic

Single-machine environment bootstrap for macOS and Linux. One command brings any machine to a declared state.

## Layers

```
Layer 2: Configuration   chezmoi (dotfiles, MCP client config)
Layer 1: Software        tectonic CLI (packages, tools)
Layer 0: Infrastructure  1Password + Tailscale + Homebrew/apt
```

See [architecture.md](docs/architecture.md) for details.

## Scope

tectonic is single-machine by design. The same configs work on any machine you clone the repo to, but tectonic does not manage cross-host state — no daemon lifecycle, no cross-host sync, no remote execution.

## Quick Start

After Layer 0 is in place (Homebrew/apt, 1Password, Tailscale):

```bash
brew install uv          # or: curl -LsSf https://astral.sh/uv/install.sh | sh
git clone <repo> ~/workspace/infra/tectonic
cd ~/workspace/infra/tectonic && uv run tectonic apply
```

After the first apply, the `tectonic` wrapper lives in `~/.local/bin/`. Subsequent runs:

```bash
tectonic apply
```

## CLI

```
tectonic
├── apply                Converge: packages → dotfiles → tools
├── packages             Install packages based on host preset
├── dotfiles             Apply dotfiles via chezmoi
└── tools                Clone-or-pull tool sources + install ~/.local/bin/ wrappers
    ├── [--list]         List declared tools
    └── [--status]       Show source + wrapper status
```

## Modules

Modules are internal to `packages` — not exposed as CLI commands. The host's preset in `hosts.yaml` determines which modules run.

| Module | Contents |
|--------|----------|
| `base` | curl, git, vim, neovim, htop, tree, unzip |
| `shell` | zsh, starship, plugins |
| `dev-c` | gcc, cmake, gdb, ninja |
| `dev-python` | uv |
| `dev-node` | Node.js LTS, pnpm |
| `apps-docker` | Docker |
| `shell-hpc` | HPC environment (lmod-based shell) |

## Tools

Tools are CLI commands installed as wrappers in `~/.local/bin/`. Each tool declares a source repo and a path under `root`. `tectonic tools` clones missing sources, fast-forward-pulls existing ones (skipping safely on uncommitted changes), and installs/updates the wrapper.

Declared in `configs/tools.yaml`:

```yaml
root: ~/workspace
tools:
  tectonic:
    repo: git@github.com:Joey-Jiao/tectonic.git
    path: infra/tectonic
  strata:
    repo: git@github.com:Joey-Jiao/strata.git
    path: infra/strata
```

## Docs

- [architecture.md](docs/architecture.md) — layered model, repo layout, apply flow
- [naming.md](docs/naming.md) — naming conventions
- [hardware.md](docs/hardware/hardware.md) — machine fleet
