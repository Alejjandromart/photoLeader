<#
show-db.ps1

Mostra bancos, coleções e uma amostra de documentos do MongoDB.
Funciona em dois modos:
 1) Com container local chamado 'mongo1' (docker exec...)
 2) Com uma URI MongoDB remota (mongosh --host <uri>)

Uso:
  # modo container (padrão, se existir container 'mongo1')
  .\show-db.ps1

  # modo remoto usando URI com autenticação (ex: admin user)
  .\show-db.ps1 -Uri "mongodb://admin:admin123@192.168.0.11:27017,192.168.0.12:27017/?replicaSet=rsUpload"

Parâmetros:
  -Uri  : string com a MongoDB connection URI (opcional)
  -Limit: número de documentos de amostra a mostrar (padrão 10)
#>

param(
    [string]$Uri,
    [int]$Limit = 10
)

function Run-ContainerMode {
    param($containerName, $limit)

    Write-Host "Executando no modo container: $containerName" -ForegroundColor Cyan

    Write-Host "== Databases =="
    docker exec -i $containerName mongosh --quiet --eval "printjson(db.adminCommand({listDatabases:1}))"

    Write-Host "\n== Collections em uploadDB =="
    docker exec -i $containerName mongosh --quiet --eval "printjson(db.getSiblingDB('uploadDB').getCollectionNames())"

    Write-Host "\n== Amostra de documentos (uploadDB.files) =="
    docker exec -i $containerName mongosh --quiet --eval "printjson(db.getSiblingDB('uploadDB').files.find().limit($limit).toArray())"
}

function Run-UriMode {
    param($uri, $limit)

    Write-Host "Executando no modo URI: $uri" -ForegroundColor Cyan

    Write-Host "== Databases =="
    mongosh --quiet "$uri" --eval "printjson(db.adminCommand({listDatabases:1}))"

    Write-Host "\n== Collections em uploadDB =="
    mongosh --quiet "$uri" --eval "printjson(db.getSiblingDB('uploadDB').getCollectionNames())"

    Write-Host "\n== Amostra de documentos (uploadDB.files) =="
    mongosh --quiet "$uri" --eval "printjson(db.getSiblingDB('uploadDB').files.find().limit($limit).toArray())"
}

# Detectar se existe container mongo1
$containerExists = $false
try {
    $names = docker ps --format "{{.Names}}" 2>$null
    if ($names) {
        foreach ($n in $names) { if ($n -eq 'mongo1') { $containerExists = $true; break } }
    }
} catch {
    Write-Host "Aviso: docker não parece instalado/correto ou não está em execução. Erro: $_" -ForegroundColor Yellow
}

if ($Uri) {
    Run-UriMode -uri $Uri -limit $Limit
} elseif ($containerExists) {
    Run-ContainerMode -containerName 'mongo1' -limit $Limit
} else {
    Write-Host "Nenhum container 'mongo1' detectado e nenhuma URI fornecida. Use -Uri ou inicie o container." -ForegroundColor Red
    Write-Host "Exemplo: .\show-db.ps1 -Uri \"mongodb://admin:admin123@192.168.0.11:27017/?replicaSet=rsUpload\"" -ForegroundColor Yellow
}
