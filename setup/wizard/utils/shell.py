"""Shell command execution utilities."""

import subprocess
import shutil
import os


def run(cmd, capture=True, timeout=120, cwd=None):
    """Run a shell command and return result dict.

    Args:
        cmd: Command string or list.
        capture: If True, capture stdout/stderr.
        timeout: Timeout in seconds.
        cwd: Working directory for the command.

    Returns:
        dict with keys: success, stdout, stderr, returncode
    """
    try:
        result = subprocess.run(
            cmd,
            shell=isinstance(cmd, str),
            capture_output=capture,
            text=True,
            timeout=timeout,
            env=_get_env(),
            cwd=cwd,
        )
        return {
            "success": result.returncode == 0,
            "stdout": (result.stdout or "").strip() if capture else "",
            "stderr": (result.stderr or "").strip() if capture else "",
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Command timed out after {timeout}s",
            "returncode": -1,
        }
    except FileNotFoundError:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Command not found: {cmd}",
            "returncode": -1,
        }


def launch(cmd, cwd=None):
    """Launch a command as a detached background process (fire-and-forget).

    Used for launching GUI applications where we don't need to wait for
    exit or capture output.  Returns immediately.
    """
    try:
        subprocess.Popen(
            cmd,
            shell=isinstance(cmd, str),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
            env=_get_env(),
            cwd=cwd,
        )
        return {"success": True, "stdout": "", "stderr": "", "returncode": 0}
    except FileNotFoundError:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Command not found: {cmd}",
            "returncode": -1,
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1,
        }


def is_installed(name):
    """Check if a command-line tool is installed.

    Uses expanded PATH (same as run()) so it finds tools in
    /usr/local/bin, /opt/homebrew/bin, ~/.local/bin, etc.
    """
    return shutil.which(name, path=_get_env().get("PATH")) is not None


def get_version(name):
    """Get version string of an installed tool."""
    result = run(f"{name} --version")
    if result["success"]:
        return result["stdout"].split("\n")[0]
    return None


def _get_env():
    """Get environment with PATH expanded to common install locations."""
    env = os.environ.copy()
    extra_paths = [
        "/usr/local/bin",
        "/opt/homebrew/bin",
        os.path.expanduser("~/.local/bin"),
        os.path.expanduser("~/bin"),
    ]
    current = env.get("PATH", "")
    for p in extra_paths:
        if p not in current:
            current = f"{p}:{current}"
    env["PATH"] = current
    return env
