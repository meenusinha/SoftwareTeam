"""Configuration and environment variable management."""

import os
import platform


def save_env_var(name, value):
    """Save an environment variable persistently for the current OS.

    Returns dict with success status and message.
    """
    system = platform.system()

    # Set for current process
    os.environ[name] = value

    if system in ("Darwin", "Linux"):
        return _save_unix_env(name, value)
    elif system == "Windows":
        return _save_windows_env(name, value)

    return {"success": False, "message": f"Unsupported OS: {system}"}


def _save_unix_env(name, value):
    """Append export to shell profile on Mac/Linux."""
    shell = os.environ.get("SHELL", "/bin/bash")
    if "zsh" in shell:
        profile = os.path.expanduser("~/.zshrc")
    else:
        profile = os.path.expanduser("~/.bashrc")

    export_line = f'export {name}="{value}"'

    # Check if already set
    try:
        with open(profile, "r") as f:
            content = f.read()
        if f'export {name}=' in content:
            # Replace existing line
            lines = content.split("\n")
            lines = [
                export_line if line.strip().startswith(f"export {name}=") else line
                for line in lines
            ]
            with open(profile, "w") as f:
                f.write("\n".join(lines))
            return {
                "success": True,
                "message": f"Updated {name} in {profile}",
                "profile": profile,
            }
    except FileNotFoundError:
        pass

    # Append new
    with open(profile, "a") as f:
        f.write(f"\n{export_line}\n")

    return {
        "success": True,
        "message": f"Added {name} to {profile}",
        "profile": profile,
    }


def _save_windows_env(name, value):
    """Set user environment variable on Windows."""
    import subprocess

    result = subprocess.run(
        ["setx", name, value],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return {
            "success": True,
            "message": f"Set {name} as user environment variable",
        }
    return {
        "success": False,
        "message": f"Failed to set {name}: {result.stderr}",
    }


def get_suggested_paths():
    """Return suggested project locations for the current OS."""
    home = os.path.expanduser("~")
    system = platform.system()

    paths = [
        {"path": os.path.join(home, "Desktop"), "label": "Desktop"},
        {"path": os.path.join(home, "Documents"), "label": "Documents"},
        {"path": home, "label": "Home directory"},
    ]

    if system == "Windows":
        paths.append({"path": "C:\\Projects", "label": "C:\\Projects"})

    # Filter to paths that exist
    return [p for p in paths if os.path.isdir(p["path"])]


def browse_folder():
    """Open a native OS folder picker dialog and return the selected path.

    Returns dict with 'success', 'path' (empty string if cancelled), and
    optional 'message' on failure.
    """
    import subprocess
    import shutil as _shutil
    system = platform.system()

    # --- Windows: PowerShell FolderBrowserDialog with a topmost owner form ---
    # Tried first because tkinter dialogs on Windows often appear behind the
    # browser window even with -topmost. A hidden TopMost Form as owner forces
    # the dialog to the front reliably.
    if system == "Windows":
        ps_script = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "$owner = [System.Windows.Forms.Form]::new(); "
            "$owner.TopMost = $true; "
            "$f = [System.Windows.Forms.FolderBrowserDialog]::new(); "
            "$f.Description = 'Choose project location'; "
            "$f.SelectedPath = [System.Environment]::GetFolderPath('Desktop'); "
            "if ($f.ShowDialog($owner) -eq [System.Windows.Forms.DialogResult]::OK) "
            "{ Write-Output $f.SelectedPath }; "
            "$owner.Dispose()"
        )
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                capture_output=True, text=True, timeout=300,
            )
            if result.returncode == 0 and result.stdout.strip():
                return {"success": True, "path": result.stdout.strip()}
            if result.returncode == 0:
                return {"success": True, "path": ""}  # user cancelled
        except Exception:
            pass  # fall through to tkinter

    # --- macOS: osascript (must come before tkinter on macOS) ---
    # tk.Tk() creates an NSWindow which macOS requires on the main thread.
    # The wizard HTTP server calls this from a background thread, which crashes
    # the whole Python process with NSInternalInconsistencyException.
    # osascript spawns its own subprocess (its own main thread) — safe from any thread.
    if system == "Darwin":
        try:
            result = subprocess.run(
                ["osascript",
                 "-e", 'set theFolder to choose folder with prompt "Choose project location"',
                 "-e", "POSIX path of theFolder"],
                capture_output=True, text=True, timeout=300,
            )
            if result.returncode == 0 and result.stdout.strip():
                return {"success": True, "path": result.stdout.strip().rstrip("/")}
            if result.returncode == 0:
                return {"success": True, "path": ""}  # user cancelled
        except Exception:
            pass
        return {
            "success": False,
            "path": "",
            "message": "Could not open folder picker. Please type the path directly into the text box.",
        }

    # --- tkinter (Linux with display, and Windows fallback) ---
    # NOT used on macOS — see above.
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes("-topmost", 1)  # bring above other windows
        root.update()                       # process pending events so topmost takes effect
        folder = filedialog.askdirectory(
            parent=root,
            title="Choose project location",
            initialdir=os.path.expanduser("~"),
        )
        root.destroy()
        if folder:
            return {"success": True, "path": folder}
        return {"success": True, "path": ""}  # user cancelled
    except Exception:
        pass

    # --- Linux: zenity or kdialog ---
    if system == "Linux":
        for cmd, args in [
            ("zenity", ["zenity", "--file-selection", "--directory",
                        "--title=Choose project location"]),
            ("kdialog", ["kdialog", "--getexistingdirectory",
                         os.path.expanduser("~")]),
        ]:
            if _shutil.which(cmd):
                try:
                    result = subprocess.run(args, capture_output=True, text=True, timeout=300)
                    if result.returncode == 0 and result.stdout.strip():
                        return {"success": True, "path": result.stdout.strip()}
                except Exception:
                    continue

    return {
        "success": False,
        "path": "",
        "message": (
            "Could not open a folder picker on this system. "
            "Please type the destination path directly into the text box."
        ),
    }
