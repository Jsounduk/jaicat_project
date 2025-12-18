<#  Jaicat Repo Refactor (archive + import unification)
    - Moves deprecated/duplicate files into archive\Incubate\<timestamp>
    - Updates imports across all .py files
    - Optionally migrates computer_vision\oneDrive.py to services\one_drive.py
    - Creates a change log

    Usage:
      1) Save as refactor_jaicat.ps1 at the repo root or anywhere.
      2) Open PowerShell (VS Code terminal is fine).
      3) Dry run:
           .\refactor_jaicat.ps1 -Root "C:\Users\josh_\Desktop\jaicat_project" -DryRun $true -Confirm
         Apply:
           .\refactor_jaicat.ps1 -Root "C:\Users\josh_\Desktop\jaicat_project" -DryRun $false -Confirm
         Apply + OneDrive move:
           .\refactor_jaicat.ps1 -Root "C:\Users\josh_\Desktop\jaicat_project" -DryRun $false -Confirm -MigrateOneDrive
#>

param(
  [string]$Root = (Get-Location).Path,
  [switch]$Confirm,            # Skip interactive confirm if present
  [bool]$DryRun = $true,       # Set false to actually change files
  [switch]$MigrateOneDrive     # Move computer_vision\oneDrive.py -> services\one_drive.py and rewrite imports
)

# ---------- helpers ----------
function New-LogLine([string]$msg) {
  $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  "$timestamp  $msg"
}

function Ensure-Folder {
  param(
    [Parameter(Mandatory=$true)][string]$Path,
    [bool]$AlwaysCreate = $false  # if true, create even in DryRun (used for log dir)
  )
  if ([string]::IsNullOrWhiteSpace($Path)) { return }
  if (-not (Test-Path -LiteralPath $Path)) {
    if ($DryRun -and -not $AlwaysCreate) {
      New-LogLine "Create folder: $Path [DRY-RUN]" | Out-Host
    } else {
      New-Item -ItemType Directory -Force -Path $Path | Out-Null
    }
  }
}

# unified logger: prints and also logs to file if available
function Write-Log {
  param([Parameter(Mandatory=$true)][string]$Message)
  $line = New-LogLine $Message
  $line | Out-Host
  if ($script:LogToFile -and $script:LogPath) {
    try {
      Add-Content -LiteralPath $script:LogPath -Value $line
    } catch { }
  }
}

function Move-Safe([string]$src, [string]$dst) {
  if ([string]::IsNullOrWhiteSpace($src) -or -not (Test-Path -LiteralPath $src)) { return }
  $dstDir = Split-Path $dst -Parent
  Ensure-Folder -Path $dstDir
  if ($DryRun) { Write-Log "Move: $src -> $dst [DRY-RUN]" }
  else { Move-Item -Force -LiteralPath $src -Destination $dst }
}

function Copy-Safe([string]$src, [string]$dst) {
  if ([string]::IsNullOrWhiteSpace($src) -or -not (Test-Path -LiteralPath $src)) { return }
  $dstDir = Split-Path $dst -Parent
  Ensure-Folder -Path $dstDir
  if ($DryRun) { Write-Log "Copy: $src -> $dst [DRY-RUN]" }
  else { Copy-Item -Force -LiteralPath $src -Destination $dst }
}

# --- SAFE Replace-InFile (handles null/empty/locked files gracefully) ---
function Replace-InFile {
  param(
    [Parameter(Mandatory=$true)][string]$Path,
    [Parameter(Mandatory=$true)][hashtable]$Map,        # literal replacements
    [Parameter(Mandatory=$true)][hashtable]$RegexMap,   # regex replacements
    [Parameter(Mandatory=$true)][string]$BackupDir
  )

  if ([string]::IsNullOrWhiteSpace($Path) -or -not (Test-Path -LiteralPath $Path)) {
    return $false
  }

  try {
    # Force string; empty becomes ""
    $original = Get-Content -LiteralPath $Path -Raw -ErrorAction Stop
    if ($null -eq $original) { $original = "" }
    if (-not ($original -is [string])) { $original = [string]$original }
  }
  catch {
    Write-Log "SKIP (unreadable): $Path  -> $($_.Exception.Message)"
    return $false
  }

  $modified = $original

  # Literal replacements
  foreach ($k in $Map.Keys) {
    $v = $Map[$k]
    if ($null -ne $k -and $null -ne $v) {
      $modified = $modified.Replace([string]$k, [string]$v)
    }
  }

  # Regex replacements
  foreach ($pattern in $RegexMap.Keys) {
    $replacement = $RegexMap[$pattern]
    try {
      $modified = [System.Text.RegularExpressions.Regex]::Replace(
        $modified, [string]$pattern, [string]$replacement,
        [System.Text.RegularExpressions.RegexOptions]::Multiline
      )
    } catch {
      Write-Log "SKIP (regex fail): $Path  pattern='$pattern'  -> $($_.Exception.Message)"
    }
  }

  if ($modified -ne $original) {
    $rel = (Resolve-Path -LiteralPath $Path).Path.Replace($Root, "").TrimStart("\","/")
    if ($DryRun) {
      Write-Log "Modify: $rel [DRY-RUN]"
    } else {
      Ensure-Folder -Path $BackupDir -AlwaysCreate:$true
      $backupPath = Join-Path $BackupDir $rel
      Ensure-Folder -Path (Split-Path $backupPath -Parent) -AlwaysCreate:$true
      Copy-Item -Force -LiteralPath $Path -Destination $backupPath
      Set-Content -LiteralPath $Path -Value $modified -Encoding UTF8
      Write-Log "Modified: $rel (backup at $backupPath)"
    }
    return $true
  }

  return $false
}

# ---------- start ----------
$Root = (Resolve-Path $Root).Path
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ArchiveRoot = Join-Path $Root ("archive\Incubate\" + $stamp)
$BackupRoot  = Join-Path $Root ("archive\RefactorBackups\" + $stamp)
$LogPath     = Join-Path $Root ("archive\RefactorLog_" + $stamp + ".txt")

# Always create the **log directory** even in DryRun so logging to file works
Ensure-Folder -Path (Split-Path $LogPath -Parent) -AlwaysCreate:$true
$script:LogPath = $LogPath
$script:LogToFile = $true

$intro = @"
=== Jaicat Refactor ===
Root:          $Root
Archive:       $ArchiveRoot
Backups:       $BackupRoot
DryRun:        $DryRun
MigrateOneDrive: $($MigrateOneDrive.IsPresent)

This will:
  - Archive deprecated files (controller/processor/handler_table/weather_api/calendar_api/google_calendar_api, utils duplicates)
  - Optional: move computer_vision\oneDrive.py -> services\one_drive.py
  - Rewrite imports in all .py files:
      utils.encryption_utils  -> security.encryption_utils
      utils.enrollment        -> services.user_enrollment
      services.weather_api    -> services.weather_service
      services.calendar_api   -> services.calendar_service
      services.google_calendar_api -> services.calendar_service
      Core.controller         -> app.controller
      computer_vision.oneDrive -> services.one_drive (if -MigrateOneDrive)
      command.processor / command.handler_table -> commented with TODO
"@
Write-Log $intro

if (-not $Confirm) {
  $resp = Read-Host "Proceed? (y/n)"
  if ($resp -ne "y") { Write-Log "Cancelled."; exit 1 }
}

# ---------- 1) Archive or move files ----------
# (Archive folder itself is only created on apply; dry-run just logs.)
Ensure-Folder -Path $ArchiveRoot  # DryRun will just log the intention

$ToArchive = @(
  "Core\controller.py",
  "command\processor.py",
  "command\handler_table.py",
  "services\weather_api.py",
  "services\calendar_api.py",
  "services\google_calendar_api.py",
  "utils\encryption_utils.py",    # prefer security\encryption_utils.py
  "utils\enrollment.py",          # prefer services\user_enrollment.py
  "services\spotify_integration 1.txt"
)

foreach ($rel in $ToArchive) {
  $src = Join-Path $Root $rel
  if (Test-Path -LiteralPath $src) {
    Move-Safe $src (Join-Path $ArchiveRoot $rel)
  }
}

# OneDrive migration (optional)
if ($MigrateOneDrive) {
  $srcOne = Join-Path $Root "computer_vision\oneDrive.py"
  $dstOne = Join-Path $Root "services\one_drive.py"
  if (Test-Path -LiteralPath $srcOne) {
    if ($DryRun) {
      Write-Log "Migrate: computer_vision\oneDrive.py -> services\one_drive.py [DRY-RUN]"
    } else {
      Ensure-Folder -Path (Split-Path $dstOne -Parent) -AlwaysCreate:$true
      Move-Item -Force -LiteralPath $srcOne -Destination $dstOne
      Write-Log "Migrated: computer_vision\oneDrive.py -> services\one_drive.py"
    }
  }
}

# ---------- 2) Rewrite imports in .py files ----------
# Only real .py files (skip __pycache__, .venv, large/binary)
$pyFiles = Get-ChildItem -Path $Root -Recurse -Include *.py -File |
  Where-Object {
    $_.FullName -notmatch '\\__pycache__\\' -and
    $_.FullName -notmatch '\\\.venv\\' -and
    $_.Length -lt 5MB
  }

# literal map
$LiteralMap = @{
  "from utils.encryption_utils"           = "from security.encryption_utils"
  "import utils.encryption_utils"         = "import security.encryption_utils"
  "from utils.enrollment"                 = "from services.user_enrollment"
  "import utils.enrollment"               = "import services.user_enrollment"
  "from services.weather_api"             = "from services.weather_service"
  "import services.weather_api"           = "import services.weather_service"
  "from services.calendar_api"            = "from services.calendar_service"
  "import services.calendar_api"          = "import services.calendar_service"
  "from services.google_calendar_api"     = "from services.calendar_service"
  "import services.google_calendar_api"   = "import services.calendar_service"
  "from Core.controller"                  = "from app.controller"
  "import Core.controller"                = "import app.controller"
}
if ($MigrateOneDrive) {
  $LiteralMap["from computer_vision.oneDrive"]   = "from services.one_drive"
  $LiteralMap["import computer_vision.oneDrive"] = "import services.one_drive"
}

# regex map (to comment out removed modules)
$RegexMap = @{
  '^\s*from\s+command\.processor\s+import\s+.*$'      = '# REMOVED: command.processor (use CommandRouter + command.builtin)'
  '^\s*import\s+command\.processor.*$'                = '# REMOVED: command.processor (use CommandRouter + command.builtin)'
  '^\s*from\s+command\.handler_table\s+import\s+.*$'  = '# REMOVED: command.handler_table (use CommandRouter + command.builtin)'
  '^\s*import\s+command\.handler_table.*$'            = '# REMOVED: command.handler_table (use CommandRouter + command.builtin)'
}

$changed = 0
foreach ($f in $pyFiles) {
  try {
    $ok = Replace-InFile -Path $f.FullName -Map $LiteralMap -RegexMap $RegexMap -BackupDir $BackupRoot
    if ($ok) { $changed++ }
  } catch {
    Write-Log "SKIP (Replace-InFile error): $($f.FullName) -> $($_.Exception.Message)"
  }
}
Write-Log ("Python files modified: {0}" -f $changed)

# ---------- 3) Write archive README ----------
$ArchiveReadme = @"
# Incubate Archive ($stamp)

The following files were moved here to consolidate duplicates and standardise imports:

- Core\controller.py (replaced by app\controller.py)
- command\processor.py (replace with Core\command_router + command\builtin)
- command\handler_table.py (same as above)
- services\weather_api.py (use services\weather_service.py)
- services\calendar_api.py, services\google_calendar_api.py (use services\calendar_service.py)
- utils\encryption_utils.py (use security\encryption_utils.py)
- utils\enrollment.py (use services\user_enrollment.py)
- services\spotify_integration 1.txt (notes merged; file removed)

If -MigrateOneDrive was used:
- computer_vision\oneDrive.py -> services\one_drive.py (imports updated)

A backup of modified source files lives at:
$BackupRoot

See change log:
$LogPath
"@
$archiveNotes = Join-Path $ArchiveRoot "ARCHIVE_NOTES.md"
if ($DryRun) {
  Write-Log "Write ARCHIVE_NOTES.md [DRY-RUN]"
} else {
  Ensure-Folder -Path $ArchiveRoot -AlwaysCreate:$true
  Set-Content -Path $archiveNotes -Value $ArchiveReadme -Encoding UTF8
  Write-Log "Wrote $archiveNotes"
}

Write-Log "Done."
