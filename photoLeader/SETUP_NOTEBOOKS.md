# Guia Rápido: Configuração dos Notebooks MongoDB

Este guia descreve os comandos executados passo a passo para configurar cada notebook do Replica Set MongoDB.

---

## 📋 Pré-requisitos (verificar em cada notebook)

- ✅ Docker Desktop instalado e **rodando**
- ✅ Python 3.8+ instalado
- ✅ Todos os notebooks na mesma rede local (ex: 192.168.0.x)
- ✅ Porta 27017 liberada no Firewall do Windows

---

## 🔧 Configuração de Cada Notebook

### **IMPORTANTE:** Execute estes passos em CADA um dos 5 notebooks, alterando apenas o nome do container.

---

### **Passo 1: Verificar Docker**

Abra o PowerShell e execute:

```powershell
docker --version
docker ps
```

✅ Se funcionar, o Docker está OK. Se não, inicie o Docker Desktop antes de continuar.

---

### **Passo 2: Criar pasta de dados**

```powershell
mkdir C:\mongo\data -Force
```

---

### **Passo 3: Descobrir o IP do notebook**

```powershell
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.*"} | Select-Object IPAddress, InterfaceAlias
```

📝 **ANOTE O IP** deste notebook (ex: 192.168.0.3)

---

### **Passo 4: Subir o container MongoDB**

Execute o comando abaixo **alterando o nome do container** conforme o notebook:

#### **Notebook 1 (mongo1):**
```powershell
docker run -d --name mongo1 -p 27017:27017 -v C:\mongo\data:/data/db --restart unless-stopped mongo:6 mongod --replSet rsUpload --bind_ip_all
```

#### **Notebook 2 (mongo2):**
```powershell
docker run -d --name mongo2 -p 27017:27017 -v C:\mongo\data:/data/db --restart unless-stopped mongo:6 mongod --replSet rsUpload --bind_ip_all
```

#### **Notebook 3 (mongo3):**
```powershell
docker run -d --name mongo3 -p 27017:27017 -v C:\mongo\data:/data/db --restart unless-stopped mongo:6 mongod --replSet rsUpload --bind_ip_all
```

#### **Notebook 4 (mongo4):**
```powershell
docker run -d --name mongo4 -p 27017:27017 -v C:\mongo\data:/data/db --restart unless-stopped mongo:6 mongod --replSet rsUpload --bind_ip_all
```

#### **Notebook 5 (mongo5):**
```powershell
docker run -d --name mongo5 -p 27017:27017 -v C:\mongo\data:/data/db --restart unless-stopped mongo:6 mongod --replSet rsUpload --bind_ip_all
```

---

### **Passo 5: Verificar se o container está rodando**

```powershell
docker ps
```

✅ Você deve ver o container na lista (STATUS = "Up")

---

## 📝 Tabela de IPs (preencher conforme você anota)

| Notebook | Nome do Container | IP Real        | Status |
|----------|-------------------|----------------|--------|
| 1        | mongo1            | 192.168.0.3    | ✅     |
| 2        | mongo2            | 192.168.0.__   | ⏳     |
| 3        | mongo3            | 192.168.0.__   | ⏳     |
| 4        | mongo4            | 192.168.0.__   | ⏳     |
| 5        | mongo5            | 192.168.0.__   | ⏳     |

---

## 🚀 Inicialização do Replica Set (SOMENTE no Notebook 1)

**⚠️ Execute APENAS após todos os 5 containers estarem rodando!**

### **Passo 6: Editar o arquivo de configuração**

No **Notebook 1**, edite o arquivo `C:\mongo\init-replica.js` e substitua os IPs pelos valores reais anotados acima:

```javascript
rs.initiate({
  _id: "rsUpload",
  version: 1,
  members: [
    { _id: 0, host: "192.168.0.3:27017" },    // Notebook 1
    { _id: 1, host: "192.168.0.__:27017" },   // Notebook 2 - SUBSTITUA
    { _id: 2, host: "192.168.0.__:27017" },   // Notebook 3 - SUBSTITUA
    { _id: 3, host: "192.168.0.__:27017" },   // Notebook 4 - SUBSTITUA
    { _id: 4, host: "192.168.0.__:27017" }    // Notebook 5 - SUBSTITUA
  ]
});
```

---

### **Passo 7: Copiar e executar o script (SOMENTE no Notebook 1)**

```powershell
# Copiar o arquivo para dentro do container
docker cp C:\mongo\init-replica.js mongo1:/init-replica.js

# Executar o script de inicialização
docker exec -it mongo1 mongosh --eval "load('/init-replica.js')"
```

---

### **Passo 8: Verificar o status do Replica Set**

```powershell
docker exec -it mongo1 mongosh --eval "rs.status()"
```

✅ Procure por:
- Um membro com `"stateStr" : "PRIMARY"`
- Os outros com `"stateStr" : "SECONDARY"`

---

### **Passo 9: Criar usuário admin (opcional, mas recomendado)**

No **Notebook 1** (PRIMARY):

```powershell
docker exec -it mongo1 mongosh --eval "use uploadDB; db.createUser({ user: 'admin', pwd: 'admin123', roles: [{ role: 'readWrite', db: 'uploadDB' }] });"
```

---

## ✅ Verificação Final

Execute em qualquer notebook para testar a conexão:

```powershell
docker exec -it mongo1 mongosh --eval "db.adminCommand('ping')"
```

---

## 🔥 Comandos Úteis

### Parar um container:
```powershell
docker stop mongo1
```

### Iniciar um container parado:
```powershell
docker start mongo1
```

### Ver logs do container:
```powershell
docker logs mongo1
```

### Remover um container (cuidado!):
```powershell
docker stop mongo1
docker rm mongo1
```

### Verificar status do Replica Set:
```powershell
docker exec -it mongo1 mongosh --eval "rs.status()"
```

### Acessar o shell do MongoDB:
```powershell
docker exec -it mongo1 mongosh
```

---

## 🐛 Problemas Comuns

### "Cannot connect to Docker daemon"
- **Solução:** Inicie o Docker Desktop e aguarde até ele estar completamente carregado

### "Port 27017 already in use"
- **Solução:** Já existe um container rodando. Verifique com `docker ps -a` e remova se necessário

### "Network unreachable" entre notebooks
- **Solução:** Verifique se todos estão na mesma rede e libere a porta 27017 no Firewall

### Replica Set não elege PRIMARY
- **Solução:** Verifique se todos os 5 containers estão rodando e se os IPs estão corretos no `init-replica.js`

---

## 📌 Próximos Passos

Após ter o Replica Set funcionando, consulte o `README_WINDOWS.md` para:
- Configurar o ambiente Python no VS Code
- Executar scripts de upload/listagem/exclusão
- Testar failover (tolerância a falhas)

---

**Data de criação:** 27/10/2025  
**Versão MongoDB:** 6.x  
**Replica Set Name:** rsUpload
