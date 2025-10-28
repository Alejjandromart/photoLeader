# Frontend - PhotoLeader

Esta pasta contém todos os arquivos do frontend da aplicação PhotoLeader (HTML, CSS, JavaScript).

## 📁 Estrutura

```
frontend/
├── cadastro.html              # Página de cadastro de usuário
├── esqueceu.html              # Página de recuperação de senha
├── login.html                 # Página de login
├── telaInicial.html           # Tela principal da aplicação
├── telaVisualizar.html        # Tela de visualização de fotos
├── estiloCad.css              # Estilos da página de cadastro
├── estiloEsqueceu.css         # Estilos da página de recuperação
├── estiloLogin.css            # Estilos da página de login
├── estiloTelaInicial.css      # Estilos da tela inicial
├── estiloVisualizacao.css     # Estilos da tela de visualização
├── inicial.js                 # Scripts da tela inicial
├── script.js                  # Scripts gerais
├── visualizar.js              # Scripts da visualização de fotos
├── img/                       # Imagens e assets
└── README.md                  # Este arquivo
```

## 🚀 Como Executar

### Opção 1: Abrir diretamente no navegador

Navegue até a pasta frontend e abra qualquer arquivo HTML:

```powershell
# Abrir a página de login
start frontend/login.html

# Ou usando o navegador específico
chrome frontend/login.html
firefox frontend/login.html
```

### Opção 2: Servidor HTTP local (recomendado)

Para evitar problemas com CORS e módulos:

```powershell
# Usando Python (se disponível)
cd frontend
python -m http.server 8080

# Acesse no navegador: http://localhost:8080/login.html
```

Ou usando Node.js:

```powershell
# Instalar http-server globalmente (uma vez)
npm install -g http-server

# Executar na pasta frontend
cd frontend
http-server -p 8080

# Acesse: http://localhost:8080/login.html
```

## 📄 Páginas Disponíveis

### login.html
- Tela de autenticação do usuário
- Formulário de login
- Link para cadastro e recuperação de senha

### cadastro.html
- Registro de novos usuários
- Validação de campos
- Estilos customizados (estiloCad.css)

### esqueceu.html
- Recuperação de senha
- Interface para redefinição

### telaInicial.html
- Dashboard principal do usuário
- Navegação entre funcionalidades
- Scripts: inicial.js

### telaVisualizar.html
- Galeria de fotos
- Visualização de uploads
- Scripts: visualizar.js

## 🎨 Estilos (CSS)

Cada página tem seu arquivo CSS correspondente:

- `estiloLogin.css` → `login.html`
- `estiloCad.css` → `cadastro.html`
- `estiloEsqueceu.css` → `esqueceu.html`
- `estiloTelaInicial.css` → `telaInicial.html`
- `estiloVisualizacao.css` → `telaVisualizar.html`

## 📜 Scripts JavaScript

### script.js
Funções gerais e utilitárias compartilhadas entre as páginas.

### inicial.js
Lógica específica da tela inicial:
- Carregamento de dados do usuário
- Navegação entre seções
- Eventos de interface

### visualizar.js
Lógica da galeria de fotos:
- Carregamento de imagens
- Filtros e busca
- Visualização em modal

## 🔗 Integração com Backend

Para conectar o frontend com o backend MongoDB:

1. Os scripts JavaScript devem fazer requisições HTTP para uma API
2. Considere criar uma API REST usando Flask ou FastAPI
3. Configure CORS adequadamente

Exemplo de integração:

```javascript
// Em visualizar.js - exemplo de busca de fotos
async function loadPhotos() {
    try {
        const response = await fetch('http://localhost:5000/api/photos');
        const photos = await response.json();
        displayPhotos(photos);
    } catch (error) {
        console.error('Erro ao carregar fotos:', error);
    }
}
```

## 🛠️ Desenvolvimento

### Modificar estilos
Edite os arquivos `.css` correspondentes à página que deseja alterar.

### Adicionar nova página
1. Crie um novo arquivo `.html` na pasta `frontend/`
2. Crie o CSS correspondente (ex: `estiloNovaPagina.css`)
3. Se necessário, crie um arquivo JS (ex: `novaPagina.js`)
4. Atualize os links de navegação nas outras páginas

### Estrutura HTML recomendada
```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Título da Página - PhotoLeader</title>
    <link rel="stylesheet" href="estiloNomeDaPagina.css">
</head>
<body>
    <!-- Conteúdo -->
    <script src="nomeDaPagina.js"></script>
</body>
</html>
```

## 📱 Responsividade

Os arquivos CSS devem incluir media queries para responsividade:

```css
/* Desktop */
@media (min-width: 1024px) {
    /* Estilos para desktop */
}

/* Tablet */
@media (min-width: 768px) and (max-width: 1023px) {
    /* Estilos para tablet */
}

/* Mobile */
@media (max-width: 767px) {
    /* Estilos para mobile */
}
```

## 🖼️ Assets (Imagens)

Todas as imagens estão na pasta `img/`:
- Logos
- Ícones
- Imagens de background
- Placeholders

## 🐛 Troubleshooting

### Estilos não carregam
- Verifique o caminho relativo no `<link>` do HTML
- Certifique-se de estar executando de um servidor HTTP

### JavaScript não funciona
- Abra o Console do navegador (F12) para ver erros
- Verifique se o script está sendo carregado antes de ser usado

### CORS errors
- Use um servidor HTTP local ao invés de abrir direto no navegador
- Configure o backend para aceitar requisições do frontend

## 📌 Próximos Passos

- [ ] Criar API REST no backend para conectar com frontend
- [ ] Implementar autenticação JWT
- [ ] Adicionar loading states e feedback visual
- [ ] Implementar upload de arquivos reais (não apenas metadados)
- [ ] Melhorar responsividade mobile
