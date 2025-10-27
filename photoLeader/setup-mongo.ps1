<#
setup-mongo.ps1

Script auxiliar para Windows (PowerShell) que automatiza a criação do container MongoDB e,
no node 1, inicializa o Replica Set com os IPs fornecidos.

Uso: execute em cada notebook com privilégios administrativos.
#>

param(
    [Parameter(Mandatory=$true)]
    [int]$NodeIndex,

    [Parameter(Mandatory=$true)]
    [string]$MemberIPs, # Ex: "192.168.0.11,192.168.0.12,192.168.0.13,192.168.0.14,192.168.0.15"

    [string]$ContainerNamePrefix = 'mongo',
    [string]$ReplSetName = 'rsUpload',
    [switch]$CreateAdmin
)

function Ensure-Path([string]$p) {
    if (-not (Test-Path $p)) {
        New-Item -ItemType Directory -Path $p -Force | Out-Null
    }
}

Write-Host "== Setup MongoDB container (node $NodeIndex) =="

# Validate IPs
$ips = $MemberIPs.Split(',') | ForEach-Object { $_.Trim() }
if ($ips.Count -ne 5) {
    Write-Error "Parameter MemberIPs must contain exactly 5 comma-separated IPs. Ex: 192.168.0.11,192.168.0.12,192.168.0.13,192.168.0.14,192.168.0.15"
    exit 1
}

# Prepare data directory
$dataRoot = 'C:\mongo\data'
Ensure-Path $dataRoot

$containerName = "${ContainerNamePrefix}${NodeIndex}"

# Run container (idempotent: if exists, show message)
$exists = docker ps -a --format "{{.Names}}" | Where-Object { $_ -eq $containerName }
if ($exists) {
    Write-Host "Container $containerName já existe. Pulando criação. (Você pode parar/remover manualmente se quiser recriar.)"
} else {
    Write-Host "Criando container $containerName ..."
    docker run -d `
      --name $containerName `
      -p 27017:27017 `
      -v C:\mongo\data:/data/db `
      --restart unless-stopped `
      mongo:6 `
      mongod --replSet $ReplSetName --bind_ip_all

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Falha ao criar container $containerName. Verifique Docker Desktop e execute novamente."
        exit 1
    }
}

# If this is node 1, create the init file and run rs.initiate
if ($NodeIndex -eq 1) {
    Write-Host "Gerando init-replica.js em C:\mongo ..."

    $membersJS = @()
    for ($i=0; $i -lt $ips.Count; $i++) {
        $membersJS += "    { _id: $i, host: \"$($ips[$i]):27017\" }"
    }

    $initContent = @"
rs.initiate({
  _id: \"$ReplSetName\",
  version: 1,
  members: [
$($membersJS -join ",`n")
  ]
});
"@

    $initPath = 'C:\mongo\init-replica.js'
    $initContent | Out-File -FilePath $initPath -Encoding ascii -Force

    Write-Host "Copiando init-replica.js para o container $containerName ..."
    docker cp $initPath $containerName:/init-replica.js

    Write-Host "Executando mongosh para carregar o script de inicialização..."
    docker exec -it $containerName mongosh --eval "load('/init-replica.js')"

    Write-Host "Verificando o status do Replica Set (aguarde alguns segundos) ..."
    Start-Sleep -Seconds 3
    docker exec -it $containerName mongosh --eval "rs.status()"

    # Criar usuário admin se solicitado
    if ($CreateAdmin.IsPresent) {
        Write-Host "Criando usuário admin no banco uploadDB ..."
        docker exec -it $containerName mongosh --eval "use uploadDB; db.createUser({ user: 'admin', pwd: 'admin123', roles: [{ role: 'readWrite', db: 'uploadDB' }] });"
    }

    # Criar base de dados e índices da aplicação (upload metadata)
    Write-Host "Criando base uploadDB e índices (files.upload_date, files.user, files.tags) ..."
    $createDbCmd = "var appDB = db.getSiblingDB('uploadDB'); if (!appDB.getCollectionNames().includes('files')) { appDB.createCollection('files'); } appDB.files.createIndex({ upload_date: -1 }); appDB.files.createIndex({ user: 1 }); appDB.files.createIndex({ tags: 1 }); print('DB/indexes ready');"
    docker exec -it $containerName mongosh --eval $createDbCmd
}

Write-Host "Setup concluído para node $NodeIndex. (container: $containerName)"
Write-Host "IPs do cluster: $MemberIPs"

Write-Host "Dica: execute 'docker logs $containerName' para ver logs do mongod se precisar debugar."
