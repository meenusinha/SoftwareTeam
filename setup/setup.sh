#!/usr/bin/env bash
# =============================================================================
# Setup Wizard - Mac & Linux Entry Point
#
# Usage (one-liner for users):
#   curl -sL https://raw.githubusercontent.com/meenusinha/SoftwareTeam/template/agentic-workflow-gui/setup/setup.sh | bash
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
REPO_BRANCH="template/agentic-workflow-gui"
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
    case "$(uname -s)" in
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
        *)
            error "Unsupported OS: $(uname -s)"
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

# Run a command with a timeout, streaming its output live and capturing to a log.
# Usage: run_timed LABEL TIMEOUT_SECS CMD [ARGS...]
# Shows "LABEL (timeout: Xs)..." before running.
# On failure or timeout, prints the last 15 lines of the output log.
# Returns 0 on success, non-zero on failure or timeout.
run_timed() {
    local label="$1"
    local timeout_sec="$2"
    shift 2
    local logfile
    logfile=$(mktemp)

    info "$label (timeout: ${timeout_sec}s)..."
    if [ -n "$_TIMEOUT_CMD" ]; then
        $_TIMEOUT_CMD "$timeout_sec" "$@" 2>&1 | tee "$logfile"
        local exit_code=${PIPESTATUS[0]}
    else
        "$@" 2>&1 | tee "$logfile"
        local exit_code=${PIPESTATUS[0]}
    fi

    if [ "$exit_code" -eq 0 ]; then
        rm -f "$logfile"
        return 0
    elif [ "$exit_code" -eq 124 ]; then
        warn "Timed out after ${timeout_sec}s. Output log (last 15 lines):"
        tail -15 "$logfile"
    else
        warn "Failed (exit code: $exit_code). Output log (last 15 lines):"
        tail -15 "$logfile"
    fi
    rm -f "$logfile"
    return 1
}

# --- Check/Install Python 3 ---
ensure_python() {
    # Check for python3
    if command -v python3 &>/dev/null; then
        PYTHON="python3"
        ok "Python 3 found: $(python3 --version)"
        return
    fi

    # Check for python (might be Python 3)
    if command -v python &>/dev/null; then
        PY_VER=$(python --version 2>&1)
        if echo "$PY_VER" | grep -q "Python 3"; then
            PYTHON="python"
            ok "Python 3 found: $PY_VER"
            return
        fi
    fi

    warn "Python 3 not found. Installing automatically..."
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

    # The tarball extracts to a directory like SoftwareTeam-template-agentic-workflow-gui/
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

    # Run the wizard (run script directly to avoid 'setup' package name conflicts)
    PYTHONPATH="$REPO_DIR" $PYTHON "$REPO_DIR/setup/wizard/main.py"

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
