document.addEventListener("DOMContentLoaded", async () => {
  const botaoAdicionar = document.getElementById("botaoAdicionar");
  const modalUpload = document.getElementById("modalUpload");
  const fecharModal = document.getElementById("fecharModal");
  const formUpload = document.getElementById("formUpload");
  const galeria = document.getElementById("galeria");
  const inputArquivo = document.getElementById("fotoAdicionar");
  const botaoSair = document.getElementById("botaoSair");

  // Carregar fotos da API
  await carregarFotos();

  //abrir modal
  botaoAdicionar.addEventListener("click", () => {
    modalUpload.style.display = "flex";
  });

  //fechar modal
  fecharModal.addEventListener("click", () => {
    modalUpload.style.display = "none";
    formUpload.reset();
  });

  //sair da conta
  botaoSair.addEventListener("click", () => {
    alert("Logout realizado!");
    window.location.href = "login.html";
  });

  //enviar formulário
  formUpload.addEventListener("submit", async (e) => {
    e.preventDefault();
    const arquivo = inputArquivo.files[0];
    const descricao = document.getElementById("descricao").value.trim();

    if (!arquivo) {
      alert("Selecione um arquivo antes de salvar!");
      return;
    }

    try {
      // Criar FormData para enviar arquivo + metadados
      const formData = new FormData();
      formData.append('file', arquivo);
      formData.append('user', localStorage.getItem("usuarioLogado") || "usuario_padrao");
      formData.append('description', descricao || "Sem descrição");
      
      // Adicionar tags se houver descrição
      if (descricao) {
        const tags = descricao.split(" ").filter(t => t.length > 2);
        formData.append('tags', tags.join(','));
      }

      // Upload usando fetch diretamente (não usar PhotoLeaderAPI pois precisa de FormData)
      const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:5000/api`;
      const response = await fetch(`${API_BASE_URL}/photos`, {
        method: 'POST',
        body: formData  // Não definir Content-Type, o navegador faz automaticamente
      });

      const resultado = await response.json();
      
      if (!resultado.success) {
        throw new Error(resultado.error || 'Erro desconhecido');
      }

      // Adicionar à galeria
      criarItemGaleria(resultado.data);
      
      alert("Foto enviada com sucesso!");
      
      //fechar o modal
      modalUpload.style.display = "none";
      formUpload.reset();
    } catch (error) {
      console.error("Erro ao enviar foto:", error);
      alert("Erro ao enviar foto: " + error.message);
    }
  });

  // Carregar fotos da API
  async function carregarFotos() {
    try {
      const fotos = await PhotoLeaderAPI.getPhotos();
      galeria.innerHTML = ""; // Limpar galeria
      fotos.forEach(foto => criarItemGaleria(foto));
    } catch (error) {
      console.error("Erro ao carregar fotos:", error);
      alert("Erro ao carregar fotos. Verifique se a API está rodando.");
    }
  }

  //criar aquele formato de galeria a cada inserção
  function criarItemGaleria(foto) {
    const item = document.createElement("div");
    item.classList.add("item-galeria");

    // Criar imagem usando a URL do GridFS
    const img = document.createElement("img");
    const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:5000`;
    img.src = foto.photo_url ? `${API_BASE_URL}${foto.photo_url}` : "img/iconPhotoLeader.png";
    img.alt = foto.description || foto.filename;
    img.style.width = "100%";
    img.style.height = "200px";
    img.style.objectFit = "cover";
    item.appendChild(img);

    const legenda = document.createElement("p");
    legenda.textContent = foto.description || foto.filename;
    item.appendChild(legenda);

    //qnd clicar na foto, vai para página de visualização
    item.addEventListener("click", () => {
      // Salvar ID da foto selecionada
      localStorage.setItem("fotoSelecionadaId", foto._id);
      window.location.href = "telaVisualizar.html";
    });

    galeria.prepend(item);
  }
});
