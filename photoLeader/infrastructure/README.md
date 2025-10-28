# Infrastructure - PhotoLeader

Esta pasta contém todos os arquivos de infraestrutura para deploy e configuração do MongoDB Replica Set.

## 📁 Estrutura

```
infrastructure/
├── docker-compose.yml         # Configuração Docker Compose (local)
├── mongo-init.js             # Script de inicialização do Replica Set
├── setup-mongo.ps1           # Script PowerShell para setup local
├── deploy-remote.ps1         # Deploy remoto via PSRemoting/WinRM
├── verify-prereqs.ps1        # Verificação de pré-requisitos
├── show-db.ps1              # Visualizar dados do MongoDB
└── README.md                # Este arquivo
```

## 🐳 Docker Compose (Desenvolvimento Local)

### Uso

Para testar localmente com 5 containers MongoDB na mesma máquina:

```powershell
cd infrastructure
docker-compose up -d
```

Isso irá criar:
- 5 containers MongoDB (mongo1..mongo5)
- Portas: 27017, 27018, 27019, 27020, 27021
- Rede interna Docker para comunicação entre containers

### Parar os containers

```powershell
docker-compose down
```

### Ver logs

```powershell
docker-compose logs -f
```

## 🔧 Scripts PowerShell

### setup-mongo.ps1

Configura o MongoDB em um notebook individual.

**Uso local:**

```powershell
.\infrastructure\setup-mongo.ps1 -NodeIndex 1 -MemberIPs @("10.76.9.53","10.76.1.212","10.76.10.131","10.76.6.1") -ReplSetName rsUpload
```

**Parâmetros:**
- `-NodeIndex`: Índice do nó (1-5) determina qual container criar (mongo1..mongo5)
- `-MemberIPs`: Array com todos os IPs dos notebooks
- `-ReplSetName`: Nome do replica set (padrão: rsUpload)
- `-CreateAdmin`: Switch para criar usuário admin (use apenas no nó 1)

**O que faz:**
1. Cria a pasta `C:\mongo\data`
2. Sobe o container MongoDB com o nome apropriado
3. Se for o nó 1, inicializa o replica set
4. Opcionalmente cria o usuário admin

### deploy-remote.ps1

Automatiza o deploy em múltiplos notebooks via PowerShell Remoting (WinRM).

**Pré-requisitos:**
- WinRM habilitado em todos os notebooks: `Enable-PSRemoting -Force`
- TrustedHosts configurado (se fora de domínio):
  ```powershell
  Set-Item WSMan:\localhost\Client\TrustedHosts -Value "10.76.9.53,10.76.1.212,10.76.10.131,10.76.6.1" -Concatenate
  ```

**Uso:**

```powershell
$hosts = '10.76.9.53','10.76.1.212','10.76.10.131','10.76.6.1'
.\infrastructure\deploy-remote.ps1 -Hosts $hosts -LocalSetupScript .\infrastructure\setup-mongo.ps1 -ReplSetName rsUpload -CreateAdmin
```

**Parâmetros:**
- `-Hosts`: Array com IPs de todos os notebooks
- `-LocalSetupScript`: Caminho para o setup-mongo.ps1
- `-ReplSetName`: Nome do replica set
- `-CreateAdmin`: Cria usuário admin no nó 1

**O que faz:**
1. Conecta via PSRemoting em cada host
2. Copia o script setup-mongo.ps1 para o host remoto
3. Executa o script com os parâmetros corretos
4. No primeiro host, inicializa o replica set e cria admin

### verify-prereqs.ps1

Verifica se os pré-requisitos estão atendidos.

**Uso local:**

```powershell
.\infrastructure\verify-prereqs.ps1
```

**Uso remoto (múltiplos hosts):**

```powershell
$hosts = '10.76.9.53','10.76.1.212','10.76.10.131','10.76.6.1'
.\infrastructure\verify-prereqs.ps1 -Hosts $hosts
```

**Verifica:**
- ✅ Conectividade (ping)
- ✅ WinRM ativo
- ✅ Docker instalado e rodando
- ✅ Porta 27017 acessível

### show-db.ps1

Visualiza os dados no MongoDB de forma amigável.

**Uso:**

```powershell
.\infrastructure\show-db.ps1
```

**O que mostra:**
- Status do replica set
- Documentos na coleção
- Contagem de registros

## 📝 mongo-init.js

Script JavaScript para inicializar o Replica Set.

**Configuração atual:**

```javascript
rs.initiate({
  _id: "rsUpload",
  version: 1,
  members: [
    { _id: 0, host: "10.76.9.53:27017" },
    { _id: 1, host: "10.76.1.212:27017" },
    { _id: 2, host: "10.76.10.131:27017" },
    { _id: 3, host: "10.76.6.1:27017" }
  ]
});
```

**Para usar manualmente:**

```powershell
# Copiar para o container
docker cp infrastructure/mongo-init.js mongo1:/mongo-init.js

# Executar
docker exec -it mongo1 mongosh --eval "load('/mongo-init.js')"
```

## 🚀 Fluxo de Deploy Completo

### Cenário 1: Deploy Manual (notebook por notebook)

1. **Em cada notebook:**
   ```powershell
   # Verificar pré-requisitos
   .\infrastructure\verify-prereqs.ps1
   
   # Criar pasta de dados
   mkdir C:\mongo\data -Force
   
   # Subir container (alterar mongoX para mongo1, mongo2, etc)
   docker run -d --name mongo1 -p 27017:27017 -v C:\mongo\data:/data/db --restart unless-stopped mongo:6 mongod --replSet rsUpload --bind_ip_all
   ```

2. **No notebook 1 (PRIMARY):**
   ```powershell
   # Editar IPs no mongo-init.js
   notepad C:\mongo\init-replica.js
   
   # Copiar e executar
   docker cp C:\mongo\init-replica.js mongo1:/init-replica.js
   docker exec -it mongo1 mongosh --eval "load('/init-replica.js')"
   
   # Criar usuário
   docker exec -it mongo1 mongosh --eval "db.getSiblingDB('uploadDB').createUser({ user: 'admin', pwd: 'admin123', roles: [{ role: 'readWrite', db: 'uploadDB' }] });"
   ```

### Cenário 2: Deploy Automatizado (WinRM)

1. **No notebook central:**
   ```powershell
   # Habilitar PSRemoting em todos os hosts (fazer em cada um)
   # Ou via deploy remoto se já tiver acesso
   
   # Configurar TrustedHosts
   $hosts = '10.76.9.53','10.76.1.212','10.76.10.131','10.76.6.1'
   Set-Item WSMan:\localhost\Client\TrustedHosts -Value ($hosts -join ',') -Force
   
   # Verificar pré-requisitos
   .\infrastructure\verify-prereqs.ps1 -Hosts $hosts
   
   # Deploy
   .\infrastructure\deploy-remote.ps1 -Hosts $hosts -LocalSetupScript .\infrastructure\setup-mongo.ps1 -ReplSetName rsUpload -CreateAdmin
   ```

### Cenário 3: Teste Local (Docker Compose)

```powershell
cd infrastructure
docker-compose up -d

# Aguardar inicialização
Start-Sleep -Seconds 10

# Verificar status
docker exec -it mongo1 mongosh --eval "rs.status()"
```

## 🔍 Comandos Úteis

### Verificar status do Replica Set

```powershell
docker exec -it mongo1 mongosh --eval "rs.status()"
```

### Ver qual é o PRIMARY

```powershell
docker exec -it mongo1 mongosh --eval "rs.status().members.forEach(function(m) { print(m.name + ' - ' + m.stateStr); })"
```

### Contar documentos

```powershell
docker exec -it mongo1 mongosh --eval "db.getSiblingDB('uploadDB').files.countDocuments()"
```

### Backup do banco

```powershell
docker exec -it mongo1 mongodump --db uploadDB --out /backup
docker cp mongo1:/backup ./backup
```

## 🐛 Troubleshooting

### WinRM não conecta
```powershell
# No host remoto, habilitar
Enable-PSRemoting -Force

# No host local, adicionar aos trusted
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "IP_DO_HOST" -Concatenate
```

### Porta 27017 bloqueada
```powershell
# Liberar no Firewall
New-NetFirewallRule -DisplayName "MongoDB" -Direction Inbound -Protocol TCP -LocalPort 27017 -Action Allow
```

### Container não inicia
```powershell
# Ver logs
docker logs mongo1

# Remover e recriar
docker stop mongo1
docker rm mongo1
# Execute o comando docker run novamente
```

### Replica Set não elege PRIMARY
- Verificar conectividade entre os hosts
- Confirmar que todos os containers estão rodando
- Verificar IPs no init-replica.js

## 📌 Segurança

⚠️ **IMPORTANTE:** As configurações atuais são para ambiente de desenvolvimento/teste.

Para produção:
- [ ] Configurar autenticação com keyfile
- [ ] Usar certificados SSL/TLS
- [ ] Implementar firewall rules restritivas
- [ ] Usar senhas fortes (não `admin123`)
- [ ] Configurar backup automático
- [ ] Monitorar com ferramentas adequadas (Prometheus, etc)
