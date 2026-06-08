# Architecture

tectonic is a single-machine environment bootstrap tool. The same repository works on any machine you clone it to — run `tectonic apply` and the machine converges to its declared state. tectonic does not manage cross-host state.

## Layers

```
Layer 2: Configuration   chezmoi (dotfiles, MCP client config)
Layer 1: Software        tectonic CLI (packages, tools)
Layer 0: Infrastructure  1Password + Tailscale + Homebrew/apt
```

Each layer has a single owner and a clear boundary:

| Layer | Owner | Manages | Depends On |
|-------|-------|---------|------------|
| 0 — Infrastructure | 1Password, Tailscale, Homebrew/apt | Identity, secrets, network, package manager | bare OS |
| 1 — Software | tectonic CLI (`src/tectonic/`) | OS packages, cloned tool sources, CLI wrappers in `~/.local/bin/` | Layer 0 |
| 2 — Configuration | chezmoi (`home/`) | Dotfiles, MCP client config, anything else in `$HOME` | Layer 1 |

## Scope

tectonic does **not** manage:

- **Daemon lifecycle** (launchd, systemd) — use chezmoi-managed plists if needed, or `launchctl`/`systemctl` directly
- **Cross-host data sync** — single-machine model; copy files between machines manually when needed
- **Remote command execution** — `ssh` directly when needed
- **Project repositories** — `project/*`, `site/*`, etc. are cloned and updated manually; tectonic manages only the infra tools declared in `tools.yaml`
- **Aggressive code updates** — `tectonic tools` does `git pull --ff-only`; uncommitted changes or diverged branches are skipped with a warning, never destroyed

Multi-machine support is limited to "the same configs work on any machine you clone the repo to."

## Repository Layout

```
tectonic/
├── configs/                  # Externalized configuration
│   ├── hosts.yaml            # Machine registry and presets
│   ├── packages/             # Per-module package lists (YAML)
│   ├── tools.yaml            # Tool definitions (repo + path)
│   └── urls.yaml             # External installer URLs
├── home/                     # chezmoi source directory (Layer 2)
│   ├── .chezmoidata/         # symlinks to configs/ for chezmoi template data
│   ├── dot_zshenv
│   ├── dot_claude/           # Claude Code config (CLAUDE.md, mcp.json, settings.json)
│   ├── dot_config/
│   └── run_onchange_*.sh     # chezmoi-triggered scripts (e.g. MCP registration)
├── src/tectonic/             # Python environment manager (Layer 1)
│   ├── config.py
│   ├── base/                 # ConfigService (reads configs/ YAML)
│   ├── cli/
│   │   ├── __init__.py       # App definition and command registration
│   │   ├── apply.py          # Orchestration (packages → dotfiles → tools)
│   │   ├── packages.py
│   │   ├── dotfiles.py
│   │   └── tools.py
│   ├── core/
│   │   ├── distro.py
│   │   ├── fs.py
│   │   ├── host.py
│   │   ├── process.py
│   │   ├── tools.py
│   │   └── ui.py
│   └── modules/              # Internal install modules
├── docs/
├── tests/
└── pyproject.toml
```

## hosts.yaml

The machine registry. Each host declares a preset (a named set of modules) and optional extras. `tectonic apply` reads the current hostname, looks it up in `hosts.yaml`, and converges to the declared state.

```yaml
presets:
  workstation: [base, shell, dev-c, dev-python, dev-node]
  server: [base, shell, dev-python, dev-node]
  hpc: [shell-hpc]

hosts:
  blanc:
    preset: workstation
    user: blank
    ssh_host: blanc
  campbell:
    preset: server
    user: blank
    ssh_host: campbell
  pioneer:
    preset: hpc
    user: axj770
    ssh_host: pioneer.case.edu
    aliases: [hpc5, hpc6, hpc7, hpc8, hpctransfer1]
    hpc:
      scratch: /scratch/pioneer/users/axj770
      lmod_pkg: /usr/local/lmod/lmod
      modules: [GCCcore/13.2.0, git/2.42.0-GCCcore-13.2.0, Python/3.11.5-GCCcore-13.2.0]
```

`user` and `ssh_host` are not consumed by the CLI (single-machine model) — they document where the host lives. `aliases` lets host resolution match alternative hostnames; `hpc:` is read by the `shell-hpc` module.

## Module System

Each module is a Python file with a `run()` entry point, registered in `modules/__init__.py`. Modules are internal to the `packages` step — they are not exposed as CLI commands.

| Module | Path | Contents |
|--------|------|----------|
| `base` | `modules/base.py` | curl, git, vim, neovim, htop, tree, unzip |
| `shell` | `modules/shell.py` | zsh, starship, plugins |
| `dev-c` | `modules/dev/c.py` | gcc, cmake, gdb, ninja |
| `dev-python` | `modules/dev/python.py` | uv |
| `dev-node` | `modules/dev/node.py` | Node.js LTS |
| `apps-docker` | `modules/apps/docker.py` | Docker |
| `shell-hpc` | `modules/shell_hpc.py` | HPC environment (lmod-based shell) |

## Apply Pipeline

`tectonic apply` converges the current host to its declared state by running three steps in order:

```
1. packages    resolve host preset → run matching modules
2. dotfiles    chezmoi apply --source home/ --force
3. tools       clone-or-ff-pull sources, install ~/.local/bin/ wrappers
```

Order matters: `dotfiles` adds `~/.local/bin/` to `PATH` (via zshenv), so the wrappers `tools` writes are immediately usable in new shells.

Each step is idempotent and available as a standalone command.

## CLI

| Command | Behavior |
|---------|----------|
| `tectonic apply` | Converge current host (packages → dotfiles → tools) |
| `tectonic packages` | Install packages based on host preset |
| `tectonic dotfiles` | Apply dotfiles via chezmoi |
| `tectonic tools` | Clone-or-pull tool sources, install/update wrappers |
| `tectonic tools --list` | List declared tools |
| `tectonic tools --status` | Show source state (missing/dirty/clean) + wrapper state (missing/stale/ok) |

There is no `services`, `sync`, `deploy`, `broadcast`, or `preset` command. By design.

## Tools

`tectonic tools` manages CLI tools declared in `configs/tools.yaml`:

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

For each tool:

1. **Source.** If `<root>/<path>` is missing, clone from `repo`. If present, attempt `git pull --ff-only`. On uncommitted changes or diverged branches, skip with a warning — local work is never destroyed.
2. **Wrapper.** Write `~/.local/bin/<name>` as `exec uv run --project <root>/<path> <name> "$@"`. If the file exists with identical content, skip.

`tectonic` is declared as a tool, so the first apply installs its own wrapper. Tools removed from `tools.yaml` are **not** auto-cleaned — remove the wrapper yourself (`rm ~/.local/bin/<name>`).

## Bootstrap Flow

After Layer 0 is complete (Homebrew/apt, 1Password, Tailscale), a new machine needs:

```bash
# macOS: brew install uv  |  Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
git clone <repo> ~/workspace/infra/tectonic
cd ~/workspace/infra/tectonic && uv run tectonic apply
```

The first apply:

1. Installs OS packages for the host preset
2. Applies dotfiles (which puts `~/.local/bin/` on PATH)
3. Clones the remaining tool sources and writes all wrappers (including `~/.local/bin/tectonic`)

After that, open a new shell. The entire daily interface is:

```bash
tectonic apply
```
