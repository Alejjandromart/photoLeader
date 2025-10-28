# Backend - PhotoLeader

Esta pasta contém todo o código backend do sistema PhotoLeader, incluindo clientes Python para interação com o MongoDB Replica Set.

## 📁 Estrutura

```
backend/
├── client/              # Scripts Python para operações no MongoDB
│   ├── upload_sim.py   # Simula uploads de metadados de fotos
│   └── read_sim.py     # Lista/busca metadados com leitura em secondaries
├── tests/              # Testes unitários
├── requirements.txt    # Dependências Python
└── README.md          # Este arquivo
```

## 🚀 Configuração

### 1. Ativar ambiente virtual (se ainda não estiver ativo)

```powershell
# Na raiz do projeto
.\.venv\Scripts\Activate.ps1
```

### 2. Instalar dependências

```powershell
pip install -r backend/requirements.txt
```

Ou instalar manualmente:

```powershell
pip install pymongo
```

## 📝 Scripts Disponíveis

### upload_sim.py

Simula upload de metadados de fotos para o MongoDB Replica Set.

**Uso:**

```powershell
# Upload com configuração padrão (3 documentos)
python backend/client/upload_sim.py

# Upload com número específico de documentos
python backend/client/upload_sim.py --count 10

# Upload usando URI customizada
python backend/client/upload_sim.py --count 5 --uri "mongodb://user:pass@host:port/db?replicaSet=rsName"
```

**Características:**
- Usa `writeConcern=majority` para garantir consistência
- Conecta automaticamente ao Replica Set configurado
- Gera metadados aleatórios (filename, user, tags, etc)

### read_sim.py

Lista metadados de fotos do MongoDB, usando preferência de leitura em SECONDARY nodes.

**Uso:**

```powershell
# Listar todos os uploads (últimos 20)
python backend/client/read_sim.py

# Filtrar por tag
python backend/client/read_sim.py --tag natureza
python backend/client/read_sim.py --tag urbano

# URI customizada
python backend/client/read_sim.py --uri "mongodb://user:pass@host:port/db?replicaSet=rsName"
```

**Características:**
- Usa `readPreference=secondaryPreferred` para escalar leituras
- Suporta filtro por tags
- Limita resultados (padrão: 20)

## 🔧 Configuração do Replica Set

Os scripts estão configurados para conectar ao Replica Set com as seguintes configurações:

```python
REPLICA_URI = "mongodb://admin:admin123@10.76.9.53:27017,10.76.1.212:27017,10.76.10.131:27017,10.76.6.1:27017/uploadDB?replicaSet=rsUpload"

DB_NAME = 'uploadDB'
COLLECTION = 'files'
```

**Para alterar a conexão:**
1. Edite os arquivos `client/upload_sim.py` e `client/read_sim.py`
2. Modifique a variável `REPLICA_URI` com seus IPs/credenciais
3. Ou use o parâmetro `--uri` ao executar os scripts

## 🧪 Testes

Execute os testes com pytest:

```powershell
pytest backend/tests/ -v
```

## 📊 Exemplos de Uso

### Teste de carga - Upload contínuo

```powershell
# Upload de 100 documentos
python backend/client/upload_sim.py --count 100
```

### Verificar dados inseridos

```powershell
# Listar todos
python backend/client/read_sim.py

# Filtrar por tag específica
python backend/client/read_sim.py --tag macro
```

## 🔍 Estrutura de Documentos

Os documentos inseridos seguem este formato:

```json
{
  "_id": ObjectId("..."),
  "filename": "image_1234567890_0.jpg",
  "user": "user_3",
  "tags": ["natureza", "paisagem"],
  "upload_date": ISODate("2025-10-28T10:00:00Z"),
  "status": "uploaded",
  "size_kb": 2450
}
```

## 🛠️ Desenvolvimento

Para adicionar novos scripts ou funcionalidades:

1. Crie um novo arquivo Python em `backend/client/`
2. Importe `pymongo` e use a função `make_client()` para conexão
3. Adicione testes correspondentes em `backend/tests/`
4. Atualize este README com a documentação

## 📌 Notas Importantes

- **Write Concern:** Os uploads usam `w='majority'` para garantir que os dados sejam replicados antes de confirmar
- **Read Preference:** As leituras preferem SECONDARY nodes para distribuir a carga
- **Timeout:** Configurado para 5 segundos de timeout de conexão
- **Replica Set:** Nome configurado: `rsUpload`

## 🐛 Troubleshooting

### Erro: "No module named 'pymongo'"
```powershell
pip install pymongo
```

### Erro: "ServerSelectionTimeoutError"
- Verifique se todos os containers MongoDB estão rodando
- Teste conectividade: `Test-NetConnection -ComputerName <IP> -Port 27017`
- Verifique se os IPs no `REPLICA_URI` estão corretos

### Erro: "Authentication failed"
- Verifique usuário/senha na URI
- Confirme que o usuário foi criado: `docker exec -it mongo1 mongosh --eval "use uploadDB; db.getUsers()"`
