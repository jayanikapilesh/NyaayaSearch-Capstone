# Deploy NyaayaSearch backend to Azure App Service as a Linux Container (SKU B2)
# Usage:
#   .\scripts\deploy_azure.ps1 [-ImageTag "v1"] [-AcrName "nyaayaacr473221"] [-AppName "nyaaya-api-473221"]

param (
    [string]$ResourceGroup = "nyaaya-rg",
    [string]$Location = "centralindia",
    [string]$AcrName = "nyaayaacr473221",
    [string]$AppPlan = "nyaaya-plan",
    [string]$AppName = "nyaaya-api-473221",
    [string]$ImageTag = "v1"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Deploy NyaayaSearch to Azure App Service" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Resource Group: $ResourceGroup"
Write-Host "Location:       $Location"
Write-Host "ACR Name:       $AcrName"
Write-Host "App Plan:       $AppPlan (SKU: B2)"
Write-Host "Web App Name:   $AppName"
Write-Host "Image Tag:      $ImageTag"
Write-Host ""

# 1. Read GROQ_API_KEY from .env without echoing it
$envFile = Join-Path $repoRoot ".env"
$groqKey = $null
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^\s*GROQ_API_KEY\s*=\s*(.+)$") {
            $groqKey = $matches[1].Trim()
        }
    }
}
if (-not $groqKey) {
    $groqKey = $env:GROQ_API_KEY
}
if (-not $groqKey) {
    Write-Error "GROQ_API_KEY not found in .env file or environment variables."
    exit 1
}
Write-Host "Loaded GROQ_API_KEY securely from .env (length: $($groqKey.Length) chars)." -ForegroundColor Green

# 2. Check Docker is running
try {
    $dockerCheck = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker Desktop is not currently running. Please start Docker Desktop and re-run."
        exit 1
    }
} catch {
    Write-Error "Docker command failed. Please ensure Docker Desktop is running."
    exit 1
}
Write-Host "Docker engine is running." -ForegroundColor Green

# 3. Build image locally
$imageName = "$AcrName.azurecr.io/nyaaya-api:$ImageTag"
Write-Host "`nStep 1: Building Docker image $imageName ..." -ForegroundColor Yellow
docker build -t $imageName .
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker build failed."
    exit 1
}

$rawSize = docker image inspect $imageName --format "{{.Size}}" 2>$null
if ($rawSize) {
    $sizeMB = [math]::Round([double]$rawSize / (1024 * 1024), 2)
    Write-Host "Docker image built successfully! Size: $sizeMB MB ($rawSize bytes)." -ForegroundColor Green
}

# 4. Log in to ACR
Write-Host "`nStep 2: Logging in to Azure Container Registry: $AcrName ..." -ForegroundColor Yellow
az acr login --name $AcrName
if ($LASTEXITCODE -ne 0) {
    Write-Error "az acr login failed."
    exit 1
}

# 5. Push image to ACR
Write-Host "`nStep 3: Pushing Docker image to ACR ..." -ForegroundColor Yellow
docker push $imageName
if ($LASTEXITCODE -ne 0) {
    Write-Error "docker push failed."
    exit 1
}
Write-Host "Image pushed to $imageName successfully." -ForegroundColor Green

# 6. Retrieve ACR credentials
Write-Host "`nStep 4: Configuring ACR credentials..." -ForegroundColor Yellow
$creds = az acr credential show --name $AcrName | ConvertFrom-Json
$acrUser = $creds.username
$acrPassword = $creds.passwords[0].value

# 7. Ensure App Service Plan exists
Write-Host "`nStep 5: Checking App Service Plan $AppPlan (SKU B2)..." -ForegroundColor Yellow
$planExists = az appservice plan show --name $AppPlan --resource-group $ResourceGroup 2>$null
if (-not $planExists) {
    Write-Host "Creating Linux App Service Plan $AppPlan (B2 in $Location)..."
    az appservice plan create --name $AppPlan --resource-group $ResourceGroup --is-linux --sku B2 --location $Location | Out-Null
}
Write-Host "App Service Plan $AppPlan is ready." -ForegroundColor Green

# 8. Create or Update Web App
Write-Host "`nStep 6: Setting up Web App $AppName ..." -ForegroundColor Yellow
$appExists = az webapp show --name $AppName --resource-group $ResourceGroup 2>$null
if (-not $appExists) {
    Write-Host "Creating Web App $AppName with container image $imageName ..."
    az webapp create --resource-group $ResourceGroup --plan $AppPlan --name $AppName --deployment-container-image-name $imageName | Out-Null
}

Write-Host "Configuring container registry credentials..."
az webapp config container set `
    --name $AppName `
    --resource-group $ResourceGroup `
    --docker-custom-image-name $imageName `
    --docker-registry-server-url "https://$AcrName.azurecr.io" `
    --docker-registry-server-user $acrUser `
    --docker-registry-server-password $acrPassword | Out-Null

Write-Host "Configuring App Settings (WEBSITES_PORT=7860, AlwaysOn=true)..."
# Set appsettings without printing the GROQ_API_KEY
az webapp config appsettings set `
    --resource-group $ResourceGroup `
    --name $AppName `
    --settings `
        WEBSITES_PORT=7860 `
        WEBSITES_CONTAINER_START_TIME_LIMIT=1800 `
        NYAAYA_EMBED_MODEL=duladani/nyaaya-legal-embed-v3 `
        GROQ_API_KEY=$groqKey | Out-Null

az webapp config set `
    --resource-group $ResourceGroup `
    --name $AppName `
    --always-on true | Out-Null

Write-Host "Restarting Web App $AppName ..."
az webapp restart --name $AppName --resource-group $ResourceGroup | Out-Null

# 9. Wait for startup & Test endpoints
$appUrl = "https://$AppName.azurewebsites.net"
Write-Host "`nStep 7: Testing deployed application at $appUrl ..." -ForegroundColor Yellow
Write-Host "Waiting for container initialization (can take 60-120 seconds for first boot)..."

$maxAttempts = 30
$delaySec = 10
$healthy = $false

for ($i = 1; $i -le $maxAttempts; $i++) {
    Write-Host "Attempt $i/$maxAttempts checking $appUrl/stats ..."
    try {
        $statsResp = Invoke-RestMethod -Uri "$appUrl/stats" -Method Get -TimeoutSec 15 -ErrorAction Stop
        if ($statsResp.sections -gt 0) {
            Write-Host "Stats check passed! Acts: $($statsResp.acts), Sections: $($statsResp.sections), Cases: $($statsResp.supreme_court_cases)" -ForegroundColor Green
            $healthy = $true
            break
        }
    } catch {
        # Container still starting
    }
    Start-Sleep -Seconds $delaySec
}

if (-not $healthy) {
    Write-Host "Warning: /stats did not respond within timeout. Showing container logs:" -ForegroundColor Red
    az webapp log tail --name $AppName --resource-group $ResourceGroup
    exit 1
}

# 10. Test /search query
Write-Host "Testing POST $appUrl/search with sample query..." -ForegroundColor Yellow
$searchBody = @{
    query = "my landlord won't return my deposit"
    top_k = 3
    rerank = $true
} | ConvertTo-Json

try {
    $searchResp = Invoke-RestMethod -Uri "$appUrl/search" -Method Post -Body $searchBody -ContentType "application/json" -TimeoutSec 30
    Write-Host "Search query succeeded! Top match: $($searchResp.results[0].act_name) Sec $($searchResp.results[0].section_number) (Score: $($searchResp.results[0].hybrid_score))" -ForegroundColor Green
} catch {
    Write-Host "Search request failed: $_" -ForegroundColor Red
    az webapp log tail --name $AppName --resource-group $ResourceGroup
    exit 1
}

Write-Host "`n=========================================" -ForegroundColor Green
Write-Host " Deployment Complete!" -ForegroundColor Green
Write-Host " App URL: $appUrl" -ForegroundColor Green
Write-Host " Docs:    $appUrl/docs" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
