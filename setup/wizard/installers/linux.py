"""Linux-specific installation logic."""

import os

from setup.wizard.utils.shell import run, launch, is_installed
from setup.wizard.utils.os_detect import get_os_info


def _find_vscode_cmd():
    """Find the VS Code command, returning a full path or runnable command.

    Always returns an absolute path (not bare 'code') to avoid PATH
    discrepancies between Python's shutil.which and /bin/sh resolution.
    Returns None if not found.
    """
    # Use shell's 'which' via run() — same env/PATH as launch commands
    for name in ["code", "code-insiders"]:
        result = run(f"which {name} 2>/dev/null")
        if result["success"] and result["stdout"]:
            return result["stdout"]  # full path e.g. /usr/bin/code
    # Try login shell (picks up .bashrc/.profile PATH additions)
    for name in ["code", "code-insiders"]:
        result = run(f"bash -lc 'which {name} 2>/dev/null'")
        if result["success"] and result["stdout"]:
            return result["stdout"]
    # Check snap
    if os.path.isfile("/snap/bin/code"):
        return "/snap/bin/code"
    # Check flatpak
    result = run("flatpak list --app 2>/dev/null | grep -qi 'com.visualstudio.code'")
    if result["success"]:
        return "flatpak run com.visualstudio.code"
    # Check common install locations
    for path in [
        "/usr/share/code/code",
        "/usr/share/code/bin/code",
        "/usr/bin/code",
        "/usr/lib/code/code",
        os.path.expanduser("~/.local/bin/code"),
    ]:
        if os.path.isfile(path):
            return path
    # Check dpkg/rpm — find actual binary path
    result = run("dpkg -L code 2>/dev/null | grep -m1 'bin/code$'")
    if result["success"] and result["stdout"] and os.path.isfile(result["stdout"]):
        return result["stdout"]
    result = run("rpm -ql code 2>/dev/null | grep -m1 'bin/code$'")
    if result["success"] and result["stdout"] and os.path.isfile(result["stdout"]):
        return result["stdout"]
    return None


def _is_vscode_installed():
    """Check if VS Code is installed via any method."""
    return _find_vscode_cmd() is not None


def _pkg_install(packages):
    """Install packages using the detected package manager.

    Args:
        packages: dict mapping pkg_manager -> package name(s) string
    """
    info = get_os_info()
    mgr = info.get("pkg_manager")

    if mgr == "apt":
        cmd = f"sudo apt update && sudo apt install -y {packages.get('apt', '')}"
    elif mgr == "dnf":
        cmd = f"sudo dnf install -y {packages.get('dnf', '')}"
    elif mgr == "yum":
        cmd = f"sudo yum install -y {packages.get('yum', packages.get('dnf', ''))}"
    elif mgr == "pacman":
        cmd = f"sudo pacman -S --noconfirm {packages.get('pacman', '')}"
    elif mgr == "zypper":
        cmd = f"sudo zypper install -y {packages.get('zypper', '')}"
    else:
        return {"success": False, "message": "No supported package manager found", "error_log": f"Detected package manager: {mgr}"}

    result = run(cmd, timeout=300)
    return {
        "success": result["success"],
        "message": result["stdout"] if result["success"] else "Installation failed.",
        "error_log": result["stderr"] or result["stdout"] if not result["success"] else "",
    }


def install_git():
    """Install git on Linux."""
    if is_installed("git"):
        return {"success": True, "message": "Git is already installed", "skipped": True}

    return _pkg_install({
        "apt": "git",
        "dnf": "git",
        "pacman": "git",
        "zypper": "git",
    })


def install_gh():
    """Install GitHub CLI on Linux."""
    if is_installed("gh"):
        return {"success": True, "message": "GitHub CLI is already installed", "skipped": True}

    info = get_os_info()
    mgr = info.get("pkg_manager")

    if mgr == "apt":
        # Official gh repo for Debian/Ubuntu
        cmds = (
            "type -p curl >/dev/null || sudo apt install curl -y && "
            "curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | "
            "sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && "
            "sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && "
            'echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] '
            'https://cli.github.com/packages stable main" | '
            "sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null && "
            "sudo apt update && sudo apt install gh -y"
        )
        result = run(cmds, timeout=300)
    elif mgr == "dnf":
        result = run("sudo dnf install -y gh", timeout=120)
    elif mgr == "pacman":
        result = run("sudo pacman -S --noconfirm github-cli", timeout=120)
    else:
        return {"success": False, "message": f"Cannot auto-install gh: package manager '{mgr}' is not yet supported.", "error_log": f"Detected pkg manager: {mgr}"}

    if result["success"]:
        return {"success": True, "message": "GitHub CLI installed successfully"}
    return {"success": False, "message": "Failed to install GitHub CLI.", "error_log": result["stderr"] or result["stdout"]}


def check_ai_tool(tool):
    """Check if an AI tool is already installed on Linux.

    Returns dict with 'installed' (bool) and 'message'.
    """
    checks = {
        "cursor": lambda: is_installed("cursor") or os.path.isfile(os.path.expanduser("~/cursor.AppImage")),
        "windsurf": lambda: is_installed("windsurf"),
        "claude-code": lambda: is_installed("claude"),
        "vscode": lambda: _is_vscode_installed(),
        "copilot": lambda: _is_vscode_installed(),
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


def install_ai_tool(tool):
    """Install an AI tool on Linux."""
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
    info = get_os_info()
    mgr = info.get("pkg_manager")

    if mgr == "apt":
        # Download AppImage
        result = run(
            'curl -fsSL "https://downloader.cursor.sh/linux/appImage/x64" -o ~/cursor.AppImage '
            "&& chmod +x ~/cursor.AppImage",
            timeout=300,
        )
        if result["success"]:
            return {"success": True, "message": "Cursor AppImage downloaded to ~/cursor.AppImage"}
    elif mgr in ("dnf", "pacman"):
        result = run(
            'curl -fsSL "https://downloader.cursor.sh/linux/appImage/x64" -o ~/cursor.AppImage '
            "&& chmod +x ~/cursor.AppImage",
            timeout=300,
        )
        if result["success"]:
            return {"success": True, "message": "Cursor AppImage downloaded to ~/cursor.AppImage"}

    return {"success": False, "message": "Failed to download Cursor AppImage.", "error_log": "curl download failed — check network connection"}


def _install_windsurf():
    # Windsurf has no official Linux package manager support yet; try direct download
    result = run(
        'curl -fsSL "https://windsurf-stable.codeiumdata.com/linux-x64/stable/Windsurf-linux-x64-latest.tar.gz" -o /tmp/windsurf.tar.gz '
        '&& mkdir -p ~/windsurf && tar -xzf /tmp/windsurf.tar.gz -C ~/windsurf --strip-components=1',
        timeout=300,
    )
    if result["success"]:
        return {"success": True, "message": "Windsurf extracted to ~/windsurf"}
    return {
        "success": False,
        "message": "Could not download Windsurf automatically.",
        "error_log": result["stderr"] or result["stdout"],
    }


def _install_claude_code():
    if not is_installed("npm"):
        result = _pkg_install({
            "apt": "nodejs npm",
            "dnf": "nodejs npm",
            "pacman": "nodejs npm",
        })
        if not result["success"]:
            return {"success": False, "message": "Failed to install Node.js (required for Claude Code).",
                    "error_log": result.get("error_log", "")}

    result = run("npm install -g @anthropic-ai/claude-code", timeout=120)
    if result["success"]:
        return {"success": True, "message": "Claude Code installed successfully"}
    # Try with sudo
    result = run("sudo npm install -g @anthropic-ai/claude-code", timeout=120)
    if result["success"]:
        return {"success": True, "message": "Claude Code installed successfully"}
    return {"success": False, "message": "Failed to install Claude Code via npm.", "error_log": result["stderr"] or result["stdout"]}


def _install_vscode():
    info = get_os_info()
    mgr = info.get("pkg_manager")

    if mgr == "apt":
        cmds = (
            "curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /tmp/ms.gpg && "
            "sudo install -o root -g root -m 644 /tmp/ms.gpg /etc/apt/trusted.gpg.d/ && "
            'echo "deb [arch=amd64] https://packages.microsoft.com/repos/code stable main" | '
            "sudo tee /etc/apt/sources.list.d/vscode.list && "
            "sudo apt update && sudo apt install -y code"
        )
        result = run(cmds, timeout=300)
    elif mgr == "dnf":
        result = run("sudo dnf install -y code", timeout=120)
    elif mgr == "pacman":
        result = run("sudo pacman -S --noconfirm code", timeout=120)
    else:
        return {"success": False, "message": "Please install VS Code manually from https://code.visualstudio.com"}

    if result["success"]:
        vscode_cmd = _find_vscode_cmd() or "code"
        run(f'{vscode_cmd} --install-extension continue.continue', timeout=60)
        return {"success": True, "message": "VS Code + Continue extension installed"}
    return {"success": False, "message": "Failed to install VS Code.", "error_log": result["stderr"] or result["stdout"]}


def _install_copilot():
    # Install VS Code if not present, then add Copilot extension
    vscode_cmd = _find_vscode_cmd()
    if not vscode_cmd:
        result = _install_vscode_only()
        if not result["success"]:
            return result
        vscode_cmd = _find_vscode_cmd() or "code"
    run(f"{vscode_cmd} --install-extension GitHub.copilot", timeout=60)
    run(f"{vscode_cmd} --install-extension GitHub.copilot-chat", timeout=60)
    return {"success": True, "message": "VS Code + GitHub Copilot extension installed"}


def _install_vscode_only():
    """Install VS Code without extensions."""
    info = get_os_info()
    mgr = info.get("pkg_manager")

    if mgr == "apt":
        cmds = (
            "curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /tmp/ms.gpg && "
            "sudo install -o root -g root -m 644 /tmp/ms.gpg /etc/apt/trusted.gpg.d/ && "
            'echo "deb [arch=amd64] https://packages.microsoft.com/repos/code stable main" | '
            "sudo tee /etc/apt/sources.list.d/vscode.list && "
            "sudo apt update && sudo apt install -y code"
        )
        result = run(cmds, timeout=300)
    elif mgr == "dnf":
        result = run("sudo dnf install -y code", timeout=120)
    elif mgr == "pacman":
        result = run("sudo pacman -S --noconfirm code", timeout=120)
    else:
        return {"success": False, "message": "Please install VS Code manually from https://code.visualstudio.com"}

    return {"success": result["success"], "message": "VS Code installed" if result["success"] else "Failed to install VS Code.",
            "error_log": "" if result["success"] else (result["stderr"] or result["stdout"])}


def _install_aider():
    if not is_installed("pip3") and not is_installed("pip"):
        _pkg_install({"apt": "python3-pip", "dnf": "python3-pip", "pacman": "python-pip"})
    pip = "pip3" if is_installed("pip3") else "pip"
    result = run(f"{pip} install aider-chat", timeout=120)
    if result["success"]:
        return {"success": True, "message": "Aider installed successfully"}
    return {"success": False, "message": "Failed to install Aider via pip.", "error_log": result["stderr"] or result["stdout"]}


def launch_ai_tool(tool, project_path):
    """Launch an AI tool pointed at the project directory.

    Uses launch() (fire-and-forget via subprocess.Popen) so the API call
    returns immediately and the launched tool window appears on top.
    """
    if tool == "cursor":
        result = launch(f'~/cursor.AppImage "{project_path}"')
        if result["success"]:
            return {"success": True, "message": "Cursor launched"}
        return {"success": False, "message": f"Failed to launch Cursor: {result['stderr']}"}

    if tool == "windsurf":
        result = launch(f'windsurf "{project_path}"')
        if result["success"]:
            return {"success": True, "message": "Windsurf launched"}
        return {"success": False, "message": f"Failed to launch Windsurf: {result['stderr']}"}

    if tool == "claude-code":
        # Open a terminal with claude
        for terminal in ["gnome-terminal", "xterm", "konsole", "xfce4-terminal"]:
            if is_installed(terminal):
                if terminal == "gnome-terminal":
                    cmd = f'{terminal} -- bash -c "cd \\"{project_path}\\" && claude; exec bash"'
                else:
                    cmd = f'{terminal} -e "bash -c \\"cd \\"{project_path}\\" && claude; exec bash\\""'
                launch(cmd)
                return {"success": True, "message": "Claude Code launched in terminal"}
        return {"success": False, "message": "No supported terminal emulator found"}

    if tool == "vscode" or tool == "copilot":
        vscode_cmd = _find_vscode_cmd()
        if not vscode_cmd:
            return {"success": False, "message": "VS Code not found. Try restarting your terminal or reinstalling."}
        label = "VS Code + GitHub Copilot" if tool == "copilot" else "VS Code"
        result = launch(f'{vscode_cmd} "{project_path}"')
        if result["success"]:
            return {"success": True, "message": f"{label} launched"}
        return {"success": False, "message": f"Failed to launch {label}: {result['stderr']}"}

    if tool == "aider":
        for terminal in ["gnome-terminal", "xterm", "konsole", "xfce4-terminal"]:
            if is_installed(terminal):
                if terminal == "gnome-terminal":
                    cmd = f'{terminal} -- bash -c "cd \\"{project_path}\\" && aider; exec bash"'
                else:
                    cmd = f'{terminal} -e "bash -c \\"cd \\"{project_path}\\" && aider; exec bash\\""'
                launch(cmd)
                return {"success": True, "message": "Aider launched in terminal"}
        return {"success": False, "message": "No supported terminal emulator found"}

    return {"success": False, "message": f"Unknown tool: {tool}"}


def minimize_wizard_window():
    """Minimize the wizard browser window using available Linux tools."""
    # Try wmctrl first (most reliable but not always installed)
    if is_installed("wmctrl"):
        result = run("wmctrl -l | grep -i firefox | head -1 | awk '{print $1}' | xargs -I{} wmctrl -ic {}")
        if result["success"]:
            return {"success": True, "message": "Wizard minimized"}
        # Try Chrome/Chromium
        result = run("wmctrl -l | grep -i chrome | head -1 | awk '{print $1}' | xargs -I{} wmctrl -ic {}")
        if result["success"]:
            return {"success": True, "message": "Wizard minimized"}

    # Fall back to xdotool if available
    if is_installed("xdotool"):
        result = run("xdotool search --name wizard windowminimize")
        if result["success"]:
            return {"success": True, "message": "Wizard minimized"}

    return {"success": True, "message": "Wizard window minimization not available on this system"}


def install_tkinter():
    """Install python3-tk (required for agent animation window)."""
    try:
        import importlib
        if importlib.util.find_spec("tkinter") is not None:
            return {"success": True, "message": "python-tk is already available", "skipped": True}
    except Exception:
        pass

    result = _pkg_install({
        "apt":    "python3-tk",
        "dnf":    "python3-tkinter",
        "yum":    "python3-tkinter",
        "pacman": "tk",
        "zypper": "python3-tk",
    })
    if result.get("success"):
        return {"success": True, "message": "python3-tk installed successfully"}
    return result
