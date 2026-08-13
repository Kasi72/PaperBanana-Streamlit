param(
    [switch]$SkipInstall,
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $ProjectRoot ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$Requirements = Join-Path $ProjectRoot "requirements.txt"
$RequirementsStamp = Join-Path $VenvDir ".paperbanana-requirements.sha256"

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$Command,
        [Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments
    )

    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE`: $Command $($Arguments -join ' ')"
    }
}

function Find-CompatiblePython {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        foreach ($Version in @("3.12", "3.11")) {
            try {
                & py "-$Version" -c "import sys; print(sys.executable)" *> $null
                if ($LASTEXITCODE -eq 0) {
                    return @{ Command = "py"; Arguments = @("-$Version") }
                }
            }
            catch {
                continue
            }
        }
    }

    if (Get-Command python -ErrorAction SilentlyContinue) {
        try {
            & python -c "import sys; raise SystemExit(0 if sys.version_info[:2] in ((3, 11), (3, 12)) else 1)" *> $null
            if ($LASTEXITCODE -eq 0) {
                return @{ Command = "python"; Arguments = @() }
            }
        }
        catch {
            return $null
        }
    }

    return $null
}

try {
    Push-Location $ProjectRoot

    if (-not (Test-Path $VenvPython)) {
        $Python = Find-CompatiblePython
        if ($null -eq $Python) {
            throw "Python 3.11 or 3.12 is required. Install Python 3.12 from https://www.python.org/downloads/ and run start_app.cmd again."
        }

        Write-Host "Creating PaperBanana environment..." -ForegroundColor Cyan
        Invoke-Checked -Command $Python.Command -Arguments (@($Python.Arguments) + @("-m", "venv", $VenvDir))
    }

    Invoke-Checked -Command $VenvPython -Arguments @("-c", "import sys; raise SystemExit(0 if sys.version_info[:2] in ((3, 11), (3, 12)) else 1)")

    if (-not $SkipInstall) {
        $CurrentHash = (Get-FileHash $Requirements -Algorithm SHA256).Hash
        $SavedHash = if (Test-Path $RequirementsStamp) { (Get-Content $RequirementsStamp -Raw).Trim() } else { "" }

        if ($CurrentHash -ne $SavedHash) {
            Write-Host "Installing PaperBanana dependencies (first launch can take a few minutes)..." -ForegroundColor Cyan
            Invoke-Checked -Command $VenvPython -Arguments @("-m", "pip", "install", "-r", $Requirements)
            Set-Content -Path $RequirementsStamp -Value $CurrentHash -NoNewline
        }
    }

    if ($CheckOnly) {
        Write-Host "PaperBanana environment is ready." -ForegroundColor Green
        exit 0
    }

    Write-Host "Starting PaperBanana Streamlit Studio..." -ForegroundColor Green
    Invoke-Checked -Command $VenvPython -Arguments @("-m", "streamlit", "run", (Join-Path $ProjectRoot "streamlit_app.py"))
}
catch {
    Write-Host ""
    Write-Host "PaperBanana could not start:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
finally {
    Pop-Location
}
