"""Windows-specific installation logic."""

import os
import shutil

from setup.wizard.utils.shell import run, launch, is_installed


def _is_vscode_installed():
    """Check if VS Code is installed on Windows."""
    return _find_vscode_cmd() is not None


def _find_vscode_cmd():
    """Find the VS Code executable, returning the full path or None.

    Always returns an absolute path — bare 'code' won't work with
    subprocess shell=False since CreateProcess can't find .cmd files by name.
    """
    # Resolve 'code' to full path (e.g. C:\...\bin\code.cmd)
    from setup.wizard.utils.shell import _get_env
    for name in ["code", "code.cmd"]:
        full_path = shutil.which(name, path=_get_env().get("PATH"))
        if full_path:
            return full_path
    # Check common install locations
    for path in [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft VS Code\bin\code.cmd"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft VS Code\Code.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft VS Code\bin\code.cmd"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft VS Code\Code.exe"),
    ]:
        if os.path.isfile(path):
            return path
    return None


def install_git():
    """Install git on Windows."""
    if is_installed("git"):
        return {"success": True, "message": "Git is already installed", "skipped": True}

    errors = []

    if is_installed("winget"):
        result = run(
            "winget install Git.Git --accept-package-agreements --accept-source-agreements",
            timeout=180,
        )
        if result["success"]:
            return {"success": True, "message": "Git installed via winget"}
        errors.append(f"[winget] {result['stderr'] or result['stdout']}")

    if is_installed("choco"):
        result = run("choco install git -y", timeout=180)
        if result["success"]:
            return {"success": True, "message": "Git installed via Chocolatey"}
        errors.append(f"[choco] {result['stderr'] or result['stdout']}")

    if not errors:
        errors.append("No package manager found (winget or Chocolatey). Try running PowerShell as Administrator.")

    return {
        "success": False,
        "message": "Automatic installation failed. Try running as Administrator or check your network.",
        "error_log": "\n".join(errors),
    }


def install_gh():
    """Install GitHub CLI on Windows."""
    if is_installed("gh"):
        return {"success": True, "message": "GitHub CLI is already installed", "skipped": True}

    errors = []

    if is_installed("winget"):
        result = run(
            "winget install GitHub.cli --accept-package-agreements --accept-source-agreements",
            timeout=180,
        )
        if result["success"]:
            return {"success": True, "message": "GitHub CLI installed via winget"}
        errors.append(f"[winget] {result['stderr'] or result['stdout']}")

    if is_installed("choco"):
        result = run("choco install gh -y", timeout=180)
        if result["success"]:
            return {"success": True, "message": "GitHub CLI installed via Chocolatey"}
        errors.append(f"[choco] {result['stderr'] or result['stdout']}")

    if not errors:
        errors.append("No package manager found (winget or Chocolatey). Try running PowerShell as Administrator.")

    return {
        "success": False,
        "message": "Automatic installation failed. Try running as Administrator or check your network.",
        "error_log": "\n".join(errors),
    }


def check_ai_tool(tool):
    """Check if an AI tool is already installed on Windows.

    Returns dict with 'installed' (bool) and 'message'.
    """
    checks = {
        "cursor": lambda: is_installed("cursor"),
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
    """Install an AI tool on Windows."""
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
    if is_installed("winget"):
        result = run(
            "winget install Anysphere.Cursor --accept-package-agreements --accept-source-agreements",
            timeout=300,
        )
        if result["success"]:
            return {"success": True, "message": "Cursor installed via winget"}
        return {"success": False, "message": "Failed to install Cursor via winget.", "error_log": result["stderr"] or result["stdout"]}
    return {"success": False, "message": "winget is required to install Cursor automatically.", "error_log": "winget not found in PATH"}


def _install_windsurf():
    if is_installed("winget"):
        result = run(
            "winget install Codeium.Windsurf --accept-package-agreements --accept-source-agreements",
            timeout=300,
        )
        if result["success"]:
            return {"success": True, "message": "Windsurf installed via winget"}
        return {"success": False, "message": "Failed to install Windsurf via winget.", "error_log": result["stderr"] or result["stdout"]}
    return {"success": False, "message": "winget is required to install Windsurf automatically.", "error_log": "winget not found in PATH"}


def _install_claude_code():
    if not is_installed("npm"):
        # Try installing Node.js first
        if is_installed("winget"):
            node_result = run(
                "winget install OpenJS.NodeJS --accept-package-agreements --accept-source-agreements",
                timeout=300,
            )
            if not node_result["success"]:
                return {"success": False, "message": "Failed to install Node.js (required for Claude Code).",
                        "error_log": node_result["stderr"] or node_result["stdout"]}
        else:
            return {"success": False, "message": "Node.js/npm is required for Claude Code. winget not found.",
                    "error_log": "winget not found — cannot auto-install Node.js"}

    result = run("npm install -g @anthropic-ai/claude-code", timeout=120)
    if result["success"]:
        return {"success": True, "message": "Claude Code installed successfully"}
    return {"success": False, "message": "Failed to install Claude Code via npm.", "error_log": result["stderr"] or result["stdout"]}


def _install_vscode():
    if is_installed("winget"):
        result = run(
            "winget install Microsoft.VisualStudioCode --accept-package-agreements --accept-source-agreements",
            timeout=300,
        )
        if result["success"]:
            vscode_cmd = _find_vscode_cmd() or "code"
            run([vscode_cmd, "--install-extension", "continue.continue"], timeout=60)
            return {"success": True, "message": "VS Code + Continue extension installed"}
        return {"success": False, "message": "Failed to install VS Code via winget.", "error_log": result["stderr"] or result["stdout"]}
    return {"success": False, "message": "winget is required to install VS Code automatically.", "error_log": "winget not found in PATH"}


def _install_copilot():
    vscode_cmd = _find_vscode_cmd()
    if not vscode_cmd:
        if is_installed("winget"):
            result = run(
                "winget install Microsoft.VisualStudioCode --accept-package-agreements --accept-source-agreements",
                timeout=300,
            )
            if not result["success"]:
                return {"success": False, "message": "Failed to install VS Code via winget.", "error_log": result["stderr"] or result["stdout"]}
            vscode_cmd = _find_vscode_cmd() or "code"
        else:
            return {"success": False, "message": "winget is required to install VS Code automatically.", "error_log": "winget not found in PATH"}
    run([vscode_cmd, "--install-extension", "GitHub.copilot"], timeout=60)
    run([vscode_cmd, "--install-extension", "GitHub.copilot-chat"], timeout=60)
    return {"success": True, "message": "VS Code + GitHub Copilot extension installed"}


def _install_aider():
    if not is_installed("pip") and not is_installed("pip3"):
        return {"success": False, "message": "Python/pip is required for Aider. Trying to install via winget...",
                "error_log": "pip not found in PATH"}
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
        launch(f'start "" cursor "{project_path}"')
        return {"success": True, "message": "Cursor launched"}

    if tool == "windsurf":
        launch(f'start "" windsurf "{project_path}"')
        return {"success": True, "message": "Windsurf launched"}

    if tool == "claude-code":
        launch(f'start cmd /k "cd /d "{project_path}" && claude"')
        return {"success": True, "message": "Claude Code launched in Command Prompt"}

    if tool == "vscode" or tool == "copilot":
        vscode_cmd = _find_vscode_cmd()
        if not vscode_cmd:
            return {"success": False, "message": "VS Code not found. Please reinstall."}
        label = "VS Code + GitHub Copilot" if tool == "copilot" else "VS Code"
        result = launch(f'"{vscode_cmd}" "{project_path}"')
        if result["success"]:
            return {"success": True, "message": f"{label} launched"}
        return {"success": False, "message": f"Failed to launch {label}: {result['stderr']}"}

    if tool == "aider":
        launch(f'start cmd /k "cd /d "{project_path}" && aider"')
        return {"success": True, "message": "Aider launched in Command Prompt"}

    return {"success": False, "message": f"Unknown tool: {tool}"}


def minimize_wizard_window():
    """Minimize the wizard browser window on Windows.

    Uses a list-based call so no shell-escaping issues.
    Add-Type is wrapped in try/catch so re-calls don't fail.
    $p is forced to array with @() so .MainWindowHandle works on single results.
    """
    ps_code = (
        "$ErrorActionPreference='SilentlyContinue';"
        "try{Add-Type -MemberDefinition '[DllImport(\"user32.dll\")]public static extern bool ShowWindow(IntPtr h,int c);'"
        " -Name WzW -Namespace Wz}catch{};"
        "foreach($b in 'chrome','msedge','firefox'){"
        "$procs=@(Get-Process $b|Where-Object{$_.MainWindowHandle -ne 0});"
        "if($procs.Count -gt 0){[Wz.WzW]::ShowWindow($procs[0].MainWindowHandle,6);break}}"
    )
    run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_code], timeout=10)
    return {"success": True, "message": "Wizard minimized"}


def install_tkinter():
    """Verify tkinter is available on Windows (bundled with standard Python installer)."""
    import subprocess
    import sys

    check = subprocess.run(
        [sys.executable, "-c", "import tkinter"],
        capture_output=True,
    )
    if check.returncode == 0:
        return {
            "success": True,
            "message": "python-tk is already available (bundled with Python)",
            "skipped": True,
        }
    return {
        "success": False,
        "message": (
            "tkinter not found. Please reinstall Python from python.org "
            "and ensure the 'tcl/tk and IDLE' option is checked during installation."
        ),
    }
