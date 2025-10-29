# 🚀 Como Usar o PhotoLeader

## Iniciar o Sistema

### 1. Iniciar a API (Backend)

```powershell
cd "c:\Users\silva\OneDrive\Área de Trabalho\singleleader\photoLeader\photoLeader\backend"
& "C:/Program Files/Python313/python3.13t.exe" api.py
```

A API vai iniciar em: **http://localhost:5000**

### 2. Abrir a Interface Web (Frontend)

```powershell
Invoke-Item "c:\Users\silva\OneDrive\Área de Trabalho\singleleader\photoLeader\photoLeader\frontend\telaInicial.html"
```

Ou simplesmente abra o arquivo `telaInicial.html` no navegador.

## Fluxo de Uso

### Tela Inicial (`telaInicial.html`)
- **Ver Galeria**: Todas as fotos do banco de dados são carregadas automaticamente
- **Adicionar Foto**: Clique em "Adicionar Foto ou Vídeo"
  - Selecione um arquivo
  - Adicione uma descrição (opcional)
  - Clique em "Salvar"
- **Visualizar Foto**: Clique em qualquer foto da galeria

### Tela de Visualização (`telaVisualizar.html`)
- **Navegar**: Use os botões "Anterior" e "Próximo"
- **Excluir**: Clique no botão de lixeira para deletar a foto atual
- **Voltar**: Clique no "X" para voltar à tela inicial

## Integração API + Frontend

### O que mudou?

**ANTES** (localStorage):
- Fotos salvas apenas no navegador (localStorage)
- Dados perdidos ao limpar cache
- Limite de ~5MB por arquivo

**AGORA** (MongoDB API):
- Fotos salvas no MongoDB Replica Set
- Persistência garantida em 4+ servidores
- Sem limite prático de tamanho
- Dados acessíveis de qualquer cliente

### Arquivos Integrados

1. **frontend/inicial.js**
   - `PhotoLeaderAPI.getPhotos()` - Carrega fotos da API
   - `PhotoLeaderAPI.uploadPhoto()` - Faz upload para API

2. **frontend/visualizar.js**
   - `PhotoLeaderAPI.getPhotos()` - Carrega fotos para navegação
   - `PhotoLeaderAPI.deletePhoto()` - Deleta foto da API

3. **frontend/api-client.js**
   - Biblioteca JavaScript com todas as funções da API
   - Base URL: `http://localhost:5000`

## Estrutura do Projeto

```
photoLeader/
├── backend/
│   ├── api.py              # Flask REST API (9 endpoints)
│   ├── client/
│   │   ├── upload_sim.py   # Script Python para upload
│   │   └── read_sim.py     # Script Python para leitura
│   └── requirements.txt
│
├── frontend/
│   ├── telaInicial.html    # Galeria principal
│   ├── telaVisualizar.html # Visualizador de fotos
│   ├── inicial.js          # Lógica da tela inicial (integrado com API)
│   ├── visualizar.js       # Lógica de visualização (integrado com API)
│   ├── api-client.js       # Cliente JavaScript da API
│   └── [outros arquivos CSS/HTML]
│
└── infrastructure/
    └── [docker configs]
```

## Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/health` | Status da API |
| GET | `/api/photos` | Lista todas as fotos |
| POST | `/api/photos` | Upload de foto |
| GET | `/api/photos/<id>` | Busca foto por ID |
| DELETE | `/api/photos/<id>` | Remove foto |
| GET | `/api/photos/user/<usuario>` | Fotos de um usuário |
| GET | `/api/photos/tag/<tag>` | Fotos por tag |
| GET | `/api/search?q=<texto>` | Busca por texto |
| GET | `/api/stats` | Estatísticas do banco |

## Troubleshooting

### API não inicia
```powershell
# Verificar se pymongo/flask estão instalados
& "C:/Program Files/Python313/python3.13t.exe" -m pip list | Select-String "pymongo|flask"

# Reinstalar dependências
& "C:/Program Files/Python313/python3.13t.exe" -m pip install pymongo flask flask-cors
```

### Frontend não carrega fotos
1. Verifique se a API está rodando: http://localhost:5000/api/health
2. Abra o Console do navegador (F12) para ver erros
3. Verifique se `api-client.js` está carregado

### MongoDB não conecta
1. Verifique se os containers Docker estão rodando:
   ```powershell
   docker ps
   ```
2. Verifique a conexão:
   ```powershell
   docker exec mongo1 mongosh --eval "rs.status()" --quiet
   ```

## Próximos Passos

- [ ] Adicionar autenticação (login/cadastro funcionais)
- [ ] Implementar tags visuais
- [ ] Adicionar suporte a vídeos
- [ ] Criar página de busca avançada
- [ ] Adicionar 5º nó ao Replica Set (10.76.1.612)
