#!/bin/bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RESET='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/bootstrap.log"

log_info()  { printf "${GREEN}[INFO]${RESET} %s\n" "$*"; }
log_warn()  { printf "${YELLOW}[WARN]${RESET} %s\n" "$*"; }
log_error() { printf "${RED}[ERROR]${RESET} %s\n" "$*" >&2; }

# Run command silently, redirect output to log file
run() {
    "$@" >> "$LOG_FILE" 2>&1
}

command_exists() {
    command -v "$1" &>/dev/null
}

detect_pkg_mgr() {
    if command_exists brew; then
        echo "brew"
    elif command_exists apt; then
        echo "apt"
    elif command_exists pacman; then
        echo "pacman"
    elif command_exists dnf; then
        echo "dnf"
    else
        echo ""
    fi
}

install_homebrew() {
    if command_exists brew; then
        log_info "Homebrew is already installed"
        return 0
    fi

    log_info "Installing Homebrew..."
    NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" >> "$LOG_FILE" 2>&1

    if [[ -x /opt/homebrew/bin/brew ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [[ -x /usr/local/bin/brew ]]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi

    if command_exists brew; then
        log_info "Homebrew installed successfully"
    else
        log_error "Failed to install Homebrew"
        exit 1
    fi
}

install_prerequisites_linux() {
    local pkg_mgr
    pkg_mgr="$(detect_pkg_mgr)"

    if [[ -z "$pkg_mgr" ]]; then
        log_error "Unsupported package manager"
        exit 1
    fi

    log_info "Detected package manager: $pkg_mgr"

    local packages=()
    case "$pkg_mgr" in
        apt)
            log_info "Updating apt cache..."
            run sudo apt update
            packages=(curl git python3 python3-venv)
            ;;
        pacman)
            log_info "Updating pacman cache..."
            run sudo pacman -Sy
            packages=(curl git python)
            ;;
        dnf)
            packages=(curl git python3)
            ;;
    esac

    log_info "Installing prerequisites: ${packages[*]}"
    case "$pkg_mgr" in
        apt)    run sudo apt install -y "${packages[@]}" ;;
        pacman) run sudo pacman -S --noconfirm --needed "${packages[@]}" ;;
        dnf)    run sudo dnf install -y "${packages[@]}" ;;
    esac
}

install_prerequisites_macos() {
    install_homebrew

    log_info "Installing prerequisites via Homebrew..."
    run brew install git python3 uv
}

install_uv_linux() {
    if command_exists uv; then
        log_info "uv is already installed"
        return 0
    fi

    local pkg_mgr
    pkg_mgr="$(detect_pkg_mgr)"

    case "$pkg_mgr" in
        pacman)
            log_info "Installing uv via pacman..."
            run sudo pacman -S --noconfirm --needed uv
            ;;
        *)
            log_info "Installing uv via install script..."
            run curl -LsSf https://astral.sh/uv/install.sh -o /tmp/uv-install.sh
            run sh /tmp/uv-install.sh
            rm -f /tmp/uv-install.sh
            export PATH="$HOME/.local/bin:$PATH"
            ;;
    esac

    if command_exists uv; then
        log_info "uv installed successfully"
    else
        log_error "Failed to install uv"
        exit 1
    fi
}

main() {
    mkdir -p "$(dirname "$LOG_FILE")"
    rm -f "$LOG_FILE"

    log_info "Bootstrap: Installing prerequisites..."

    case "$(uname)" in
        Darwin)
            install_prerequisites_macos
            ;;
        Linux)
            install_prerequisites_linux
            install_uv_linux
            ;;
        *)
            log_error "Unsupported OS: $(uname)"
            exit 1
            ;;
    esac

    log_info "Bootstrap complete!"
    echo ""
    echo "Run the following command to continue:"
    echo ""
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\" && uv run lxs"
}

main "$@"
