#!/usr/bin/env bash
# =============================================================================
# Setup Wizard - Mac & Linux Entry Point
#
# Usage (one-liner for users):
#   curl -sL https://raw.githubusercontent.com/meenusinha/SoftwareTeam/main/setup/setup.sh | bash
#
# What this script does:
#   1. Detects OS (macOS vs Linux distro)
#   2. Checks/installs Python 3
#   3. Downloads the project repo as a tarball
#   4. Extracts it to a temp directory
#   5. Launches the setup wizard (opens in browser)
# =============================================================================

set -e

REPO_OWNER="meenusinha"
REPO_NAME="SoftwareTeam"
REPO_BRANCH="main"
TARBALL_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/archive/refs/heads/${REPO_BRANCH}.tar.gz"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# --- Detect OS ---
detect_os() {
    local uname_s
    uname_s="$(uname -s)"
    case "$uname_s" in
        Darwin*)
            OS="mac"
            info "Detected: macOS $(sw_vers -productVersion 2>/dev/null || echo '')"
            ;;
        Linux*)
            OS="linux"
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                info "Detected: ${NAME} ${VERSION_ID}"
                DISTRO_ID="${ID}"
            else
                info "Detected: Linux"
                DISTRO_ID="linux"
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*)
            # Git Bash / MSYS2 / Cygwin on Windows — this script is for Mac/Linux only.
            error "Detected: Windows ($uname_s)"
            error "This script does not support Windows bash environments (Git Bash, MSYS2, Cygwin)."
            error ""
            error "Please use the PowerShell setup script instead:"
            error "  1. Open PowerShell (not Git Bash)"
            error "  2. Run:  irm https://raw.githubusercontent.com/meenusinha/SoftwareTeam/main/setup/setup.ps1 | iex"
            echo ""
            { read -r _dummy </dev/tty || read -r _dummy; } 2>/dev/null || true
            exit 1
            ;;
        *)
            error "Unsupported OS: $uname_s"
            error "For Windows, use setup.ps1 instead."
            exit 1
            ;;
    esac
}

# --- Timeout command detection (macOS has no built-in 'timeout') ---
_TIMEOUT_CMD=""
if command -v timeout &>/dev/null; then
    _TIMEOUT_CMD="timeout"
elif command -v gtimeout &>/dev/null; then
    _TIMEOUT_CMD="gtimeout"
fi

# Run a command with a timeout, showing output directly to the terminal.
# Usage: run_timed LABEL TIMEOUT_SECS CMD [ARGS...]
# Shows "LABEL (timeout: Xs)..." before running, then streams all output live.
# Piping through tee is intentionally avoided — apt/brew/dnf detect pipes and
# buffer all output until completion, making it look like the script is frozen.
run_timed() {
    local label="$1"
    local timeout_sec="$2"
    shift 2
    local exit_code=0

    info "$label (timeout: ${timeout_sec}s)..."
    if [ -n "$_TIMEOUT_CMD" ]; then
        "$_TIMEOUT_CMD" "$timeout_sec" "$@" || exit_code=$?
    else
        "$@" || exit_code=$?
    fi

    if [ "$exit_code" -eq 124 ]; then
        warn "Timed out after ${timeout_sec}s."
        return 1
    fi
    return "$exit_code"
}

# Verify that a Python command is 3.6 or newer.
# Usage: _verify_python_version <cmd>   returns 0 if OK, 1 if too old or not found
_verify_python_version() {
    local cmd="$1"
    "$cmd" -c "import sys; sys.exit(0 if sys.version_info >= (3,6) else 1)" 2>/dev/null
}

# --- Check/Install Python 3 ---
ensure_python() {
    # Check for python3 first — most reliable name for Python 3
    if command -v python3 &>/dev/null; then
        if _verify_python_version python3; then
            PYTHON="python3"
            ok "Python 3 found: $(python3 --version)"
            return
        else
            warn "python3 found but is $(python3 --version 2>&1) — need 3.6+ (f-strings require 3.6; 3.5 is also end-of-life since 2020). Will install a newer version."
        fi
    fi

    # Check for python (might be Python 3 on some systems)
    if command -v python &>/dev/null; then
        PY_VER=$(python --version 2>&1)
        if echo "$PY_VER" | grep -q "Python 3" && _verify_python_version python; then
            PYTHON="python"
            ok "Python 3 found: $PY_VER"
            return
        fi
        # python is Python 2 (or too old Python 3) — don't use it
        warn "Found '$(python --version 2>&1)' but Python 3.6+ is required (f-strings were added in 3.6; Python 3.5 is end-of-life)."
    fi

    warn "Python 3.6+ is required but was not found on this system."
    echo ""
    # Read from /dev/tty so the prompt works even when stdin is a pipe (curl | bash)
    if [ -e /dev/tty ]; then
        { read -r -p "May we install Python 3 automatically? [y/N] " _py_answer </dev/tty; } || true
    else
        { read -r -p "May we install Python 3 automatically? [y/N] " _py_answer; } || true
    fi
    case "$_py_answer" in
        [yY]|[yY][eE][sS]) ;;
        *)
            error "Python 3 is required to run the setup wizard."
            error "Please install Python 3.6+ from https://python.org and run this script again."
            exit 1
            ;;
    esac
    info "Installing Python 3..."
    local py_installed=false

    if [ "$OS" = "mac" ]; then
        # --- Method 1: Homebrew (if already installed) ---
        if command -v brew &>/dev/null; then
            if run_timed "Installing Python 3 via Homebrew" 120 brew install python3; then
                py_installed=true
            fi
        fi

        # --- Method 2: Install Homebrew first, then Python ---
        if [ "$py_installed" = false ]; then
            info "Homebrew not found. Installing Homebrew first..."
            NONINTERACTIVE=1 /bin/bash -c \
                "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            # Add brew to PATH for this session
            if [ -f /opt/homebrew/bin/brew ]; then
                eval "$(/opt/homebrew/bin/brew shellenv)"
            elif [ -f /usr/local/bin/brew ]; then
                eval "$(/usr/local/bin/brew shellenv)"
            fi
            if run_timed "Installing Python 3 via Homebrew" 120 brew install python3; then
                py_installed=true
            fi
        fi

    elif [ "$OS" = "linux" ]; then
        if command -v apt &>/dev/null; then
            run_timed "Updating package lists" 60 sudo apt update -qq || true
            if run_timed "Installing Python 3 via apt" 120 sudo apt install -y python3; then
                py_installed=true
            fi
        elif command -v dnf &>/dev/null; then
            if run_timed "Installing Python 3 via dnf" 120 sudo dnf install -y python3; then
                py_installed=true
            fi
        elif command -v pacman &>/dev/null; then
            if run_timed "Installing Python 3 via pacman" 120 sudo pacman -S --noconfirm python; then
                py_installed=true
            fi
        elif command -v zypper &>/dev/null; then
            if run_timed "Installing Python 3 via zypper" 120 sudo zypper install -y python3; then
                py_installed=true
            fi
        fi
    fi

    # --- Fallback: pyenv (works on both mac and linux, compiles from source) ---
    if [ "$py_installed" = false ]; then
        info "Trying pyenv as fallback (may take a few minutes — compiles Python from source)..."
        if ! command -v pyenv &>/dev/null; then
            run_timed "Installing pyenv" 120 bash -c \
                "curl -fsSL https://pyenv.run | bash" || true
            export PYENV_ROOT="$HOME/.pyenv"
            export PATH="$PYENV_ROOT/bin:$PATH"
            eval "$(pyenv init - 2>/dev/null)" || true
        fi
        if command -v pyenv &>/dev/null; then
            if run_timed "Installing Python 3.12 via pyenv" 600 pyenv install -s 3.12.0; then
                pyenv global 3.12.0 2>/dev/null || true
                PYTHON="$(pyenv which python 2>/dev/null || echo python3)"
                ok "Python 3 installed via pyenv."
                return
            fi
        fi
        error "All automatic Python installation methods failed."
        error "Check your internet connection and try running this script again."
        exit 1
    fi

    # Verify installation
    if command -v python3 &>/dev/null; then
        PYTHON="python3"
        ok "Python 3 installed: $(python3 --version)"
    else
        error "Python 3 installation could not be verified. Check your internet connection and try again."
        exit 1
    fi
}

# --- Download repo tarball ---
download_repo() {
    TEMP_DIR=$(mktemp -d)
    info "Downloading project files..."

    if command -v curl &>/dev/null; then
        curl -sL "$TARBALL_URL" | tar -xz -C "$TEMP_DIR"
    elif command -v wget &>/dev/null; then
        wget -qO- "$TARBALL_URL" | tar -xz -C "$TEMP_DIR"
    else
        error "Neither curl nor wget found. Please install one of them."
        exit 1
    fi

    # The tarball extracts to a directory like SoftwareTeam-main/
    # Find the extracted directory
    REPO_DIR=$(find "$TEMP_DIR" -maxdepth 1 -type d -name "${REPO_NAME}*" | head -1)

    if [ -z "$REPO_DIR" ] || [ ! -d "$REPO_DIR" ]; then
        error "Failed to download project files."
        rm -rf "$TEMP_DIR"
        exit 1
    fi

    ok "Project files downloaded to temporary directory."

    # Export so the wizard can find the full repo for local copy mode
    export WIZARD_REPO_PATH="$REPO_DIR"

    # Export the user's original working directory as a default project path
    export WIZARD_USER_CWD="$(pwd)"
}

# --- Launch wizard ---
launch_wizard() {
    info "Starting setup wizard..."
    echo ""
    echo "============================================"
    echo "  The wizard will open in your browser."
    echo "  If it doesn't open automatically,"
    echo "  look for the URL printed below."
    echo "============================================"
    echo ""

    # Final safety check — if $PYTHON is Python 2 or too old, try harder before giving up
    if ! _verify_python_version "$PYTHON"; then
        warn "'$PYTHON' is $(${PYTHON} --version 2>&1) — not Python 3.6+. Searching for a usable Python 3..."

        # Try explicit python3 variants first (may have just been installed but $PYTHON wasn't updated)
        for _p3 in python3 python3.12 python3.11 python3.10 python3.9 python3.8; do
            if command -v "$_p3" &>/dev/null && _verify_python_version "$_p3"; then
                PYTHON="$_p3"
                ok "Found usable Python 3: $($PYTHON --version)"
                break
            fi
        done

        # Still not Python 3? Ask the user before installing
        if ! _verify_python_version "$PYTHON"; then
            echo ""
            if [ -e /dev/tty ]; then
                { read -r -p "No Python 3.6+ found. May we install it automatically? [y/N] " _py_answer2 </dev/tty; } || true
            else
                { read -r -p "No Python 3.6+ found. May we install it automatically? [y/N] " _py_answer2; } || true
            fi
            case "$_py_answer2" in
                [yY]|[yY][eE][sS])
                    ensure_python
                    ;;
                *)
                    error "Python 3 is required. Please install Python 3.6+ from https://python.org"
                    exit 1
                    ;;
            esac
        fi

        # Last resort — if still wrong, give a clear error
        if ! _verify_python_version "$PYTHON"; then
            error "Python 3.6+ could not be installed automatically."
            error "Please install Python 3 manually from https://python.org"
            error "Then run this script again."
            exit 1
        fi
    fi

    # Run the wizard (run script directly to avoid 'setup' package name conflicts)
    PYTHONPATH="$REPO_DIR" "$PYTHON" "$REPO_DIR/setup/wizard/main.py"

    # Cleanup temp directory when done
    info "Cleaning up temporary files..."
    rm -rf "$TEMP_DIR"
    ok "Done!"
}

# --- Main ---
main() {
    echo ""
    echo "==============================="
    echo "  Project Setup Wizard"
    echo "==============================="
    echo ""

    detect_os
    ensure_python
    download_repo
    launch_wizard
}

main
