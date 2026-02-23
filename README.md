# Tectonic: automated env setup

Personal macOS/Linux environment setup tool. Installs dev tools, configures shell, and manages dotfiles.

## Usage

```bash
# Bootstrap (installs uv, git, python)
./bootstrap.sh

# Install everything
uv run tectonic install

# Install a specific module
uv run tectonic install base

# List available modules
uv run tectonic install --list

# Manage dotfiles
uv run tectonic dotfiles status    # Check drift
uv run tectonic dotfiles diff      # Show differences
uv run tectonic dotfiles sync      # Sync repo -> system

# List installed plugins
uv run tectonic plugins
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
