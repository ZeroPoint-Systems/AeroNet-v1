param(
    [ValidateSet("Audit", "Test", "All")]
    [string]$Stage = "All"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
Set-Location $RepoRoot

$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$OutDir = Join-Path $RepoRoot "experiments\master_key\runs\$Stamp"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$Results = [System.Collections.Generic.List[string]]::new()
$Failures = 0

function Save-Command {
    param(
        [string]$Name,
        [string]$Executable,
        [string[]]$Arguments
    )

    $Log = Join-Path $OutDir "$Name.log"
    Write-Host "`n>>> $Name" -ForegroundColor Cyan

    $Output = @(& $Executable @Arguments 2>&1)
    $ExitCode = $LASTEXITCODE
    $Output | Out-String | Set-Content -Encoding utf8 $Log
    $Output | ForEach-Object { Write-Host $_ }

    if ($ExitCode -eq 0) {
        $script:Results.Add("- PASS: $Name")
    } else {
        $script:Results.Add("- FAIL: $Name (exit code $ExitCode)")
        $script:Failures++
    }
}

Write-Host "`nMASTER KEY | AeroNet Research Pipeline" -ForegroundColor Cyan
Write-Host "Repository: $RepoRoot"
Write-Host "Run output: $OutDir"

# Record the current state without changing tracked or untracked files.
Save-Command "git-status" "git" @("status", "--short", "--branch")
Save-Command "git-diff-check" "git" @("diff", "--check")

# Preserve source snapshots for diagnosis.
$SourceFiles = @(
    "simulation\estimation\base.py",
    "simulation\estimation\reference_kalman.py",
    "simulation\estimation\covariance_intersection.py",
    "experiments\runners\config.py",
    "experiments\runners\run_experiment.py"
)

foreach ($RelativePath in $SourceFiles) {
    $FullPath = Join-Path $RepoRoot $RelativePath
    if (Test-Path $FullPath) {
        $SafeName = $RelativePath -replace '[\\/:]', '_'
        Copy-Item $FullPath (Join-Path $OutDir $SafeName)
        $Results.Add("- SNAPSHOT: $RelativePath")
    } else {
        $Results.Add("- MISSING: $RelativePath")
        Write-Host "Missing expected file: $RelativePath" -ForegroundColor Yellow
    }
}

# Identify incomplete implementation markers.
$Markers = Get-ChildItem "simulation" -Recurse -File -Filter "*.py" |
    Select-String -Pattern "NotImplementedError|STATUS: LITERATURE-DEPENDENT" |
    ForEach-Object {
        "$($_.Path.Replace($RepoRoot, '.')):$($_.LineNumber): $($_.Line.Trim())"
    }

if ($Markers) {
    $Markers | Set-Content -Encoding utf8 (Join-Path $OutDir "implementation-blockers.txt")
    Write-Host "`nImplementation blockers found:" -ForegroundColor Yellow
    $Markers | ForEach-Object { Write-Host $_ }
    $Results.Add("- REVIEW REQUIRED: incomplete implementation markers found")
} else {
    $Results.Add("- PASS: no scanned implementation markers found")
}

if ($Stage -in @("Test", "All")) {
    Save-Command "pytest" "python" @("-m", "pytest", "-q")
}

$Report = @(
    "# Master Key Run Report"
    ""
    "- Timestamp: $Stamp"
    "- Stage: $Stage"
    "- Repository: $RepoRoot"
    "- Failed commands: $Failures"
    ""
    "## Results"
    $Results
    ""
    "## Interpretation"
    "This run audits repository state and executes requested checks."
    "It does not claim that scientific novelty has been established."
    "Review implementation-blockers.txt and source snapshots before"
    "integrating new estimator or communication-policy code."
)

$Report | Set-Content -Encoding utf8 (Join-Path $OutDir "REPORT.md")

Write-Host "`nReport: $OutDir\REPORT.md" -ForegroundColor Cyan

if ($Failures -gt 0) {
    Write-Host "MASTER KEY FAILED. Inspect the logs before proceeding." -ForegroundColor Red
    exit 1
}

Write-Host "MASTER KEY CHECKS COMPLETED." -ForegroundColor Green
Write-Host "Completion means the requested checks ran successfully, not that all research components are implemented."
