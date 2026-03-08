"""API endpoints for the setup wizard.

Handles requests from the browser-based wizard UI.
All endpoints return JSON responses.
"""

import json
import os
import platform
import shutil

from setup.wizard.utils.os_detect import get_os_info
from setup.wizard.utils.shell import run, is_installed, get_version
from setup.wizard.utils.config import save_env_var, get_suggested_paths, browse_folder


# Repository to fork/clone
REPO_OWNER = "meenusinha"
REPO_NAME = "BigProjPOC"
REPO_BRANCH = "template/agentic-workflow-gui"


def handle_api(path, body=None):
    """Route an API request to the right handler.

    Args:
        path: URL path (e.g., "/api/os-info")
        body: Parsed JSON body for POST requests

    Returns:
        dict to be serialized as JSON response
    """
    routes = {
        "/api/os-info": api_os_info,
        "/api/prerequisites/status": api_prerequisites_status,
        "/api/prerequisites/install": api_prerequisites_install,
        "/api/github/auth-status": api_github_auth_status,
        "/api/github/login": api_github_login,
        "/api/github/token": api_github_token,
        "/api/github/fork-clone": api_github_fork_clone,
        "/api/llm/configure": api_llm_configure,
        "/api/tools/list": api_tools_list,
        "/api/tools/check": api_tools_check,
        "/api/tools/install": api_tools_install,
        "/api/tools/launch": api_tools_launch,
        "/api/local/copy": api_local_copy,
        "/api/paths/suggested": api_suggested_paths,
        "/api/paths/browse": api_browse_folder,
        "/api/wizard/minimize": api_wizard_minimize,
        "/api/shutdown": api_shutdown,
        "/api/debug": api_debug,
    }

    handler = routes.get(path)
    if not handler:
        return {"error": f"Unknown endpoint: {path}"}

    try:
        if body is not None:
            return handler(body)
        return handler()
    except Exception as e:
        return {"error": str(e)}


# --- OS Info ---

def api_os_info():
    """Return detected OS information including user's original working directory."""
    info = get_os_info()
    info["user_cwd"] = os.environ.get("WIZARD_USER_CWD", os.path.expanduser("~"))
    return info


# --- Prerequisites ---

def api_prerequisites_status():
    """Check installation status of all prerequisites."""
    # Check tkinter importability (works cross-platform)
    try:
        import importlib
        tkinter_available = importlib.util.find_spec("tkinter") is not None
    except Exception:
        tkinter_available = False

    return {
        "git": {
            "installed": is_installed("git"),
            "version": get_version("git"),
        },
        "gh": {
            "installed": is_installed("gh"),
            "version": get_version("gh"),
        },
        "python-tk": {
            "installed": tkinter_available,
            "version": "bundled" if tkinter_available else None,
        },
    }


def api_prerequisites_install(body):
    """Install a prerequisite tool.

    body: {"tool": "git" | "gh" | "python-tk"}
    """
    tool = body.get("tool")
    installer = _get_installer()

    if tool == "git":
        return installer.install_git()
    elif tool == "python-tk":
        return installer.install_tkinter()
    elif tool == "gh":
        return installer.install_gh()
    return {"success": False, "message": f"Unknown tool: {tool}"}


# --- GitHub Account ---

def api_github_auth_status():
    """Check if user is authenticated with GitHub CLI."""
    if not is_installed("gh"):
        return {"authenticated": False, "reason": "gh not installed"}

    result = run("gh auth status")
    if result["success"]:
        # Extract username from output
        output = result["stdout"] + result["stderr"]  # gh prints to stderr
        username = ""
        for line in output.split("\n"):
            if "Logged in to" in line and "account" in line.lower():
                parts = line.split()
                for i, p in enumerate(parts):
                    if p == "as":
                        username = parts[i + 1].strip("()")
                        break
            elif "Logged in to" in line:
                # Try to extract username
                for part in line.split():
                    if part.startswith("@") or (not part.startswith("-") and "." not in part and len(part) > 1):
                        pass
        return {"authenticated": True, "username": username, "output": output}

    return {
        "authenticated": False,
        "reason": "Not authenticated",
        "output": result["stderr"],
    }


def api_github_login(body=None):
    """Initiate GitHub login via device code flow.

    Runs 'gh auth login' in the background, captures the device code and
    verification URL, and returns them so the wizard UI can display them.
    The user opens the URL in their browser and enters the code manually.
    """
    import subprocess
    import threading
    import re

    if not is_installed("gh"):
        return {"success": False, "message": "GitHub CLI is not installed"}

    # We need to run gh auth login and capture the one-time code it prints.
    # gh prints the code and URL to stderr, then waits for completion.
    # We use a background thread so we can return the code to the UI immediately.

    # Store process reference for polling
    if not hasattr(api_github_login, '_process'):
        api_github_login._process = None
        api_github_login._output = ""
        api_github_login._done = False
        api_github_login._success = False

    # If already running, return current status
    if api_github_login._process and api_github_login._process.poll() is None:
        return {
            "success": True,
            "status": "waiting",
            "message": "Login in progress — complete it in your browser.",
            "output": api_github_login._output,
        }

    # Check if previous run completed
    if api_github_login._done:
        api_github_login._done = False
        proc = api_github_login._process
        api_github_login._process = None
        if api_github_login._success:
            return {"success": True, "status": "complete", "message": "Successfully logged in to GitHub"}
        return {"success": False, "status": "failed", "message": "Login failed or was cancelled."}

    # Start new login process
    from setup.wizard.utils.shell import _get_env
    env = _get_env()
    # Force no browser auto-open on some systems; user opens manually
    env["BROWSER"] = ""
    env["GH_BROWSER"] = " "

    proc = subprocess.Popen(
        ["gh", "auth", "login", "--hostname", "github.com", "--web", "--git-protocol", "https"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        text=True,
        env=env,
    )
    api_github_login._process = proc
    api_github_login._output = ""

    def reader():
        """Read stderr in background to capture device code."""
        output_lines = []
        try:
            for line in proc.stderr:
                output_lines.append(line)
                api_github_login._output = "".join(output_lines)
            proc.wait()
        except Exception:
            pass
        api_github_login._success = proc.returncode == 0
        api_github_login._done = True

    t = threading.Thread(target=reader, daemon=True)
    t.start()

    # Wait briefly for gh to print the device code
    import time
    for _ in range(20):
        time.sleep(0.5)
        output = api_github_login._output
        if "one-time code" in output.lower() or "https://github.com/login/device" in output:
            break

    output = api_github_login._output

    # Parse out the code and URL
    code_match = re.search(r'([A-F0-9]{4}-[A-F0-9]{4})', output)
    url_match = re.search(r'(https://github\.com/login/device\S*)', output)

    return {
        "success": True,
        "status": "started",
        "device_code": code_match.group(1) if code_match else "",
        "verification_url": url_match.group(1) if url_match else "https://github.com/login/device",
        "message": "Enter the code at the URL below to sign in.",
        "raw_output": output,
    }


def api_github_token(body):
    """Save GitHub token to environment.

    body: {"token": "ghp_..."}
    """
    token = body.get("token", "").strip()
    if not token:
        return {"success": False, "message": "Token is required"}

    # Authenticate gh CLI with the token (cross-platform: use stdin pipe)
    import subprocess
    from setup.wizard.utils.shell import _get_env
    try:
        env = _get_env()
        env.pop('GITHUB_TOKEN', None)
        proc = subprocess.run(
            ["gh", "auth", "login", "--with-token"],
            input=token,
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        if proc.returncode != 0:
            stderr = (proc.stderr or "").strip()
            return {"success": False, "message": f"Token authentication failed: {stderr}"}
    except FileNotFoundError:
        return {"success": False, "message": "GitHub CLI (gh) is not installed"}
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Token authentication timed out"}

    # Save to environment
    env_result = save_env_var("GITHUB_TOKEN", token)

    return {
        "success": True,
        "message": "GitHub token saved and gh authenticated",
        "env": env_result,
    }


# --- Fork & Clone ---

def api_github_fork_clone(body):
    """Fork the template repo and clone to user's chosen location.

    body: {"path": "/Users/me/Desktop", "project_name": "my-project"}
    """
    dest_parent = body.get("path", "")
    project_name = body.get("project_name", REPO_NAME)
    dest = os.path.join(dest_parent, project_name)

    if os.path.exists(dest):
        return {"success": False, "message": f"Directory already exists: {dest}"}

    if not is_installed("gh"):
        return {"success": False, "message": "GitHub CLI is required for fork & clone"}

    # Detect the authenticated GitHub username
    whoami = run("gh api user --jq .login", timeout=15)
    gh_user = whoami["stdout"].strip() if whoami["success"] else ""

    # Fork the repo (if not already forked)
    run(f"gh repo fork {REPO_OWNER}/{REPO_NAME} --clone=false", timeout=60)

    # Strategy 1: Clone from user's fork
    clone_result = {"success": False, "stderr": ""}
    if gh_user:
        clone_result = run(
            f'gh repo clone {gh_user}/{REPO_NAME} "{dest}" -- --branch {REPO_BRANCH}',
            timeout=120,
        )

    # Strategy 2: If branch missing in fork, sync fork then retry
    if not clone_result["success"] and gh_user:
        run(f"gh repo sync {gh_user}/{REPO_NAME} --branch {REPO_BRANCH} --source {REPO_OWNER}/{REPO_NAME}", timeout=60)
        clone_result = run(
            f'gh repo clone {gh_user}/{REPO_NAME} "{dest}" -- --branch {REPO_BRANCH}',
            timeout=120,
        )

    # Strategy 3: Clone from original repo, then fix remotes to point to fork
    if not clone_result["success"]:
        clone_result = run(
            f'gh repo clone {REPO_OWNER}/{REPO_NAME} "{dest}" -- --branch {REPO_BRANCH}',
            timeout=120,
        )

    if not clone_result["success"]:
        return {
            "success": False,
            "message": f"Clone failed: {clone_result['stderr']}",
        }

    # Ensure origin points to user's fork, not the template repo
    origin_check = run(f'git -C "{dest}" remote get-url origin', timeout=10)
    origin_url = origin_check["stdout"].strip() if origin_check["success"] else ""
    if gh_user and gh_user.lower() not in origin_url.lower():
        # origin points to template repo — fix it to point to user's fork
        run(f'git -C "{dest}" remote set-url origin https://github.com/{gh_user}/{REPO_NAME}.git', timeout=10)
        # Add upstream for pulling template updates
        run(f'git -C "{dest}" remote add upstream https://github.com/{REPO_OWNER}/{REPO_NAME}.git', timeout=10)

    # Set gh repo default so agents can create PRs without --repo flag
    repo_owner = gh_user if gh_user else REPO_OWNER
    run(f'gh repo set-default {repo_owner}/{REPO_NAME}', timeout=15, cwd=dest)

    # Write workflow-config.json for github mode
    config = {"mode": "github", "setup_complete": True}
    config_path = os.path.join(dest, "workflow-config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    return {
        "success": True,
        "message": f"Project cloned to {dest}",
        "project_path": dest,
    }


# --- LLM Provider ---

def api_llm_configure(body):
    """Configure LLM provider and API key.

    body: {"provider": "openai", "api_key": "sk-...", "azure_endpoint": "..." (optional)}
    """
    provider = body.get("provider", "").strip()
    api_key = body.get("api_key", "").strip()
    azure_endpoint = body.get("azure_endpoint", "").strip()

    if not provider:
        return {"success": False, "message": "Provider is required"}

    results = []

    # Save provider
    r = save_env_var("LLM_PROVIDER", provider)
    results.append(r)

    # Save API key (unless copilot which doesn't need one)
    if provider != "copilot" and api_key:
        r = save_env_var("LLM_API_KEY", api_key)
        results.append(r)

    # Azure needs endpoint
    if provider == "azure" and azure_endpoint:
        r = save_env_var("AZURE_OPENAI_ENDPOINT", azure_endpoint)
        results.append(r)

    # Also set as GitHub secrets if gh is available and authenticated
    github_secrets_status = {"attempted": False, "results": []}
    if is_installed("gh"):
        auth = run("gh auth status")
        if auth["success"]:
            github_secrets_status["attempted"] = True

            # Detect the authenticated GitHub user to build the target repo slug.
            # Always pass --repo explicitly to gh secret set so the wizard works
            # correctly from any directory (temp or otherwise), never relying on
            # gh repo set-default which is context-dependent.
            whoami = run("gh api user --jq .login", timeout=15)
            repo_owner = whoami["stdout"].strip() if whoami["success"] else REPO_OWNER
            target_repo = f"{repo_owner}/{REPO_NAME}"

            # Set secrets with error checking.
            # Use list form (shell=False) so the key value is passed verbatim —
            # no shell expansion of $ or other special characters that would
            # silently corrupt the stored secret.
            secret_provider = run(['gh', 'secret', 'set', 'LLM_PROVIDER', '--body', provider, '--repo', target_repo], timeout=30)
            github_secrets_status["results"].append({
                "secret": "LLM_PROVIDER",
                "success": secret_provider["success"],
                "error": secret_provider["stderr"].strip() if not secret_provider["success"] else "",
            })

            if provider != "copilot" and api_key:
                secret_key = run(['gh', 'secret', 'set', 'LLM_API_KEY', '--body', api_key, '--repo', target_repo], timeout=30)
                github_secrets_status["results"].append({
                    "secret": "LLM_API_KEY",
                    "success": secret_key["success"],
                    "error": secret_key["stderr"].strip() if not secret_key["success"] else "",
                })

            if provider == "azure" and azure_endpoint:
                secret_endpoint = run(['gh', 'secret', 'set', 'AZURE_OPENAI_ENDPOINT', '--body', azure_endpoint, '--repo', target_repo], timeout=30)
                github_secrets_status["results"].append({
                    "secret": "AZURE_OPENAI_ENDPOINT",
                    "success": secret_endpoint["success"],
                    "error": secret_endpoint["stderr"].strip() if not secret_endpoint["success"] else "",
                })

    all_ok = all(r.get("success", False) for r in results)
    secrets_ok = all(s["success"] for s in github_secrets_status["results"]) if github_secrets_status["results"] else True
    message = f"LLM provider '{provider}' configured"
    if not all_ok:
        message = "Some local settings failed"
    elif not secrets_ok:
        failed = [s["secret"] for s in github_secrets_status["results"] if not s["success"]]
        message = f"LLM provider '{provider}' configured locally, but GitHub secrets failed: {', '.join(failed)}"

    return {
        "success": all_ok,
        "message": message,
        "details": results,
        "github_secrets": github_secrets_status,
    }


# --- AI Tools ---

TOOLS = [
    {
        "id": "cursor",
        "name": "Cursor",
        "description": "AI-powered code editor (GUI)",
        "difficulty": "Easiest",
        "instruction_file": ".cursorrules",
    },
    {
        "id": "windsurf",
        "name": "Windsurf",
        "description": "AI-powered code editor by Codeium (GUI)",
        "difficulty": "Easiest",
        "instruction_file": ".windsurfrules",
    },
    {
        "id": "claude-code",
        "name": "Claude Code",
        "description": "Anthropic's CLI for Claude (Terminal)",
        "difficulty": "Easy",
        "instruction_file": "CLAUDE.md",
    },
    {
        "id": "vscode",
        "name": "VS Code + Continue",
        "description": "VS Code with Continue AI extension",
        "difficulty": "Easy",
        "instruction_file": ".continuerules",
    },
    {
        "id": "copilot",
        "name": "VS Code + GitHub Copilot",
        "description": "VS Code with GitHub Copilot extension (GUI)",
        "difficulty": "Easiest",
        "instruction_file": ".github/copilot-instructions.md",
    },
    {
        "id": "aider",
        "name": "Aider",
        "description": "AI pair programming in terminal",
        "difficulty": "Easy",
        "instruction_file": ".aider.conf.yml",
    },
]


def api_tools_list():
    """Return list of available AI tools."""
    return {"tools": TOOLS}


def api_tools_check(body):
    """Check if an AI tool is already installed.

    body: {"tool": "cursor"}
    """
    tool = body.get("tool")
    installer = _get_installer()
    return installer.check_ai_tool(tool)


def api_tools_install(body):
    """Install selected AI tool.

    body: {"tool": "cursor"}
    """
    tool = body.get("tool")
    installer = _get_installer()
    return installer.install_ai_tool(tool)


def api_tools_launch(body):
    """Launch AI tool at the project path.

    body: {"tool": "cursor", "project_path": "/path/to/project"}
    """
    tool = body.get("tool")
    project_path = body.get("project_path")

    if not project_path or not os.path.isdir(project_path):
        return {"success": False, "message": f"Invalid project path: {project_path}"}

    installer = _get_installer()
    return installer.launch_ai_tool(tool, project_path)


# --- Local Mode ---

def api_local_copy(body):
    """Copy project files to user's chosen location (local mode, no git).

    Copies the project, then overlays local-mode workflow files that remove
    all git/branch/PR instructions, and writes workflow-config.json.

    body: {"path": "/Users/me/Desktop", "project_name": "my-project"}
    """
    dest_parent = body.get("path", "")
    project_name = body.get("project_name", REPO_NAME)
    dest = os.path.join(dest_parent, project_name)

    if os.path.exists(dest):
        return {"success": False, "message": f"Directory already exists: {dest}"}

    # The repo was already extracted to a temp dir by setup.sh
    # That path is passed as an env var
    source = os.environ.get("WIZARD_REPO_PATH", "")
    if not source or not os.path.isdir(source):
        return {
            "success": False,
            "message": "Source repo not found. Please re-run the setup script.",
        }

    try:
        # 1. Copy base project (skip .git and setup/ dirs)
        shutil.copytree(
            source, dest,
            ignore=shutil.ignore_patterns(".git", "setup"),
        )

        # 2. Overlay local-mode workflow files
        local_src = os.path.join(source, "setup", "workflow", "local")
        if os.path.isdir(local_src):
            _overlay_files(local_src, dest)

        # 3. Remove GitHub-specific files not needed in local mode
        for path in [
            os.path.join(dest, ".github", "workflows"),
            os.path.join(dest, ".github", "CODEOWNERS"),
            os.path.join(dest, ".github", "scripts"),
        ]:
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.isfile(path):
                os.remove(path)

        # 4. Write workflow-config.json
        config = {"mode": "local", "setup_complete": True}
        config_path = os.path.join(dest, "workflow-config.json")
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        return {
            "success": True,
            "message": f"Project copied to {dest}",
            "project_path": dest,
        }
    except Exception as e:
        return {"success": False, "message": f"Copy failed: {str(e)}"}


def _overlay_files(src_dir, dest_dir):
    """Recursively copy files from src_dir into dest_dir, overwriting."""
    for item in os.listdir(src_dir):
        s = os.path.join(src_dir, item)
        d = os.path.join(dest_dir, item)
        if os.path.isdir(s):
            os.makedirs(d, exist_ok=True)
            _overlay_files(s, d)
        else:
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)


# --- Suggested Paths ---

def api_suggested_paths():
    """Return suggested project locations."""
    return {"paths": get_suggested_paths()}


def api_browse_folder():
    """Open native OS folder picker dialog and return selected path."""
    return browse_folder()


# --- Wizard Control ---

def api_wizard_minimize():
    """Minimize the wizard browser window so the launched tool is visible."""
    installer = _get_installer()
    return installer.minimize_wizard_window()


# --- Shutdown ---

_shutdown_callback = None


def set_shutdown_callback(callback):
    """Register a callback to shut down the server."""
    global _shutdown_callback
    _shutdown_callback = callback


def api_shutdown():
    """Shut down the wizard server."""
    if _shutdown_callback:
        _shutdown_callback()
    return {"success": True, "message": "Server shutting down"}


def api_debug():
    """Return diagnostic info about VS Code detection (for troubleshooting)."""
    from setup.wizard.utils.shell import _get_env
    info = get_os_info()
    env_path = _get_env().get("PATH", "")
    diag = {
        "os": info.get("os"),
        "expanded_path": env_path,
        "which_code": run("which code 2>/dev/null")["stdout"],
        "which_code_login_shell": run("bash -lc 'which code 2>/dev/null'")["stdout"],
        "snap_exists": os.path.isfile("/snap/bin/code"),
        "usr_bin_code": os.path.isfile("/usr/bin/code"),
        "usr_share_code": os.path.isfile("/usr/share/code/code"),
        "usr_share_code_bin": os.path.isfile("/usr/share/code/bin/code"),
        "dpkg_query": run("dpkg -L code 2>/dev/null | grep 'bin/code'")["stdout"],
        "code_version": "v3-login-shell-fallback",
    }
    installer = _get_installer()
    if hasattr(installer, '_find_vscode_cmd'):
        diag["find_vscode_cmd_result"] = installer._find_vscode_cmd()
    return diag


# --- Helpers ---

def _get_installer():
    """Get the OS-specific installer module."""
    info = get_os_info()
    os_type = info["os"]

    if os_type == "mac":
        from setup.wizard.installers import mac
        return mac
    elif os_type == "linux":
        from setup.wizard.installers import linux
        return linux
    elif os_type == "windows":
        from setup.wizard.installers import windows
        return windows
    else:
        raise RuntimeError(f"Unsupported OS: {os_type}")
