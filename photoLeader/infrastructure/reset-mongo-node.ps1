# Script para resetar um nó MongoDB e prepará-lo para entrar no Replica Set
# Execute este script nos Notebooks 3, 4 e 5

param(
    [Parameter(Mandatory=$true)]
    [string]$NodeName  # Ex: mongo3, mongo4, mongo5
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Resetando nó: $NodeName" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Passo 1: Parar o container
Write-Host "[1/4] Parando container $NodeName..." -ForegroundColor Yellow
docker stop $NodeName 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Container parado com sucesso" -ForegroundColor Green
} else {
    Write-Host "⚠️  Container não estava rodando" -ForegroundColor Gray
}

# Passo 2: Remover o container
Write-Host "[2/4] Removendo container $NodeName..." -ForegroundColor Yellow
docker rm $NodeName 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Container removido com sucesso" -ForegroundColor Green
} else {
    Write-Host "⚠️  Container não existia" -ForegroundColor Gray
}

# Passo 3: Limpar dados antigos
Write-Host "[3/4] Limpando dados antigos (C:\mongo\data)..." -ForegroundColor Yellow
if (Test-Path "C:\mongo\data") {
    Remove-Item -Path "C:\mongo\data\*" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Dados removidos com sucesso" -ForegroundColor Green
} else {
    Write-Host "⚠️  Pasta não existia" -ForegroundColor Gray
}

# Recriar a pasta
mkdir C:\mongo\data -Force | Out-Null

# Passo 4: Recriar o container MongoDB
Write-Host "[4/4] Recriando container $NodeName..." -ForegroundColor Yellow
docker run -d --name $NodeName -p 27017:27017 -v C:\mongo\data:/data/db --restart unless-stopped mongo:6 mongod --replSet rsUpload --bind_ip_all

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Container criado e rodando!" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  ✅ Resetado com sucesso!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Agora, no NOTEBOOK 1, execute:" -ForegroundColor Yellow
    Write-Host "docker exec -it mongo1 mongosh --eval `"rs.add('SEU_IP_AQUI:27017')`"" -ForegroundColor White
} else {
    Write-Host "❌ Erro ao criar container!" -ForegroundColor Red
}
