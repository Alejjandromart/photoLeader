# Script para adicionar todos os nós ao Replica Set
# Execute SOMENTE no Notebook 1, APÓS resetar os outros notebooks

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Adicionando nós ao Replica Set" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar status atual
Write-Host "[0/3] Verificando status atual..." -ForegroundColor Yellow
docker exec -it mongo1 mongosh --eval "rs.status().members.forEach(m => print(m._id + ': ' + m.name + ' - ' + m.stateStr))"
Write-Host ""

# Adicionar mongo3
Write-Host "[1/3] Adicionando mongo3 (10.76.10.131:27017)..." -ForegroundColor Yellow
docker exec -it mongo1 mongosh --eval "rs.add('10.76.10.131:27017')"
Start-Sleep -Seconds 3

# Adicionar mongo4
Write-Host "[2/3] Adicionando mongo4 (10.76.6.1:27017)..." -ForegroundColor Yellow
docker exec -it mongo1 mongosh --eval "rs.add('10.76.6.1:27017')"
Start-Sleep -Seconds 3

# Adicionar mongo5
Write-Host "[3/3] Adicionando mongo5 (10.76.1.61:27017)..." -ForegroundColor Yellow
docker exec -it mongo1 mongosh --eval "rs.add('10.76.1.61:27017')"
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✅ Todos os nós adicionados!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar status final
Write-Host "Status final do Replica Set:" -ForegroundColor Yellow
docker exec -it mongo1 mongosh --eval "rs.status().members.forEach(m => print(m._id + ': ' + m.name + ' - ' + m.stateStr))"
