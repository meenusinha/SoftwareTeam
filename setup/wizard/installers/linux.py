"""Linux-specific installation logic."""

import os
import subprocess

from setup.wizard.utils.shell import run, launch, is_installed, log_message, _get_env
from setup.wizard.utils.os_detect import get_os_info


def _sudo():
    """Return 'sudo ' prefix only when needed.

    Returns '' if already running as root (uid 0) or if passwordless sudo
    is available (sudo -n). Returns 'sudo ' otherwise so the caller prompts
    for a password via the wizard UI.
    """
    try:
        if os.getuid() == 0:
            return ""
    except AttributeError:
        pass  # Windows — shouldn't happen in linux.py

    # Check passwordless sudo
    result = subprocess.run(
        ["sudo", "-n", "true"],
        capture_output=True,
        timeout=5,
        env=_get_env(),
    )
    if result.returncode == 0:
        return ""

    return "sudo "


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

    s = _sudo()
    if mgr == "apt":
        cmd = f"{s}apt update && {s}apt install -y {packages.get('apt', '')}"
    elif mgr == "dnf":
        cmd = f"{s}dnf install -y {packages.get('dnf', '')}"
    elif mgr == "yum":
        cmd = f"{s}yum install -y {packages.get('yum', packages.get('dnf', ''))}"
    elif mgr == "pacman":
        cmd = f"{s}pacman -S --noconfirm {packages.get('pacman', '')}"
    elif mgr == "zypper":
        cmd = f"{s}zypper install -y {packages.get('zypper', '')}"
    else:
        return {"success": False, "message": "No supported package manager found", "error_log": f"Detected package manager: {mgr}"}

    result = run(cmd, timeout=600)
    return {
        "success": result["success"],
        "message": result["stdout"] if result["success"] else "Installation failed.",
        "error_log": result["stderr"] or result["stdout"] if not result["success"] else "",
    }


def _install_via_terminal(tool_name, cmd, check_binary):
    """Open a terminal so the user can run a sudo command natively.

    Launches the command in a visible terminal window so sudo prompts
    appear in a trusted terminal rather than the browser wizard.
    Uses launch() (fire-and-forget) so the wizard never blocks or times out
    waiting for the terminal to close.
    """
    if not cmd:
        return {"success": False, "message": f"No install command available for {tool_name}"}

    launched = False
    for terminal, flag in [
        ("gnome-terminal", "--"),
        ("xterm", "-e"),
        ("konsole", "-e"),
        ("xfce4-terminal", "-e"),
        ("lxterminal", "-e"),
        ("mate-terminal", "-e"),
    ]:
        if is_installed(terminal):
            full_cmd = (
                f"{terminal} {flag} bash -c "
                f'"{cmd}; echo; echo \'Installation complete. You may close this window.\'; '
                f"read -p 'Press Enter to close...' _\""
            )
            log_message(f"[sudo required] Opening a terminal window to install {tool_name}.")
            log_message("[action needed]  Enter your sudo password in the terminal that appears.")
            launch(full_cmd)  # fire-and-forget — terminal runs independently
            launched = True
            break

    if not launched:
        return {
            "success": False,
            "message": (
                f"No terminal emulator found to run the install command.\n"
                f"Please run this manually:\n{cmd}"
            ),
            "error_log": cmd,
        }

    return {
        "success": True,
        "message": (
            f"A terminal window has opened to install {tool_name}. "
            "Please enter your sudo password there and wait for it to finish, "
            "then click 'Check Again'."
        ),
        "terminal_launched": True,
    }


def install_git():
    """Install git on Linux.

    Tries the package manager via a terminal window so any sudo password
    prompt appears in a trusted terminal, not the browser wizard.
    """
    if is_installed("git"):
        return {"success": True, "message": "Git is already installed", "skipped": True}

    info = get_os_info()
    mgr = info.get("pkg_manager")
    s = _sudo()
    cmds = {
        "apt":    f"{s}apt update && {s}apt install -y git",
        "dnf":    f"{s}dnf install -y git",
        "yum":    f"{s}yum install -y git",
        "pacman": f"{s}pacman -S --noconfirm git",
        "zypper": f"{s}zypper install -y git",
    }
    cmd = cmds.get(mgr, "")

    # If already root or passwordless sudo, run directly (no terminal needed)
    if s == "":
        return _pkg_install({"apt": "git", "dnf": "git", "pacman": "git", "zypper": "git"})

    return _install_via_terminal("git", cmd, "git")


def install_gh():
    """Install GitHub CLI on Linux using a standalone binary — no sudo required.

    Downloads the latest release tarball from GitHub and installs to ~/.local/bin.
    Falls back to package manager (needs sudo) only if the download fails.
    """
    if is_installed("gh"):
        return {"success": True, "message": "GitHub CLI is already installed", "skipped": True}

    # --- Standalone binary install (no sudo) ---
    result = run(
        'curl -fsSL https://api.github.com/repos/cli/cli/releases/latest'
        " | grep '\"tag_name\"' | cut -d'\"' -f4 | sed 's/v//' > /tmp/_gh_ver.txt"
        " && GH_VER=$(cat /tmp/_gh_ver.txt)"
        " && mkdir -p ~/.local/bin"
        ' && curl -fsSL "https://github.com/cli/cli/releases/download/v${GH_VER}/gh_${GH_VER}_linux_amd64.tar.gz"'
        " -o /tmp/gh.tar.gz"
        " && tar -xzf /tmp/gh.tar.gz -C /tmp"
        " && mv /tmp/gh_${GH_VER}_linux_amd64/bin/gh ~/.local/bin/gh"
        " && chmod +x ~/.local/bin/gh"
        " && rm -rf /tmp/gh.tar.gz /tmp/gh_${GH_VER}_linux_amd64 /tmp/_gh_ver.txt",
        timeout=120,
    )
    if result["success"] and os.path.isfile(os.path.expanduser("~/.local/bin/gh")):
        # Ensure ~/.local/bin is on PATH for this session
        run('export PATH="$HOME/.local/bin:$PATH"')
        return {"success": True, "message": "GitHub CLI installed to ~/.local/bin (no sudo needed)"}

    # --- Fallback: package manager (needs sudo via terminal) ---
    return _install_via_terminal(
        "GitHub CLI (gh)",
        _gh_pkg_cmd(),
        "gh",
    )


def _gh_pkg_cmd():
    """Return the package-manager command to install gh."""
    info = get_os_info()
    mgr = info.get("pkg_manager")
    s = _sudo()
    if mgr == "apt":
        return (
            f"type -p curl >/dev/null || {s}apt install curl -y && "
            "curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | "
            f"{s}dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && "
            f"{s}chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && "
            'echo "deb [arch=$(dpkg --print-architecture) '
            'signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] '
            'https://cli.github.com/packages stable main" | '
            f"{s}tee /etc/apt/sources.list.d/github-cli.list > /dev/null && "
            f"{s}apt update && {s}apt install gh -y"
        )
    if mgr == "dnf":
        return f"{s}dnf install -y gh"
    if mgr == "pacman":
        return f"{s}pacman -S --noconfirm github-cli"
    return ""


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
        s = _sudo()
        if s:
            # Need elevated access for the package manager — open terminal
            info = get_os_info()
            mgr = info.get("pkg_manager")
            cmds = {
                "apt":    "sudo apt install -y nodejs npm",
                "dnf":    "sudo dnf install -y nodejs npm",
                "pacman": "sudo pacman -S --noconfirm nodejs npm",
            }
            cmd = cmds.get(mgr, "")
            if cmd:
                return _install_via_terminal("Node.js (required for Claude Code)", cmd, "npm")
            return {"success": False, "message": f"No Node.js install command for package manager: {mgr}"}
        else:
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

    # Global install failed (system npm requires sudo) — open terminal instead of
    # running sudo in the background where no password prompt is visible
    return _install_via_terminal(
        "Claude Code",
        "sudo npm install -g @anthropic-ai/claude-code",
        "claude",
    )


def _install_vscode():
    """Install VS Code using the portable tarball — no sudo required."""
    result = run(
        'curl -fsSL "https://code.visualstudio.com/sha/download?build=stable&os=linux-x64"'
        " -o /tmp/vscode.tar.gz"
        " && mkdir -p ~/.local/share/vscode"
        " && tar -xzf /tmp/vscode.tar.gz -C ~/.local/share/vscode --strip-components=1"
        " && mkdir -p ~/.local/bin"
        " && ln -sf ~/.local/share/vscode/bin/code ~/.local/bin/code"
        " && rm -f /tmp/vscode.tar.gz",
        timeout=300,
    )
    if result["success"]:
        vscode_cmd = _find_vscode_cmd() or os.path.expanduser("~/.local/bin/code")
        run(f'"{vscode_cmd}" --install-extension continue.continue', timeout=60)
        return {"success": True, "message": "VS Code + Continue extension installed (no sudo needed)"}
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
    """Install VS Code without extensions using the portable tarball (no sudo)."""
    result = run(
        'curl -fsSL "https://code.visualstudio.com/sha/download?build=stable&os=linux-x64"'
        " -o /tmp/vscode.tar.gz"
        " && mkdir -p ~/.local/share/vscode"
        " && tar -xzf /tmp/vscode.tar.gz -C ~/.local/share/vscode --strip-components=1"
        " && mkdir -p ~/.local/bin"
        " && ln -sf ~/.local/share/vscode/bin/code ~/.local/bin/code"
        " && rm -f /tmp/vscode.tar.gz",
        timeout=300,
    )
    return {
        "success": result["success"],
        "message": "VS Code installed" if result["success"] else "Failed to install VS Code.",
        "error_log": "" if result["success"] else (result["stderr"] or result["stdout"]),
    }


def _install_aider():
    if not is_installed("pip3") and not is_installed("pip"):
        _pkg_install({"apt": "python3-pip", "dnf": "python3-pip", "pacman": "python-pip"})
    pip = "pip3" if is_installed("pip3") else "pip"
    # --user installs to ~/.local — no sudo needed
    result = run(f"{pip} install --user aider-chat", timeout=120)
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
    """Install python3-tk (required for agent animation window).

    Uses a terminal window when sudo is required so the password prompt
    is visible — never asks for credentials in the wizard GUI.
    """
    try:
        import importlib
        if importlib.util.find_spec("tkinter") is not None:
            return {"success": True, "message": "python-tk is already available", "skipped": True}
    except Exception:
        pass

    info = get_os_info()
    mgr = info.get("pkg_manager")
    s = _sudo()

    # If we need sudo and can't do it passwordlessly, open a terminal
    if s:
        cmds = {
            "apt":    "sudo apt install -y python3-tk",
            "dnf":    "sudo dnf install -y python3-tkinter",
            "yum":    "sudo yum install -y python3-tkinter",
            "pacman": "sudo pacman -S --noconfirm tk",
            "zypper": "sudo zypper install -y python3-tk",
        }
        cmd = cmds.get(mgr, "")
        if cmd:
            return _install_via_terminal("python3-tk (animation window)", cmd, None)
        return {"success": False, "message": f"No install command for package manager: {mgr}"}

    # Running as root or passwordless sudo — install directly
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
