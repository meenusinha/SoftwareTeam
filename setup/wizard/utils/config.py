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

    # --- Windows: IFileOpenDialog (modern Explorer-style picker with address bar) ---
    # FolderBrowserDialog is the old XP-era tree picker with no address bar.
    # IFileOpenDialog with FOS_PICKFOLDERS gives the modern dialog where the
    # user can type or paste a path directly. Invoked via a base64-encoded
    # PowerShell script so here-strings (needed for Add-Type) work correctly.
    if system == "Windows":
        import base64
        ps_script = r"""
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public static class ModernFolderPicker {
    // IFileOpenDialog vtable: IUnknown (0-2) + IModalWindow.Show (3) +
    // IFileDialog methods (4-26) + IFileOpenDialog methods (27-28).
    [ComImport, Guid("D57C7288-D4AD-4768-BE02-9D969532D960"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IFileOpenDialog {
        [PreserveSig] int Show(IntPtr parent);
        [PreserveSig] int SetFileTypes(uint c, IntPtr r);
        [PreserveSig] int SetFileTypeIndex(uint i);
        [PreserveSig] int GetFileTypeIndex(out uint pi);
        [PreserveSig] int Advise(IntPtr pfde, out uint pdw);
        [PreserveSig] int Unadvise(uint dw);
        [PreserveSig] int SetOptions(uint fos);
        [PreserveSig] int GetOptions(out uint pfos);
        [PreserveSig] int SetDefaultFolder(IntPtr psi);
        [PreserveSig] int SetFolder(IntPtr psi);
        [PreserveSig] int GetFolder(out IntPtr ppsi);
        [PreserveSig] int GetCurrentSelection(out IntPtr ppsi);
        [PreserveSig] int SetFileName([MarshalAs(UnmanagedType.LPWStr)] string p);
        [PreserveSig] int GetFileName(out IntPtr p);
        [PreserveSig] int SetTitle([MarshalAs(UnmanagedType.LPWStr)] string p);
        [PreserveSig] int SetOkButtonLabel([MarshalAs(UnmanagedType.LPWStr)] string p);
        [PreserveSig] int SetFileNameLabel([MarshalAs(UnmanagedType.LPWStr)] string p);
        [PreserveSig] int GetResult(out IShellItem ppsi);
        [PreserveSig] int AddPlace(IntPtr psi, int fdap);
        [PreserveSig] int SetDefaultExtension([MarshalAs(UnmanagedType.LPWStr)] string p);
        [PreserveSig] int Close(int hr);
        [PreserveSig] int SetClientGuid(ref Guid g);
        [PreserveSig] int ClearClientData();
        [PreserveSig] int SetFilter(IntPtr pf);
        [PreserveSig] int GetResults(out IntPtr pp);
        [PreserveSig] int GetSelectedItems(out IntPtr pp);
    }
    [ComImport, Guid("43826D1E-E718-42EE-BC55-A1E261C37BFE"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    public interface IShellItem {
        [PreserveSig] int BindToHandler(IntPtr pbc, ref Guid bhid, ref Guid riid, out IntPtr ppv);
        [PreserveSig] int GetParent(out IShellItem ppsi);
        [PreserveSig] int GetDisplayName(uint sigdnName,
            [MarshalAs(UnmanagedType.LPWStr)] out string ppszName);
        [PreserveSig] int GetAttributes(uint sfgaoMask, out uint psfgaoAttribs);
        [PreserveSig] int Compare(IntPtr psi, uint hint, out int piOrder);
    }
    [ComImport, Guid("DC1C5A9C-E88A-4dde-A5A1-60F82A20AEF7")]
    class FileOpenDialogCoClass {}

    public static string Pick() {
        var d = (IFileOpenDialog) new FileOpenDialogCoClass();
        d.SetOptions(0x20u);  // FOS_PICKFOLDERS
        d.SetTitle("Choose project location");
        if (d.Show(IntPtr.Zero) != 0) return null;  // cancelled
        IShellItem item;
        if (d.GetResult(out item) != 0) return null;
        string path;
        item.GetDisplayName(0x80058000u, out path);  // SIGDN_FILESYSPATH
        return path;
    }
}
"@

$path = [ModernFolderPicker]::Pick()
if ($path) { Write-Output $path }
"""
        encoded_cmd = base64.b64encode(ps_script.encode("utf-16-le")).decode("ascii")
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-STA",
                 "-EncodedCommand", encoded_cmd],
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
