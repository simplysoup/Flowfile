# start-dev.ps1 - Start Flowfile backend + frontend dev servers
# Usage: .\start-dev.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$port = 55800

# Resolve tools
$venvPython = Join-Path $root ".venv\Scripts\python.exe"
$fnmNode = Join-Path $env:APPDATA "fnm\node-versions\v24.14.0\installation"

if (-not (Test-Path $venvPython)) {
    Write-Host "ERROR: .venv not found. Run 'uv venv --python 3.12 .venv && uv pip install -e .' first." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path (Join-Path $fnmNode "node.exe"))) {
    Write-Host "WARNING: fnm node v24.14.0 not found - trying system PATH for npm" -ForegroundColor Yellow
    $fnmNode = $null
}

# Add node to PATH for this session
if ($fnmNode) {
    $env:Path = "$fnmNode;$env:Path"
}

Write-Host "Starting Flowfile development servers..." -ForegroundColor Cyan
Write-Host "  Backend:  http://127.0.0.1:63578" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:$port" -ForegroundColor Green
Write-Host "" -ForegroundColor White
Write-Host "Press Ctrl+C to stop both servers." -ForegroundColor DarkGray
Write-Host "" -ForegroundColor White

# Start backend (flowfile_core on port 63578)
$backendArgs = @("-m", "flowfile_core.main")
$backend = Start-Process -FilePath $venvPython -ArgumentList $backendArgs -WorkingDirectory $root -PassThru -NoNewWindow

# Wait for backend to be ready
Write-Host "Waiting for backend to start..." -ForegroundColor DarkGray
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1
    try {
        $null = Invoke-WebRequest -Uri "http://127.0.0.1:63578/docs" -UseBasicParsing -TimeoutSec 2
        $ready = $true
        break
    } catch {}
}

if (-not $ready) {
    Write-Host "ERROR: Backend did not start within 30s" -ForegroundColor Red
    Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
    exit 1
}
Write-Host "Backend ready." -ForegroundColor Green

# Start frontend dev server on specified port
$frontendDir = Join-Path $root "flowfile_frontend"
$npmCmd = if ($fnmNode) { Join-Path $fnmNode "npm.cmd" } else { "npm" }
$frontend = Start-Process -FilePath $npmCmd -ArgumentList "run", "dev:web", "--", "--port", "$port" -WorkingDirectory $frontendDir -PassThru -NoNewWindow

Write-Host "Frontend dev server starting on port $port..." -ForegroundColor Green
Write-Host "" -ForegroundColor White

# Wait for either process to exit, then clean up both
try {
    while (-not $backend.HasExited -and -not $frontend.HasExited) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "Shutting down..." -ForegroundColor Yellow
    if (-not $backend.HasExited) {
        # Graceful shutdown via API
        try {
            $authBody = "username=admin" + "&" + "password=admin"
            $token = (Invoke-RestMethod -Uri "http://127.0.0.1:63578/auth/token" -Method Post -Body $authBody -ContentType "application/x-www-form-urlencoded" -TimeoutSec 3).access_token
            $headers = @{ Authorization = "Bearer $token" }
            $null = Invoke-RestMethod -Uri "http://127.0.0.1:63578/shutdown" -Method Post -Headers $headers -TimeoutSec 3
            Start-Sleep -Seconds 2
        } catch {}
        if (-not $backend.HasExited) {
            Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
        }
    }
    if (-not $frontend.HasExited) {
        Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "Done." -ForegroundColor Green
}
