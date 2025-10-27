# PhotoLeader — Guia completo (Windows, Docker Desktop e PowerShell)

Este documento descreve passo a passo como montar um MongoDB Replica Set com 5 nós distribuídos em 5 notebooks Windows na mesma rede local, e como executar os scripts Python (upload/list/delete) no VS Code.

IMPORTANTE: Substitua os IPs de exemplo pelos IPs reais da sua rede local antes de executar os comandos.

---

## 1) Pré-requisitos (em todos os notebooks)

Verifique em cada notebook:

- Docker Desktop instalado e funcionando (suporte a containers Linux).
- Python 3.8+ e pip.
- Visual Studio Code com extensão Python.
- Todos os notebooks na mesma rede local (mesmo subnet). Ex: `192.168.0.x`.
- Porta TCP 27017 permitida pelo Firewall do Windows (ou crie regra específica).

---

## 2) Exemplo de IPs (substitua pelos seus)

| Notebook | Nome   | IP exemplo       |
| -------- | ------ | ---------------- |
| 1        | mongo1 | 192.168.0.11     |
| 2        | mongo2 | 192.168.0.12     |
| 3        | mongo3 | 192.168.0.13     |
| 4        | mongo4 | 192.168.0.14     |
| 5        | mongo5 | 192.168.0.15     |

---

## 3) Criar pasta de dados (em cada notebook)

Abra o PowerShell como Administrador e execute:

```powershell
mkdir C:\mongo\data
```

(Se preferir outro caminho, use-o, mas mantenha consistência nos comandos abaixo.)

---

## 4) Subir um contêiner MongoDB em cada notebook

Em cada notebook você executará um comando `docker run` similar. O nome do container deve ser único (mongo1..mongo5). A seguir exemplo para cada notebook — repita em cada máquina, alterando apenas `--name`.

Exemplo (Notebook 1 — pode se tornar Primary após a eleição):

```powershell
docker run -d `
  --name mongo1 `
  -p 27017:27017 `
  -v C:\mongo\data:/data/db `
  --restart unless-stopped `
  mongo:6 `
  mongod --replSet rsUpload --bind_ip_all
```

Nos outros notebooks (mongo2..mongo5) use o mesmo comando trocando `--name mongoX` para `mongo2`, `mongo3`, etc.

Verifique containers em cada notebook:

```powershell
docker ps
```

---

## 5) Criar `init-replica.js` (somente no Notebook 1)

No Notebook 1, crie o arquivo `C:\mongo\init-replica.js` com o conteúdo abaixo (ajuste IPs reais):

```javascript
rs.initiate({
  _id: "rsUpload",
  version: 1,
  members: [
    { _id: 0, host: "192.168.0.11:27017" },
    { _id: 1, host: "192.168.0.12:27017" },
    { _id: 2, host: "192.168.0.13:27017" },
    { _id: 3, host: "192.168.0.14:27017" },
    { _id: 4, host: "192.168.0.15:27017" }
  ]
});
```

---

## 6) Inicializar o Replica Set (somente no Notebook 1)

Copie o arquivo para o container `mongo1` e execute o script com `mongosh`:

```powershell
docker cp C:\mongo\init-replica.js mongo1:/init-replica.js
docker exec -it mongo1 mongosh --eval "load('/init-replica.js')"
```

Verifique o status e aguarde eleições:

```powershell
docker exec -it mongo1 mongosh --eval "rs.status()"
```

Procure uma saída onde um membro esteja `"stateStr" : "PRIMARY"` e os demais `SECONDARY`.

---

## 7) Criar usuário do banco (opcional, segurança)

No PRIMARY (notebook 1):

```powershell
docker exec -it mongo1 mongosh --eval "use uploadDB; db.createUser({ user: 'admin', pwd: 'admin123', roles: [{ role: 'readWrite', db: 'uploadDB' }] });"
```

---

## 8) (Opcional) Deploy remoto via PSRemoting / WinRM

Se você prefere automatizar a instalação em múltiplos notebooks a partir de uma máquina central, use o script `deploy-remote.ps1` que acompanha este repositório. Ele copia `setup-mongo.ps1` para cada host via PowerShell Remoting (WinRM) e executa o script remotamente.

Pré-requisitos para usar `deploy-remote.ps1`:
- WinRM habilitado em cada host: execute como Administrador em cada notebook:

```powershell
Enable-PSRemoting -Force
```

- Se as máquinas não estiverem em um domínio, permita TrustedHosts (execute na máquina que vai disparar o deploy):

```powershell
# permitir comunicação com hosts específicos
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "192.168.0.11,192.168.0.12,192.168.0.13,192.168.0.14,192.168.0.15" -Concatenate
```

- Certifique-se de que a porta WinRM (5985) está liberada no firewall se necessário.

Como usar (exemplo): no seu notebook central, abra PowerShell como Administrador e execute:

```powershell
$hosts = '192.168.0.11','192.168.0.12','192.168.0.13','192.168.0.14','192.168.0.15'
.\deploy-remote.ps1 -Hosts $hosts -LocalSetupScript .\setup-mongo.ps1 -ReplSetName rsUpload -CreateAdmin
```

O script pedirá credenciais (use usuário administrador que exista em cada host). Ele copiará `setup-mongo.ps1` para `C:\Temp` em cada host e o executará com os parâmetros corretos (NodeIndex, MemberIPs e -CreateAdmin somente no NodeIndex 1).

Se o seu ambiente requer HTTPS/5986 ou Kerberos, adapte a configuração de WinRM/TrustedHosts conforme a sua política de rede.

---

## 9) Verificar pré-requisitos automaticamente

Incluí um script `verify-prereqs.ps1` que verifica os pré-requisitos em cada host (ou localmente): ping, WinRM, porta 27017 e disponibilidade do Docker.

Uso local (verificações na máquina atual):

```powershell
.\verify-prereqs.ps1
```

Uso remoto (verificações em múltiplos hosts via PSRemoting):

```powershell
$hosts = '192.168.0.11','192.168.0.12','192.168.0.13','192.168.0.14','192.168.0.15'
.\verify-prereqs.ps1 -Hosts $hosts
```

Se o seu WinRM usa HTTPS, passe `-UseHttps` ao script remoto.

O script pedirá credenciais para conexão remota e imprimirá um resumo com [OK]/[FAIL] para cada verificação.

---

Anote usuário/senha — serão usados na string de conexão dos scripts Python.

---

## 8) Preparar ambiente Python no VS Code (em qualquer notebook que rodará os scripts cliente)

1) Crie uma pasta do projeto (ex: `C:\projects\upload-system`) e abra no VS Code.

2) No terminal PowerShell do VS Code:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install pymongo
```

3) (Opcional) instale `pytest` para rodar os testes locais se desejar:

```powershell
pip install pytest
```

---

## 9) Scripts Python (salve em `C:\projects\upload-system\scripts`) 

Abaixo três scripts mínimos. Ajuste a string de conexão com seus IPs e as credenciais se você criou usuário.

### upload.py

```python
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://admin:admin123@192.168.0.11:27017,192.168.0.12:27017,192.168.0.13:27017,192.168.0.14:27017,192.168.0.15:27017/?replicaSet=rsUpload")
db = client["uploadDB"]
uploads = db["files"]

novo_upload = {
    "usuario": "dieglison",
    "arquivo": "foto_teste.jpg",
    "tipo": "imagem",
    "data_upload": datetime.now(),
    "status": "armazenado"
}

uploads.insert_one(novo_upload)
print("✅ Upload realizado com sucesso!")
```

### list_files.py

```python
from pymongo import MongoClient

client = MongoClient("mongodb://admin:admin123@192.168.0.11:27017,192.168.0.12:27017,192.168.0.13:27017,192.168.0.14:27017,192.168.0.15:27017/?replicaSet=rsUpload", readPreference="secondaryPreferred")
db = client["uploadDB"]

for a in db["files"].find().sort("data_upload", -1):
    print(a)
```

### delete_file.py

```python
from pymongo import MongoClient

nome_arquivo = input("Digite o nome do arquivo a remover: ")

client = MongoClient("mongodb://admin:admin123@192.168.0.11:27017,192.168.0.12:27017,192.168.0.13:27017,192.168.0.14:27017,192.168.0.15:27017/?replicaSet=rsUpload")
db = client["uploadDB"]

resultado = db["files"].delete_one({"arquivo": nome_arquivo})

if resultado.deleted_count > 0:
    print(f"✅ Arquivo '{nome_arquivo}' removido com sucesso.")
else:
    print("⚠️ Nenhum arquivo encontrado.")
```

---

## 10) Executar os scripts (no VS Code PowerShell)

```powershell
# ative o venv
.\.venv\Scripts\Activate.ps1
python .\scripts\upload.py
python .\scripts\list_files.py
python .\scripts\delete_file.py
```

---

## 11) Testar Failover (tolerância a falhas)

1) Em um notebook, verifique o Primary (ex: docker exec -it mongo1 mongosh --eval "rs.status()")

2) Derrube o container do Primary (execute no notebook que está rodando o container Primary):

```powershell
docker stop mongo1
```

3) Em outro notebook/terminal verifique `rs.status()` em outro membro para ver a nova eleição:

```powershell
docker exec -it mongo2 mongosh --eval "rs.status()"
```

4) Suba novamente o container parado:

```powershell
docker start mongo1
```

Observações: durante failover o cluster pode demorar alguns segundos para eleger novo Primary. As aplicações que escrevem devem usar writeConcern apropriado (ex: majority) para garantir durabilidade.

---

## 12) Firewall e rede

- Abra a porta TCP 27017 no Firewall do Windows (ou crie regra de entrada para o Docker Desktop). 
- Permita `Docker Desktop` nas aplicações permitidas.
- Teste conectividade com `ping 192.168.0.X` e `Test-NetConnection -ComputerName 192.168.0.X -Port 27017` no PowerShell.

---

## 13) Testes locais (pytest)

Se quiser rodar os testes unitários que simulam os clientes (mocks):

```powershell
# no diretório do projeto
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
```

Os testes que acompanham este repositório são unitários e não sobem containers; para testes de integração automáticos é necessário um setup adicional que sobe o cluster antes dos testes.

---

## 14) Troubleshooting rápido

- "Cannot reach primary": confira se os IPs estão corretos e a porta 27017 está aberta.
- Replica set não inicia: verifique logs do container `docker logs mongo1` e execute `rs.status()`.
- Erro de autenticação: confirme usuário/senha e as roles.

---

## 15) Próximos passos sugeridos

- Automatizar deploy com um script PowerShell que execute `docker run` em todas as máquinas (via SSH/WinRM) — requer configuração de acesso remoto.
- Criar testes de integração que: sobem cluster, executam uploads contínuos, param o Primary e medem tempo de failover.
- Integrar um storage de objetos (S3/MinIO) para armazenar blobs e deixar o MongoDB apenas com metadados.

---

Se quiser, eu posso:

- gerar um arquivo PowerShell que automatiza os passos em cada notebook (ex.: `setup-mongo.ps1`) para rodar localmente;
- criar um script de integração que sobe os containers via Docker Compose (alternativa para rodar tudo numa única máquina com múltiplos containers);
- atualizar o `README.md` principal substituindo/mesclando esse guia Windows.

Diga qual opção prefere e eu implemento o próximo artefato.
