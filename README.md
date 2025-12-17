# LXS: automated env setup

Personal Linux/macOS environment setup tool. Installs dev tools, configures shell, and manages dotfiles.

## Usage

```bash
# Bootstrap (installs uv, git, python)
./bootstrap.sh

# Install everything
uv run lxs install all

# Manage dotfiles
uv run lxs dotfiles status    # Check drift
uv run lxs dotfiles diff      # Show differences
uv run lxs dotfiles sync      # Sync repo -> system

# List installed plugins
uv run lxs plugins
```

## What gets installed

- **base**: curl, git, vim, neovim, htop, tree
- **shell**: zsh, starship, plugins (autosuggestions, syntax-highlighting, completions)
- **dev-c**: gcc, cmake, gdb, ninja
- **dev-python**: miniforge (conda & mamba)
- **dev-node**: nvm + node.js LTS
- **apps-docker**: Docker

## Supported platforms

- macOS (Homebrew)
- Ubuntu/Debian (apt)
- Arch Linux (pacman)
- Fedora (dnf)
