param(
    [string]$RepoUrl = "",

    [string]$Branch = "main",

    [string]$CommitMessage = "chore: sync project"
)

$gitCommand = Get-Command git -ErrorAction SilentlyContinue
$gitPath = $null

if ($gitCommand) {
    $gitPath = $gitCommand.Source
} else {
    $commonGitPaths = @(
        "C:\Program Files\Git\cmd\git.exe",
        "C:\Program Files\Git\bin\git.exe",
        (Join-Path $env:LOCALAPPDATA "Programs\Git\cmd\git.exe")
    )

    foreach ($candidate in $commonGitPaths) {
        if (Test-Path $candidate) {
            $gitPath = $candidate
            break
        }
    }
}

if (-not $gitPath) {
    Write-Error "Git is not installed or not available in PATH. Install Git for Windows first, then rerun this script."
    exit 1
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

if (-not (Test-Path (Join-Path $repoRoot ".git"))) {
    & $gitPath init | Out-Null
}

$gitStatus = & $gitPath status --porcelain

if (-not $gitStatus) {
    Write-Host "No local changes detected."
} else {
    $gitUserName = & $gitPath config user.name
    $gitUserEmail = & $gitPath config user.email

    if (-not $gitUserName -or -not $gitUserEmail) {
        $gitUserName = & $gitPath config --global user.name
        $gitUserEmail = & $gitPath config --global user.email
    }

    if (-not $gitUserName -or -not $gitUserEmail) {
        if (-not $gitUserName) {
            $gitUserName = Read-Host "Enter your Git user.name"
        }

        if (-not $gitUserEmail) {
            $gitUserEmail = Read-Host "Enter your Git user.email"
        }

        if (-not $gitUserName -or -not $gitUserEmail) {
            Write-Error "Git user.name and user.email are required to create a commit."
            exit 1
        }

        & $gitPath config --global user.name $gitUserName
        & $gitPath config --global user.email $gitUserEmail
    }

    & $gitPath add .
    & $gitPath commit -m $CommitMessage
}

$currentBranch = & $gitPath branch --show-current
if (-not $currentBranch) {
    & $gitPath checkout -b $Branch
} elseif ($currentBranch -ne $Branch) {
    & $gitPath branch -M $Branch
}

$originUrl = & $gitPath remote get-url origin 2>$null
if (-not $RepoUrl) {
    if ($originUrl) {
        $RepoUrl = $originUrl
    } else {
        $RepoUrl = Read-Host "Enter your GitHub repository URL"
    }
}

if (-not $RepoUrl) {
    Write-Error "A GitHub repository URL is required."
    exit 1
}

if (-not $originUrl) {
    & $gitPath remote add origin $RepoUrl
} elseif ($originUrl -ne $RepoUrl) {
    & $gitPath remote set-url origin $RepoUrl
}

& $gitPath push -u origin $Branch
