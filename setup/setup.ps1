# =============================================================================
# Setup Wizard - Windows Entry Point (PowerShell)
#
# Usage (one-liner for users):
#   irm https://raw.githubusercontent.com/meenusinha/SoftwareTeam/main/setup/setup.ps1 | iex
#
# What this script does:
#   1. Detects Windows version
#   2. Checks/installs Python 3
#   3. Downloads the project repo as a zip
#   4. Extracts it to a temp directory
#   5. Launches the setup wizard (opens in browser)
# =============================================================================

$ErrorActionPreference = "Stop"

$RepoOwner = "meenusinha"
$RepoName = "SoftwareTeam"
$RepoBranch = "main"
$ZipUrl = "https://github.com/$RepoOwner/$RepoName/archive/refs/heads/$RepoBranch.zip"

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Blue }
function Write-Ok($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }

# --- Detect Windows version ---
function Get-WindowsInfo {
    $version = [System.Environment]::OSVersion.Version
    Write-Info "Detected: Windows $($version.Major).$($version.Minor) (Build $($version.Build))"
}

# --- Helper: find Python by searching common install directories ---
function Find-PythonInPaths {
    # Search common Windows Python installation directories
    $searchPatterns = @(
        "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe",
        "$env:ProgramFiles\Python3*\python.exe",
        "$env:ProgramFiles\Python\Python3*\python.exe",
        "C:\Python3*\python.exe"
    )
    foreach ($pattern in $searchPatterns) {
        $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Sort-Object Name -Descending | Select-Object -First 1
        if ($found) { return $found.FullName }
    }
    return $null
}

# --- Check/Install Python 3 ---
function Ensure-Python {
    # Use Continue to prevent errors from killing the script (especially under irm | iex)
    $prevPref = $ErrorActionPreference
    $ErrorActionPreference = "Continue"

    # Strategy 1: Check py launcher (most reliable on Windows)
    $pyCmd = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCmd -and $pyCmd.Source -notlike "*WindowsApps*") {
        try {
            $pyVersion = & py -3 --version 2>&1
            if ("$pyVersion" -match "Python 3") {
                Write-Ok "Python 3 found: $pyVersion (py launcher)"
                $ErrorActionPreference = $prevPref
                return "py -3"
            }
        } catch { }
    }

    # Strategy 2: Check python/python3 on PATH (exclude WindowsApps stubs)
    foreach ($name in @("python", "python3")) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd -and $cmd.Source -notlike "*WindowsApps*") {
            try {
                $pyVersion = & $name --version 2>&1
                if ("$pyVersion" -match "Python 3") {
                    Write-Ok "Python 3 found: $pyVersion"
                    $ErrorActionPreference = $prevPref
                    return $name
                }
            } catch { }
        }
    }

    # Strategy 3: Search common install directories directly
    $directPath = Find-PythonInPaths
    if ($directPath) {
        try {
            $pyVersion = & $directPath --version 2>&1
            if ("$pyVersion" -match "Python 3") {
                Write-Ok "Python 3 found: $pyVersion (at $directPath)"
                $ErrorActionPreference = $prevPref
                return $directPath
            }
        } catch { }
    }

    # Strategy 4: Try WindowsApps python (might be real Store-installed Python, not just a redirect stub)
    foreach ($name in @("python", "python3")) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) {
            try {
                $pyVersion = & $name --version 2>&1
                if ("$pyVersion" -match "Python 3") {
                    Write-Ok "Python 3 found: $pyVersion (via Windows Store)"
                    $ErrorActionPreference = $prevPref
                    return $name
                }
            } catch { }
        }
    }

    $ErrorActionPreference = $prevPref

    # Need to install Python 3
    Write-Warn "Python 3 not found. Installing automatically..."

    $pyInstallLog = "$env:TEMP\python-install.log"
    $pyInstalled  = $false

    # Helper: show elapsed time while a process runs, kill it if it exceeds timeout.
    # Returns $true if the process exited with code 0, $false otherwise.
    function Show-InstallerProgress($proc, $timeoutSec, $label) {
        $interval = 5
        $elapsed  = 0
        Write-Host -NoNewline "  $label"
        while (-not $proc.WaitForExit($interval * 1000)) {
            $elapsed += $interval
            Write-Host -NoNewline " ${elapsed}s/${timeoutSec}s..."
            if ($elapsed -ge $timeoutSec) {
                Write-Host " [timed out after ${timeoutSec}s]"
                try { $proc.Kill() } catch { }
                return $false
            }
        }
        Write-Host " [done in ${elapsed}s]"
        return ($proc.ExitCode -eq 0)
    }

    # --- Method 1: winget ---
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        Write-Info "Installing Python 3 via winget..."
        $wingetOut = & winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Ok "Python 3 installed via winget."
            $pyInstalled = $true
        } else {
            Write-Warn "winget failed (exit code $LASTEXITCODE). Output:"
            $wingetOut | Select-Object -Last 10 | ForEach-Object { Write-Host "  $_" -ForegroundColor DarkGray }
        }
    }

    # --- Method 2: direct installer, user-level (no UAC needed) ---
    if (-not $pyInstalled) {
        Write-Info "Downloading Python installer..."
        $installerUrl  = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
        $installerPath = "$env:TEMP\python-installer.exe"
        try {
            $ProgressPreference = 'SilentlyContinue'
            Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
            $ProgressPreference = 'Continue'
        } catch {
            Write-Warn "Download failed: $_"
        }

        if (Test-Path $installerPath) {
            Write-Info "Running Python installer — attempt 1 (user-level, no admin needed)..."
            $proc1 = Start-Process -FilePath $installerPath `
                -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 /log `"$pyInstallLog`"" `
                -PassThru
            if (Show-InstallerProgress $proc1 120 "Installing") {
                $pyInstalled = $true
                Write-Ok "Python installed (user-level)."
            } else {
                $ec1 = if ($proc1.HasExited) { $proc1.ExitCode } else { "timed out" }
                Write-Warn "Attempt 1 failed (exit code: $ec1). Installer log:"
                if (Test-Path $pyInstallLog) {
                    Get-Content $pyInstallLog -ErrorAction SilentlyContinue |
                        Select-Object -Last 15 |
                        ForEach-Object { Write-Host "  $_" -ForegroundColor DarkGray }
                }
            }

            # --- Method 3: same installer, system-level (may trigger UAC prompt) ---
            if (-not $pyInstalled) {
                Write-Info "Retrying with elevated permissions — a UAC prompt may appear..."
                try {
                    $proc2 = Start-Process -FilePath $installerPath `
                        -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 /log `"$pyInstallLog`"" `
                        -Verb RunAs -PassThru -ErrorAction Stop
                    if (Show-InstallerProgress $proc2 120 "Installing (elevated)") {
                        $pyInstalled = $true
                        Write-Ok "Python installed (system-level)."
                    } else {
                        $ec2 = if ($proc2.HasExited) { $proc2.ExitCode } else { "timed out" }
                        Write-Warn "Attempt 2 failed (exit code: $ec2). Installer log:"
                        if (Test-Path $pyInstallLog) {
                            Get-Content $pyInstallLog -ErrorAction SilentlyContinue |
                                Select-Object -Last 15 |
                                ForEach-Object { Write-Host "  $_" -ForegroundColor DarkGray }
                        }
                    }
                } catch {
                    Write-Warn "Could not launch elevated installer: $_"
                }
            }

            Remove-Item $installerPath -ErrorAction SilentlyContinue
            Remove-Item $pyInstallLog -ErrorAction SilentlyContinue
        }
    }

    # --- Method 4: embeddable Python (no installer, no admin required) ---
    if (-not $pyInstalled) {
        Write-Info "Trying Python embeddable package (no installation or admin required)..."
        $embedUrl = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-embed-amd64.zip"
        $embedZip = "$env:TEMP\python-embed.zip"
        $embedDir = "$env:TEMP\python-embed-auto"
        try {
            $ProgressPreference = 'SilentlyContinue'
            Invoke-WebRequest -Uri $embedUrl -OutFile $embedZip -UseBasicParsing
            $ProgressPreference = 'Continue'
            if (Test-Path $embedDir) { Remove-Item $embedDir -Recurse -Force }
            Expand-Archive -Path $embedZip -DestinationPath $embedDir -Force
            Remove-Item $embedZip -ErrorAction SilentlyContinue

            # Uncomment 'import site' so pip and installed packages are accessible
            $pthFile = Get-ChildItem "$embedDir\python*._pth" -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($pthFile) {
                (Get-Content $pthFile.FullName) -replace '#import site', 'import site' |
                    Set-Content $pthFile.FullName
            }

            # Bootstrap pip
            Write-Info "Bootstrapping pip for embeddable Python..."
            $getPipPath = "$embedDir\get-pip.py"
            Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $getPipPath -UseBasicParsing
            & "$embedDir\python.exe" $getPipPath --quiet 2>&1 | Out-Null
            Remove-Item $getPipPath -ErrorAction SilentlyContinue

            $embedPython = "$embedDir\python.exe"
            if (Test-Path $embedPython) {
                Write-Ok "Python embeddable package ready."
                $ErrorActionPreference = $prevPref
                return $embedPython
            }
        } catch {
            Write-Warn "Embeddable Python setup failed: $_"
        }

        Write-Err "All automatic Python installation methods failed."
        Write-Err "Please check your internet connection and try running this script again."
        exit 1
    }

    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

    # Re-check using all strategies
    $ErrorActionPreference = "Continue"

    $pyCmd = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCmd) {
        try {
            $pyVersion = & py -3 --version 2>&1
            if ("$pyVersion" -match "Python 3") {
                Write-Ok "Python 3 ready: $pyVersion"
                $ErrorActionPreference = $prevPref
                return "py -3"
            }
        } catch { }
    }

    foreach ($name in @("python", "python3")) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) {
            try {
                $pyVersion = & $name --version 2>&1
                if ("$pyVersion" -match "Python 3") {
                    Write-Ok "Python 3 ready: $pyVersion"
                    $ErrorActionPreference = $prevPref
                    return $name
                }
            } catch { }
        }
    }

    $directPath = Find-PythonInPaths
    if ($directPath) {
        Write-Ok "Python 3 found at $directPath"
        $ErrorActionPreference = $prevPref
        return $directPath
    }

    $ErrorActionPreference = $prevPref
    Write-Err "Failed to find Python 3. Please install it from https://python.org and ensure 'Add to PATH' is checked."
    exit 1
}

# --- Download repo zip ---
function Download-Repo {
    $tempDir = New-Item -ItemType Directory -Path "$env:TEMP\wizard-$(Get-Random)" -Force
    $zipPath = "$tempDir\repo.zip"

    Write-Info "Downloading project files..."
    Invoke-WebRequest -Uri $ZipUrl -OutFile $zipPath

    Write-Info "Extracting..."
    Expand-Archive -Path $zipPath -DestinationPath $tempDir.FullName -Force
    Remove-Item $zipPath

    # Find extracted directory
    $repoDir = Get-ChildItem -Path $tempDir.FullName -Directory | Where-Object { $_.Name -like "$RepoName*" } | Select-Object -First 1

    if (-not $repoDir) {
        Write-Err "Failed to download project files."
        Remove-Item $tempDir.FullName -Recurse -Force
        exit 1
    }

    Write-Ok "Project files downloaded."

    # Set env var so wizard can find repo for local copy mode
    $env:WIZARD_REPO_PATH = $repoDir.FullName
    $env:WIZARD_USER_CWD = (Get-Location).Path

    return @{ TempDir = $tempDir.FullName; RepoDir = $repoDir.FullName }
}

# --- Launch wizard ---
function Launch-Wizard($python, $repoDir, $tempDir) {
    Write-Info "Starting setup wizard..."
    Write-Host ""
    Write-Host "============================================"
    Write-Host "  The wizard will open in your browser."
    Write-Host "  If it doesn't open automatically,"
    Write-Host "  look for the URL printed below."
    Write-Host "============================================"
    Write-Host ""

    # Run script directly to avoid 'setup' package name conflicts
    $env:PYTHONPATH = $repoDir
    $scriptPath = "$repoDir\setup\wizard\main.py"
    if ($python -eq "py -3") {
        & py -3 $scriptPath
    } elseif ($python -like "*\*") {
        # Full path to python.exe (from Find-PythonInPaths)
        & "$python" $scriptPath
    } else {
        & $python $scriptPath
    }

    # Cleanup
    Write-Info "Cleaning up temporary files..."
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Ok "Done!"
}

# --- Main ---
Write-Host ""
Write-Host "==============================="
Write-Host "  Project Setup Wizard"
Write-Host "==============================="
Write-Host ""

Get-WindowsInfo
$python = Ensure-Python
$paths = Download-Repo
Launch-Wizard $python $paths.RepoDir $paths.TempDir
