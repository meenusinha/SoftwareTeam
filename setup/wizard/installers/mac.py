"""macOS-specific installation logic."""

import os

from setup.wizard.utils.shell import run, launch, is_installed


def _find_vscode_cmd():
    """Find the VS Code CLI command on macOS.

    Returns a command string for running 'code' CLI, or None.
    Checks PATH first, then the embedded CLI inside the .app bundle.
    """
    if is_installed("code"):
        return "code"
    # VS Code .app embeds a CLI at this path
    app_cli = "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
    if os.path.isfile(app_cli):
        return app_cli
    return None


def install_homebrew():
    """Install Homebrew if not present."""
    if is_installed("brew"):
        return {"success": True, "message": "Homebrew is already installed", "skipped": True}

    result = run(
        '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        timeout=300,
    )
    if result["success"]:
        return {"success": True, "message": "Homebrew installed successfully"}
    return {"success": False, "message": "Failed to install Homebrew.", "error_log": result["stderr"] or result["stdout"]}


def install_git():
    """Install git via Homebrew or xcode-select."""
    if is_installed("git"):
        return {"success": True, "message": "Git is already installed", "skipped": True}

    # Try xcode-select first (doesn't need brew)
    result = run("xcode-select --install", timeout=300)
    if result["success"]:
        return {"success": True, "message": "Git installed via Xcode Command Line Tools"}

    # Fallback to brew
    if is_installed("brew"):
        result = run("brew install git", timeout=120)
        if result["success"]:
            return {"success": True, "message": "Git installed via Homebrew"}

    return {"success": False, "message": "Failed to install git automatically."}


def install_gh():
    """Install GitHub CLI via Homebrew."""
    if is_installed("gh"):
        return {"success": True, "message": "GitHub CLI is already installed", "skipped": True}

    if not is_installed("brew"):
        brew_result = install_homebrew()
        if not brew_result["success"]:
            return {"success": False, "message": "Cannot install gh: Homebrew is required"}

    result = run("brew install gh", timeout=120)
    if result["success"]:
        return {"success": True, "message": "GitHub CLI installed via Homebrew"}
    return {"success": False, "message": "Failed to install GitHub CLI via Homebrew.", "error_log": result["stderr"] or result["stdout"]}


def check_ai_tool(tool):
    """Check if an AI tool is already installed on macOS.

    Returns dict with 'installed' (bool) and 'message'.
    """
    checks = {
        "cursor": lambda: is_installed("cursor") or _app_exists("Cursor"),
        "windsurf": lambda: is_installed("windsurf") or _app_exists("Windsurf"),
        "claude-code": lambda: is_installed("claude"),
        "vscode": lambda: is_installed("code") or _app_exists("Visual Studio Code"),
        "copilot": lambda: is_installed("code") or _app_exists("Visual Studio Code"),
        "aider": lambda: is_installed("aider"),
    }
    checker = checks.get(tool)
    if not checker:
        return {"installed": False, "message": f"Unknown tool: {tool}"}
    found = checker()
    return {
        "installed": found,
        "message": f"{tool} is already installed" if found else f"{tool} is not installed",
    }


def _app_exists(name):
    """Check if a macOS .app bundle exists in /Applications."""
    import os
    return os.path.isdir(f"/Applications/{name}.app")


def install_ai_tool(tool):
    """Install an AI tool on macOS.

    Args:
        tool: One of 'cursor', 'windsurf', 'claude-code', 'vscode', 'aider'
    """
    # Skip if already installed
    status = check_ai_tool(tool)
    if status["installed"]:
        return {"success": True, "message": status["message"], "skipped": True}

    installers = {
        "cursor": _install_cursor,
        "windsurf": _install_windsurf,
        "claude-code": _install_claude_code,
        "vscode": _install_vscode,
        "copilot": _install_copilot,
        "aider": _install_aider,
    }
    installer = installers.get(tool)
    if not installer:
        return {"success": False, "message": f"Unknown tool: {tool}"}
    return installer()


def _install_cursor():
    if not is_installed("brew"):
        brew = install_homebrew()
        if not brew["success"]:
            return {"success": False, "message": "Homebrew is required for Cursor and could not be installed.", "error_log": brew.get("error_log", "")}
    result = run("brew install --cask cursor", timeout=300)
    if result["success"]:
        return {"success": True, "message": "Cursor installed successfully"}
    return {"success": False, "message": "Failed to install Cursor via Homebrew.", "error_log": result["stderr"] or result["stdout"]}


def _install_windsurf():
    if not is_installed("brew"):
        brew = install_homebrew()
        if not brew["success"]:
            return {"success": False, "message": "Homebrew is required for Windsurf and could not be installed.", "error_log": brew.get("error_log", "")}
    result = run("brew install --cask windsurf", timeout=300)
    if result["success"]:
        return {"success": True, "message": "Windsurf installed successfully"}
    return {"success": False, "message": "Failed to install Windsurf via Homebrew.", "error_log": result["stderr"] or result["stdout"]}


def _install_claude_code():
    if not is_installed("npm"):
        if is_installed("brew"):
            node_result = run("brew install node", timeout=120)
            if not node_result["success"]:
                return {"success": False, "message": "Failed to install Node.js (required for Claude Code).",
                        "error_log": node_result["stderr"] or node_result["stdout"]}
        else:
            return {"success": False, "message": "Homebrew not found — cannot install Node.js for Claude Code.",
                    "error_log": "brew not in PATH"}

    result = run("npm install -g @anthropic-ai/claude-code", timeout=120)
    if result["success"]:
        return {"success": True, "message": "Claude Code installed successfully"}
    return {"success": False, "message": "Failed to install Claude Code via npm.", "error_log": result["stderr"] or result["stdout"]}


def _install_vscode():
    if not is_installed("brew"):
        brew = install_homebrew()
        if not brew["success"]:
            return {"success": False, "message": "Homebrew is required for VS Code and could not be installed.", "error_log": brew.get("error_log", "")}
    result = run("brew install --cask visual-studio-code", timeout=300)
    if result["success"]:
        vscode_cmd = _find_vscode_cmd() or "code"
        run(f'"{vscode_cmd}" --install-extension continue.continue', timeout=60)
        return {"success": True, "message": "VS Code + Continue extension installed"}
    return {"success": False, "message": "Failed to install VS Code via Homebrew.", "error_log": result["stderr"] or result["stdout"]}


def _install_copilot():
    if not is_installed("brew"):
        brew = install_homebrew()
        if not brew["success"]:
            return {"success": False, "message": "Homebrew is required for VS Code and could not be installed.", "error_log": brew.get("error_log", "")}
    vscode_cmd = _find_vscode_cmd()
    if not vscode_cmd:
        result = run("brew install --cask visual-studio-code", timeout=300)
        if not result["success"]:
            return {"success": False, "message": "Failed to install VS Code via Homebrew.", "error_log": result["stderr"] or result["stdout"]}
        vscode_cmd = _find_vscode_cmd() or "code"
    run(f'"{vscode_cmd}" --install-extension GitHub.copilot', timeout=60)
    run(f'"{vscode_cmd}" --install-extension GitHub.copilot-chat', timeout=60)
    return {"success": True, "message": "VS Code + GitHub Copilot extension installed"}


def _install_aider():
    if not is_installed("pip3") and not is_installed("pip"):
        return {"success": False, "message": "pip is required to install Aider. Python may not be installed.",
                "error_log": "pip and pip3 not found in PATH"}
    pip = "pip3" if is_installed("pip3") else "pip"
    result = run(f"{pip} install aider-chat", timeout=120)
    if result["success"]:
        return {"success": True, "message": "Aider installed successfully"}
    return {"success": False, "message": "Failed to install Aider via pip.", "error_log": result["stderr"] or result["stdout"]}


def launch_ai_tool(tool, project_path):
    """Launch an AI tool pointed at the project directory and bring it to front.

    Uses launch() (fire-and-forget via subprocess.Popen) to start the tool,
    then explicitly activates it with osascript so it appears on top of the browser.
    """
    # Map tool name to the macOS application name for `open -a` and `activate`
    app_names = {
        "cursor": "Cursor",
        "windsurf": "Windsurf",
        "vscode": "Visual Studio Code",
        "copilot": "Visual Studio Code",
    }

    if tool == "claude-code":
        # `do script` opens and activates Terminal automatically
        script = f'''osascript -e 'tell application "Terminal" to do script "cd \\"{project_path}\\" && claude"' -e 'tell application "Terminal" to activate' '''
        launch(script)
        return {"success": True, "message": "Claude Code launched in Terminal"}

    if tool == "aider":
        script = f'''osascript -e 'tell application "Terminal" to do script "cd \\"{project_path}\\" && aider"' -e 'tell application "Terminal" to activate' '''
        launch(script)
        return {"success": True, "message": "Aider launched in Terminal"}

    app = app_names.get(tool)
    if not app:
        return {"success": False, "message": f"Cannot launch {tool}"}

    result = launch(f'open -a "{app}" "{project_path}"')
    if not result["success"]:
        return {"success": False, "message": f"Failed to launch {app}: {result['stderr']}"}

    # Bring the app to front — open -a alone does not guarantee focus
    run(f"osascript -e 'tell application \"{app}\" to activate'", timeout=5)
    return {"success": True, "message": f"{app} launched"}


def minimize_wizard_window():
    """Minimize the wizard browser window on macOS.

    Targets browsers by name directly so focus doesn't matter — avoids
    the race condition where the launched tool grabs focus and the old
    keystroke approach minimized the wrong window.
    """
    for browser in ["Google Chrome", "Chromium", "Microsoft Edge", "Firefox", "Safari"]:
        r = run(
            f"osascript -e 'tell application \"{browser}\" to set miniaturized of front window to true'",
            timeout=5,
        )
        if r["success"]:
            return {"success": True, "message": "Wizard minimized"}
    return {"success": True, "message": "Wizard window minimization not available on this system"}


def install_tkinter():
    """Install python-tk via Homebrew (required for agent animation window)."""
    try:
        import importlib
        if importlib.util.find_spec("tkinter") is not None:
            return {"success": True, "message": "python-tk is already available", "skipped": True}
    except Exception:
        pass

    if not is_installed("brew"):
        brew_result = install_homebrew()
        if not brew_result["success"]:
            return {"success": False, "message": "Cannot install python-tk: Homebrew is required"}

    import sys
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    result = run(f"brew install python-tk@{py_ver}", timeout=120)
    if result["success"]:
        return {"success": True, "message": f"python-tk@{py_ver} installed via Homebrew"}

    # Fallback: try without version suffix
    result = run("brew install python-tk", timeout=120)
    if result["success"]:
        return {"success": True, "message": "python-tk installed via Homebrew"}

    return {
        "success": False,
        "message": "Failed to install python-tk. Try: brew install python-tk",
        "error_log": result.get("stderr") or result.get("stdout", ""),
    }
