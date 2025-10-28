# 📁 Reorganização do Projeto PhotoLeader

## ✅ O que foi feito

O projeto PhotoLeader foi reorganizado para separar claramente as responsabilidades de cada componente, facilitando manutenção e desenvolvimento.

## 🔄 Estrutura ANTES vs DEPOIS

### ANTES (Raiz desorganizada)
```
photoLeader/
├── cadastro.html
├── login.html
├── estiloCad.css
├── script.js
├── upload_sim.py (em client/)
├── docker-compose.yml
├── setup-mongo.ps1
├── ... (30+ arquivos misturados)
```

### DEPOIS (Organizada por função)
```
photoLeader/
├── backend/              ← SCRIPTS PYTHON E LÓGICA
│   ├── client/
│   │   ├── upload_sim.py
│   │   └── read_sim.py
│   ├── tests/
│   └── README.md
│
├── frontend/             ← INTERFACE WEB
│   ├── *.html
│   ├── *.css
│   ├── *.js
│   ├── img/
│   └── README.md
│
├── infrastructure/       ← DOCKER E DEPLOY
│   ├── docker-compose.yml
│   ├── mongo-init.js
│   ├── *.ps1
│   └── README.md
│
└── docs/                 ← DOCUMENTAÇÃO GERAL
    ├── README.md
    ├── README_WINDOWS.md
    └── SETUP_NOTEBOOKS.md
```

## 📋 Arquivos Movidos

### → backend/
- `client/` → `backend/client/`
- `tests/` → `backend/tests/`
- `requirements.txt` → `backend/requirements.txt`

### → frontend/
- `*.html` (5 arquivos)
- `*.css` (5 arquivos)
- `*.js` (3 arquivos: inicial.js, script.js, visualizar.js)
- `img/` (pasta completa)

### → infrastructure/
- `docker-compose.yml`
- `mongo-init.js`
- `setup-mongo.ps1`
- `deploy-remote.ps1`
- `verify-prereqs.ps1`
- `show-db.ps1`

### Permaneceram na raiz:
- `.venv/` (ambiente virtual Python)
- `README.md` (atualizado com nova estrutura)
- `README_WINDOWS.md` (guia completo)
- `README_NODES.md` (referência)
- `SETUP_NOTEBOOKS.md` (guia rápido)

## 📚 Documentação Criada

Cada pasta agora tem seu próprio README:

1. **`backend/README.md`**
   - Como usar os scripts Python
   - Configuração do ambiente
   - Estrutura de dados
   - Exemplos de uso

2. **`frontend/README.md`**
   - Descrição de cada página
   - Como executar localmente
   - Estrutura de arquivos
   - Guia de desenvolvimento

3. **`infrastructure/README.md`**
   - Scripts PowerShell explicados
   - Docker Compose local
   - Deploy remoto via WinRM
   - Troubleshooting

4. **`README.md` (raiz - atualizado)**
   - Visão geral do projeto
   - Quick start
   - Links para documentação específica
   - Tecnologias utilizadas

## 🔧 Ajustes nos Scripts

### Scripts Python atualizados

Os scripts `upload_sim.py` e `read_sim.py` foram atualizados para usar os IPs reais:

```python
# ANTES (localhost Docker Compose)
SEEDS = ["mongodb://localhost:27017", ...]

# DEPOIS (IPs dos notebooks)
REPLICA_URI = "mongodb://admin:admin123@10.76.9.53:27017,10.76.1.212:27017,10.76.10.131:27017,10.76.6.1:27017/uploadDB?replicaSet=rsUpload"
```

### Comandos atualizados

```powershell
# ANTES
python client/upload_sim.py --count 10

# DEPOIS
python backend/client/upload_sim.py --count 10
```

## ✨ Benefícios da Nova Estrutura

### 🎯 Separação Clara de Responsabilidades
- Backend: Python, MongoDB, lógica de negócios
- Frontend: UI, HTML/CSS/JS
- Infrastructure: Deploy, Docker, automação

### 📖 Documentação Modular
- Cada componente tem sua própria documentação
- Mais fácil para novos desenvolvedores
- READMEs específicos para cada contexto

### 🚀 Melhor Manutenibilidade
- Facilita encontrar arquivos
- Reduz conflitos em equipe
- Padrão de organização profissional

### 🔍 Navegação Intuitiva
```
Preciso editar a página de login? → frontend/login.html
Preciso ajustar o script de upload? → backend/client/upload_sim.py
Preciso fazer deploy? → infrastructure/
```

## 📝 Comandos Pós-Reorganização

### Executar scripts Python
```powershell
# Ativar ambiente virtual (sempre na raiz)
.\.venv\Scripts\Activate.ps1

# Executar scripts
python backend/client/upload_sim.py --count 10
python backend/client/read_sim.py --tag natureza
```

### Gerenciar infraestrutura
```powershell
# Docker Compose local
cd infrastructure
docker-compose up -d

# Deploy remoto
.\infrastructure\deploy-remote.ps1 -Hosts $hosts ...

# Verificar pré-requisitos
.\infrastructure\verify-prereqs.ps1
```

### Trabalhar com frontend
```powershell
# Abrir páginas
start frontend/login.html

# Ou servir com HTTP server
cd frontend
python -m http.server 8080
```

## 🎓 Para Novos Desenvolvedores

1. **Leia primeiro:** `README.md` na raiz
2. **Configure ambiente:** Siga `SETUP_NOTEBOOKS.md`
3. **Desenvolva backend:** Leia `backend/README.md`
4. **Desenvolva frontend:** Leia `frontend/README.md`
5. **Deploy:** Leia `infrastructure/README.md`

## ⚠️ Atenção

### Imports no Python
Se você tinha imports relativos, pode precisar ajustá-los:

```python
# ANTES
from client.upload_sim import *

# DEPOIS
from backend.client.upload_sim import *
```

### Paths nos scripts
Certifique-se de executar scripts a partir da raiz do projeto:

```powershell
# CORRETO (na raiz)
python backend/client/upload_sim.py

# ERRADO (dentro de backend/)
cd backend
python client/upload_sim.py  # pode não encontrar dependências
```

## ✅ Checklist de Verificação

- [x] Backend separado com README
- [x] Frontend separado com README
- [x] Infrastructure separada com README
- [x] README principal atualizado
- [x] Scripts Python funcionando
- [x] Ambiente virtual preservado
- [x] Documentação completa

## 🚀 Próximos Passos Sugeridos

1. [ ] Criar API REST para conectar frontend e backend
2. [ ] Adicionar testes automatizados no backend
3. [ ] Implementar CI/CD
4. [ ] Dockerizar o backend (não apenas o MongoDB)
5. [ ] Melhorar frontend com framework (React, Vue, etc.)

---

**Data da reorganização:** 28/10/2025  
**Estrutura aprovada:** ✅  
**Documentação completa:** ✅  
**Scripts funcionais:** ✅
