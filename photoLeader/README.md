# PhotoLeader — MongoDB Replica Set

Sistema de gerenciamento de uploads de fotos com MongoDB Replica Set para alta disponibilidade e escalabilidade. Metadados de fotos são armazenados no MongoDB com replicação em múltiplos nós.

## 📁 Estrutura do Projeto

```
photoLeader/
├── backend/              # Código backend (Python + MongoDB)
│   ├── client/          # Scripts Python para interação com MongoDB
│   ├── tests/           # Testes unitários
│   └── README.md        # Documentação do backend
├── frontend/            # Interface web (HTML/CSS/JS)
│   ├── *.html          # Páginas da aplicação
│   ├── *.css           # Estilos
│   ├── *.js            # Scripts frontend
│   ├── img/            # Imagens e assets
│   └── README.md       # Documentação do frontend
├── infrastructure/      # Scripts de infraestrutura e deploy
│   ├── docker-compose.yml      # Orquestra 5 containers MongoDB localmente
│   ├── mongo-init.js           # Inicialização do Replica Set
│   ├── setup-mongo.ps1         # Setup automatizado Windows
│   ├── deploy-remote.ps1       # Deploy remoto via WinRM
│   ├── verify-prereqs.ps1      # Verificação de pré-requisitos
│   └── README.md               # Documentação de infraestrutura
├── .venv/               # Ambiente virtual Python (criado localmente)
├── README.md            # Este arquivo - visão geral
├── README_WINDOWS.md    # Guia detalhado para Windows
└── SETUP_NOTEBOOKS.md   # Guia rápido de configuração dos notebooks
```

## 🚀 Quick Start

### Opção 1: Teste Local (Docker Compose)

Para testar rapidamente com 5 containers MongoDB na mesma máquina:

```powershell
# 1. Subir os containers
cd infrastructure
docker-compose up -d

# 2. Aguardar inicialização
Start-Sleep -Seconds 10

# 3. Verificar status
docker exec -it mongo1 mongosh --eval "rs.status()"

# 4. Instalar dependências Python
cd ..
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install pymongo

# 5. Testar uploads
python backend/client/upload_sim.py --count 10

# 6. Listar dados
python backend/client/read_sim.py
```

### Opção 2: Deploy em Notebooks Físicos

Para configurar o Replica Set em 4-5 notebooks diferentes na rede local:

1. **Siga o guia detalhado:** [`SETUP_NOTEBOOKS.md`](SETUP_NOTEBOOKS.md)
2. **Ou leia o guia completo:** [`README_WINDOWS.md`](README_WINDOWS.md)

## 📚 Documentação por Componente

- **[Backend](backend/README.md)** - Scripts Python, conexão MongoDB, testes
- **[Frontend](frontend/README.md)** - Páginas web, estilos, interatividade
- **[Infrastructure](infrastructure/README.md)** - Docker, deploy, scripts PowerShell

## 🎯 Funcionalidades

### Alta Disponibilidade
- **Replica Set** com 4-5 nós (1 Primary + 3-4 Secondaries)
- **Failover automático** - se o Primary cair, um Secondary é promovido
- **Write Concern majority** - garante que dados sejam replicados antes de confirmar

### Escalabilidade de Leitura
- **Read Preference secondaryPreferred** - distribui leituras nos Secondaries
- Reduz carga no Primary
- Melhora performance de consultas

### Metadados de Upload
Documentos armazenados:
```json
{
  "_id": ObjectId("..."),
  "filename": "image_1234567890.jpg",
  "user": "user_3",
  "tags": ["natureza", "paisagem"],
  "upload_date": ISODate("2025-10-28T10:00:00Z"),
  "status": "uploaded",
  "size_kb": 2450
}
```

## 🛠️ Tecnologias

- **MongoDB 6** - Banco de dados NoSQL com suporte a Replica Set
- **Python 3.12+** - Scripts backend
- **pymongo** - Driver Python para MongoDB
- **Docker** - Containerização
- **PowerShell** - Scripts de automação Windows
- **HTML/CSS/JavaScript** - Interface web

## 📖 Guias Disponíveis

1) Levantar o cluster:

```powershell
# a partir da pasta onde está o docker-compose.yml
docker-compose up -d
```

O serviço `mongo-setup` tentará rodar `mongo-init.js` e iniciar o replica set. Aguarde alguns segundos e verifique os containers:

```powershell
docker ps
```

2) Instalar dependências Python:

```powershell
python -m pip install -r requirements.txt
```

3) Simular uploads:

```powershell
python client\upload_sim.py --count 10
```

Este script insere documentos com writeConcern majority para garantir que a escrita foi registrada pelo quórum.

4) Ler a galeria a partir dos Secondaries:

```powershell
python client\read_sim.py --tag natureza
```

5) Simular falha do Primary (em outra janela PowerShell):

Primeiro identifique o Primary (em um container execute `rs.status()` ou verifique logs). Para simular:

```powershell
# pare o container mongo1 (supondo que seja o Primary)
docker stop mongo1
```

Observe que o Replica Set fará uma nova eleição. Você pode continuar inserindo (o cliente Python irá apontar para o novo Primary depois da eleição) e medir o tempo de failover.

Observações:
- Os scripts Python usam `localhost:27017..27021` como seeds — execute-os localmente na máquina que está rodando os containers.
- Em ambientes diferentes (por exemplo, deploy em VMs separadas), ajuste os hosts/ports na `docker-compose.yml` e nos scripts.

Próximos passos sugeridos:
- Adicionar testes automáticos (latência de failover, latência de escrita/ leitura de segundo nível).
- Instrumentar logs para medir tempos de failover em diferentes condições.
- Integrar com um storage de objetos (S3) para arquivos binários; MongoDB fica apenas com metadados.

Instruções para os notebooks (nós) — deploy em múltiplas máquinas
-------------------------------------------------------------

Se você vai executar o cluster distribuído em 5 notebooks (cada um como um nó do Replica Set), siga o guia específico para os nós disponível em `README_NODES.md`. Esse arquivo contém passo-a-passo para cada notebook:

- pré-requisitos (Docker Desktop, PowerShell/WinRM, permissões administrativas);
- criação da pasta de dados (`C:\\mongo\\data`);
- habilitação do PowerShell Remoting (`Enable-PSRemoting -Force`) e instruções sobre TrustedHosts;
- opção de executar `setup-mongo.ps1` localmente em cada nó ou receber o deploy remoto via `deploy-remote.ps1`;
- checagens de verificação e troubleshooting básicos.

Link rápido para o guia dos nós: `README_NODES.md` (recomendo adicioná-lo ao GitHub junto com este repositório).

Setup rápido para cada notebook (copiar para o GitHub)
--------------------------------------------------

Se você for um dos donos dos notebooks que participarão do cluster, siga este resumo rápido antes do deploy remoto:

1) Abra PowerShell como Administrador.
2) Instale e inicie o Docker Desktop; confirme com:

```powershell
docker version --format '{{.Server.Version}}'
```

3) Crie a pasta de dados local que será montada pelo container:

```powershell
mkdir C:\mongo\data -Force
```

4) Habilite PowerShell Remoting (WinRM) para permitir deploy remoto:

```powershell
Enable-PSRemoting -Force
# (opcional na máquina central) Set-Item WSMan:\localhost\Client\TrustedHosts -Value "<lista-de-hosts>" -Concatenate
```

5) Abra as portas necessárias no firewall se aplicável: 5985 (WinRM HTTP) e 27017 (MongoDB).

6) Aguarde o administrador rodar o deploy remoto ou execute localmente `setup-mongo.ps1` com o NodeIndex correto:

```powershell
# No notebook 1 (nodeIndex 1)
.\setup-mongo.ps1 -NodeIndex 1 -MemberIPs '192.168.0.11,192.168.0.12,192.168.0.13,192.168.0.14,192.168.0.15' -CreateAdmin

# Em outros notebooks (nodeIndex 2..5)
.\setup-mongo.ps1 -NodeIndex 2 -MemberIPs '192.168.0.11,192.168.0.12,192.168.0.13,192.168.0.14,192.168.0.15'
```

7) Verifique que o Replica Set está ativo (no node 1):

```powershell
docker exec -it mongo1 mongosh --eval "rs.status()"
```

8) Confirme que a base `uploadDB` e a collection `files` existem:

```powershell
docker exec -it mongo1 mongosh --eval "use uploadDB; show collections; db.files.getIndexes();"
```

Observação: instruções completas e troubleshooting estão em `README_NODES.md`.
