"""Shell command execution utilities."""

import subprocess
import shutil
import os
import threading
import time as _time

# Thread-local storage for live log streaming during background installs
_thread_local = threading.local()


def set_log_context(lines_list):
    """Attach a list to the current thread; run() will append output lines to it."""
    _thread_local.log_lines = lines_list


def clear_log_context():
    """Remove the log context from the current thread."""
    _thread_local.log_lines = None


def run(cmd, capture=True, timeout=120, cwd=None):
    """Run a shell command and return result dict.

    Args:
        cmd: Command string or list.
        capture: If True, capture stdout/stderr.
        timeout: Timeout in seconds.
        cwd: Working directory for the command.

    Returns:
        dict with keys: success, stdout, stderr, returncode

    When a log context is active on the calling thread (set via set_log_context),
    output is streamed line-by-line into that list in real time so the UI can
    poll for progress.
    """
    log_lines = getattr(_thread_local, 'log_lines', None)

    if log_lines is not None:
        # Streaming mode — log the command then stream stdout+stderr line by line
        cmd_str = cmd if isinstance(cmd, str) else ' '.join(str(c) for c in cmd)
        log_lines.append(f"$ {cmd_str}")
        try:
            proc = subprocess.Popen(
                cmd,
                shell=isinstance(cmd, str),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # merge stderr into stdout
                text=True,
                env=_get_env(),
                cwd=cwd,
            )
            all_output = []
            deadline = _time.monotonic() + (timeout or 120)
            for line in proc.stdout:
                line = line.rstrip('\n')
                all_output.append(line)
                if line:
                    log_lines.append(line)
                if _time.monotonic() > deadline:
                    proc.kill()
                    msg = f"[timed out after {timeout}s]"
                    log_lines.append(msg)
                    return {"success": False, "stdout": "\n".join(all_output),
                            "stderr": msg, "returncode": -1}
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            combined = "\n".join(all_output)
            return {
                "success": proc.returncode == 0,
                "stdout": combined if capture else "",
                "stderr": "",
                "returncode": proc.returncode,
            }
        except FileNotFoundError:
            msg = f"Command not found: {cmd_str}"
            log_lines.append(f"[error] {msg}")
            return {"success": False, "stdout": "", "stderr": msg, "returncode": -1}
        except Exception as e:
            log_lines.append(f"[error] {e}")
            return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}
    else:
        # Original blocking mode (unchanged)
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
