param(
    [string]$Location = "eastus",
    [string]$ResourceGroup = "rg-warehouse-mcp-weather",
    [string]$AcrName = "yourcontainerregistry",
    [string]$EnvName = "acae-warehouse-mcp",
    [string]$AppName = "ca-warehouse-weather-mcp",
    [string]$ImageTag = "1.0.0"
)

$ErrorActionPreference = "Stop"

Write-Host "Ensuring Azure providers are registered..."
az provider register --namespace Microsoft.App | Out-Null
az provider register --namespace Microsoft.OperationalInsights | Out-Null
az provider register --namespace Microsoft.ContainerRegistry | Out-Null

Write-Host "Creating resource group if needed..."
az group create --name $ResourceGroup --location $Location | Out-Null

$workspaceName = "law-warehouse-mcp"
Write-Host "Creating Log Analytics workspace if needed..."
az monitor log-analytics workspace create --resource-group $ResourceGroup --workspace-name $workspaceName --location $Location | Out-Null

Write-Host "Creating ACR if needed..."
az acr create --resource-group $ResourceGroup --name $AcrName --sku Basic --admin-enabled true | Out-Null

Write-Host "Building and pushing image in ACR..."
az acr build --registry $AcrName --image "weather-mcp:$ImageTag" ./mcp-weather-server --no-logs | Out-Null

Write-Host "Fetching Log Analytics workspace details..."
$workspaceId = az monitor log-analytics workspace show --resource-group $ResourceGroup --workspace-name $workspaceName --query customerId --output tsv
$workspaceKey = az monitor log-analytics workspace get-shared-keys --resource-group $ResourceGroup --workspace-name $workspaceName --query primarySharedKey --output tsv

Write-Host "Creating Container Apps environment if needed..."
$envExists = az containerapp env show --name $EnvName --resource-group $ResourceGroup --query name --output tsv 2>$null
if (-not $envExists) {
    az containerapp env create --name $EnvName --resource-group $ResourceGroup --location $Location --logs-workspace-id $workspaceId --logs-workspace-key $workspaceKey | Out-Null
}

Write-Host "Getting ACR credentials..."
$acrServer = az acr show --name $AcrName --resource-group $ResourceGroup --query loginServer --output tsv
$acrUser = az acr credential show --name $AcrName --query username --output tsv
$acrPass = az acr credential show --name $AcrName --query passwords[0].value --output tsv

$image = "$acrServer/weather-mcp:$ImageTag"

Write-Host "Deploying or updating Container App..."
$appExists = az containerapp show --name $AppName --resource-group $ResourceGroup --query name --output tsv 2>$null
if (-not $appExists) {
    az containerapp create `
      --name $AppName `
      --resource-group $ResourceGroup `
      --environment $EnvName `
      --image $image `
      --ingress external `
      --target-port 8080 `
      --min-replicas 1 `
      --max-replicas 1 `
      --cpu 0.5 `
      --memory 1.0Gi `
  --env-vars FASTMCP_HOST=0.0.0.0 FASTMCP_PORT=8080 `
      --registry-server $acrServer `
      --registry-username $acrUser `
      --registry-password $acrPass `
      --query properties.configuration.ingress.fqdn --output tsv | Out-Null
} else {
    az containerapp update `
      --name $AppName `
      --resource-group $ResourceGroup `
      --image $image `
  --set-env-vars FASTMCP_HOST=0.0.0.0 FASTMCP_PORT=8080 `
            --min-replicas 1 `
            --max-replicas 1 | Out-Null
}

Write-Host "Enabling sticky sessions for MCP session affinity..."
az containerapp ingress sticky-sessions set `
    --name $AppName `
    --resource-group $ResourceGroup `
    --affinity sticky | Out-Null

$fqdn = az containerapp show --name $AppName --resource-group $ResourceGroup --query properties.configuration.ingress.fqdn --output tsv
$url = "https://$fqdn"

Write-Host "Deployment complete."
Write-Host "MCP URL: $url"
Write-Host "Use this URL in Copilot Studio MCP tool connection (append /mcp if required by the client)."
