$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/FranBarInstance/neutral-starter-py.git"
$DefaultBranch = "master"

function Read-Value {
    param(
        [string]$Prompt,
        [string]$Default
    )
    $value = Read-Host "$Prompt [$Default]"
    if ([string]::IsNullOrWhiteSpace($value)) {
        return $Default
    }
    return $value
}

function Set-EnvValue {
    param(
        [string]$Path,
        [string]$Key,
        [string]$Value
    )
    $content = @()
    if (Test-Path $Path) {
        $content = Get-Content -Path $Path
    }

    $updated = $false
    $newContent = foreach ($line in $content) {
        if ($line -match "^$([regex]::Escape($Key))=") {
            $updated = $true
            "$Key=$Value"
        }
        else {
            $line
        }
    }

    if (-not $updated) {
        $newContent += "$Key=$Value"
    }

    Set-Content -Path $Path -Value $newContent
}

function Resolve-Python {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @{
            Executable = "py"
            Args = @("-3")
        }
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @{
            Executable = "python"
            Args = @()
        }
    }
    throw "Python 3 is required but was not found."
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git is required but was not found."
}

Write-Host "Fetching latest tags from repository..."
$tagLines = git ls-remote --tags --refs $RepoUrl
$tags = @()
foreach ($line in $tagLines) {
    $parts = $line -split "`t"
    if ($parts.Length -ge 2) {
        $tags += ($parts[1] -replace "^refs/tags/", "")
    }
}

$sortedTags = $tags |
    Sort-Object -Property `
    @{ Expression = {
            $clean = ($_ -replace "^[vV]", "")
            if ($clean -match '^\d+(\.\d+){0,3}$') { [version]$clean } else { [version]"0.0.0.0" }
        }; Descending = $true }, `
    @{ Expression = { $_ }; Descending = $true } |
    Select-Object -First 15

if (-not $sortedTags -or $sortedTags.Count -eq 0) {
    Write-Host "No tags found. Falling back to branch: $DefaultBranch"
    $sortedTags = @($DefaultBranch)
}

Write-Host "Available versions:"
for ($i = 0; $i -lt $sortedTags.Count; $i++) {
    Write-Host ("  {0}) {1}" -f ($i + 1), $sortedTags[$i])
}

$selection = Read-Value -Prompt "Select version number" -Default "1"
if (-not ($selection -match '^\d+$')) {
    throw "Invalid version selection."
}

$selectionIndex = [int]$selection
if ($selectionIndex -lt 1 -or $selectionIndex -gt $sortedTags.Count) {
    throw "Version selection out of range (1..$($sortedTags.Count))."
}

$selectedTag = $sortedTags[$selectionIndex - 1]
$installDir = Read-Value -Prompt "Installation directory" -Default (Get-Location).Path

if (Test-Path $installDir) {
    $entries = Get-ChildItem -Force -Path $installDir
    if ($entries.Count -gt 0) {
        throw "Installation directory is not empty: $installDir"
    }
}
else {
    New-Item -ItemType Directory -Path $installDir | Out-Null
}

Write-Host "Cloning version '$selectedTag' into '$installDir'..."
if ($selectedTag -eq $DefaultBranch) {
    git clone --depth 1 --branch $DefaultBranch $RepoUrl $installDir
}
else {
    git clone --depth 1 --branch $selectedTag $RepoUrl $installDir
}

Set-Location $installDir

$pythonCmd = Resolve-Python
Write-Host "Creating virtual environment..."
if ($pythonCmd.Args.Count -gt 0) {
    & $pythonCmd.Executable $pythonCmd.Args -m venv .venv
}
else {
    & $pythonCmd.Executable -m venv .venv
}

$venvPython = Join-Path $installDir ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Virtual environment Python not found at $venvPython"
}

Write-Host "Installing dependencies..."
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

Write-Host "Configuring environment file..."
Copy-Item -Path "config/.env.example" -Destination "config/.env" -Force
$secretKey = & $venvPython -c "import secrets; print(secrets.token_urlsafe(48))"
Set-EnvValue -Path "config/.env" -Key "SECRET_KEY" -Value $secretKey

Write-Host "Generating randomized admin routes..."
$adminSuffix = (& $venvPython -c "import secrets; print(secrets.token_hex(6))").Trim()
$devAdminSuffix = (& $venvPython -c "import secrets; print(secrets.token_hex(6))").Trim()
$adminRoute = "/admin-$adminSuffix"
$devAdminRoute = "/dev-admin-$devAdminSuffix"

$adminCustomPath = "src/component/cmp_7060_admin/custom.json"
$devAdminCustomPath = "src/component/cmp_7050_dev_admin/custom.json"
New-Item -ItemType Directory -Path (Split-Path -Parent $adminCustomPath) -Force | Out-Null
New-Item -ItemType Directory -Path (Split-Path -Parent $devAdminCustomPath) -Force | Out-Null

$adminJson = @{
    manifest = @{
        route = $adminRoute
    }
} | ConvertTo-Json -Depth 3

$devAdminJson = @{
    manifest = @{
        route = $devAdminRoute
    }
} | ConvertTo-Json -Depth 3

Set-Content -Path $adminCustomPath -Value $adminJson
Set-Content -Path $devAdminCustomPath -Value $devAdminJson
Write-Host "Admin route: $adminRoute"
Write-Host "Dev admin route: $devAdminRoute"

Write-Host "Bootstrapping databases..."
& $venvPython "bin/bootstrap_db.py"

$devName = Read-Value -Prompt "DEV user alias" -Default "Dev Admin"
$devEmail = Read-Value -Prompt "DEV user email" -Default "dev@example.com"

$devPassword = ""
while ($devPassword.Length -lt 9) {
    $securePwd = Read-Host "DEV user password (min 9 chars)" -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePwd)
    try {
        $devPassword = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
    if ($devPassword.Length -lt 9) {
        Write-Host "Password must be at least 9 characters."
    }
}

$devBirthdate = Read-Value -Prompt "DEV user birthdate (YYYY-MM-DD)" -Default "1990-01-01"
$devLocale = Read-Value -Prompt "DEV user locale" -Default "es"

Write-Host "Creating DEV user..."
& $venvPython "bin/create_user.py" $devName $devEmail $devPassword $devBirthdate --locale $devLocale --role dev

Set-EnvValue -Path "config/.env" -Key "DEV_ADMIN_USER" -Value $devEmail
Set-EnvValue -Path "config/.env" -Key "DEV_ADMIN_PASSWORD" -Value $devPassword
Set-EnvValue -Path "config/.env" -Key "DEV_ADMIN_LOCAL_ONLY" -Value "true"
Set-EnvValue -Path "config/.env" -Key "DEV_ADMIN_ALLOWED_IPS" -Value "127.0.0.1,::1"
Write-Host "DEV_ADMIN_* updated in config/.env"

Write-Host "Installation completed."
Write-Host "Project directory: $installDir"
Write-Host "Run with:"
Write-Host "  .\.venv\Scripts\python.exe src\run.py"
