# Docker Status Check Script for CommuteOS
# Run this to diagnose Docker issues

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "  CommuteOS Docker Status Check" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# Check 1: Docker Desktop Running
Write-Host "[1/6] Checking if Docker Desktop is running..." -ForegroundColor Cyan
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Docker is running: " -ForegroundColor Green -NoNewline
        Write-Host $dockerVersion
    } else {
        throw "Docker not accessible"
    }
} catch {
    Write-Host "  ❌ Docker Desktop is NOT running!" -ForegroundColor Red
    Write-Host "  " -NoNewline
    Write-Host "SOLUTION: " -ForegroundColor Yellow -NoNewline
    Write-Host "Start Docker Desktop from the Start menu"
    Write-Host "  Wait 30-60 seconds for it to fully start, then run this script again."
    Write-Host ""
    exit 1
}

# Check 2: Docker Compose
Write-Host "[2/6] Checking Docker Compose..." -ForegroundColor Cyan
try {
    $composeVersion = docker-compose --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Docker Compose: " -ForegroundColor Green -NoNewline
        Write-Host $composeVersion
    } else {
        throw "Docker Compose not found"
    }
} catch {
    Write-Host "  ❌ Docker Compose not found!" -ForegroundColor Red
    Write-Host "  " -NoNewline
    Write-Host "SOLUTION: " -ForegroundColor Yellow -NoNewline
    Write-Host "Update Docker Desktop to latest version"
    exit 1
}

# Check 3: Project Files
Write-Host "[3/6] Checking project files..." -ForegroundColor Cyan
$requiredFiles = @("docker-compose.yml", "Dockerfile", "requirements.txt", "commuteos")
$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file missing!" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Host "  " -NoNewline
    Write-Host "SOLUTION: " -ForegroundColor Yellow -NoNewline
    Write-Host "Ensure you're in the correct directory: 'commute os'"
    exit 1
}

# Check 4: Environment File
Write-Host "[4/6] Checking environment configuration..." -ForegroundColor Cyan
if (Test-Path ".env") {
    Write-Host "  ✅ .env file exists" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  .env file not found" -ForegroundColor Yellow
    Write-Host "  Creating .env from .env.example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "  ✅ .env file created" -ForegroundColor Green
    } else {
        Write-Host "  ❌ .env.example not found!" -ForegroundColor Red
    }
}

# Check 5: Running Containers
Write-Host "[5/6] Checking running containers..." -ForegroundColor Cyan
$containers = docker ps --filter "name=commuteos" --format "{{.Names}}" 2>&1
if ($LASTEXITCODE -eq 0 -and $containers) {
    Write-Host "  ✅ CommuteOS containers are running:" -ForegroundColor Green
    foreach ($container in $containers) {
        Write-Host "     - $container" -ForegroundColor Gray
    }
} else {
    Write-Host "  ⚠️  No CommuteOS containers running" -ForegroundColor Yellow
    Write-Host "  This is normal if you haven't started the services yet."
}

# Check 6: Port Availability
Write-Host "[6/6] Checking port availability..." -ForegroundColor Cyan
$ports = @(8000, 8001, 5432, 6379)
$portsOk = $true
foreach ($port in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection -and ($connection | Where-Object { $_.State -eq "Listen" })) {
        Write-Host "  ⚠️  Port $port is in use" -ForegroundColor Yellow
    } else {
        Write-Host "  ✅ Port $port is available" -ForegroundColor Green
    }
}

# Summary
Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "  Status Summary" -ForegroundColor Yellow
Write-Host ("=" * 60) -ForegroundColor Cyan

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ All checks passed! You're ready to start CommuteOS." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Start services: " -NoNewline
    Write-Host "docker-compose up -d" -ForegroundColor White
    Write-Host "  2. Check health:   " -NoNewline
    Write-Host "curl http://localhost:8000/health" -ForegroundColor White
    Write-Host "  3. View logs:      " -NoNewline
    Write-Host "docker-compose logs -f" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "⚠️  Some issues detected. Please fix them and run this script again." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host ("=" * 60) -ForegroundColor Cyan
