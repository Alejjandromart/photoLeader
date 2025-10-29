document.addEventListener("DOMContentLoaded", async () => {
  const botaoFechar = document.getElementById("botaoFechar");
  const dataMidia = document.getElementById("dataMidia");
  const anterior = document.getElementById("anterior");
  const proximo = document.getElementById("proximo");
  const excluir = document.getElementById("excluir");
  const midiaContainer = document.querySelector(".midia-container");

  // Carregar todas as fotos da API
  let fotos = [];
  let indiceAtual = 0;

  try {
    fotos = await PhotoLeaderAPI.getPhotos();
    
    // Se uma foto específica foi selecionada, encontrar seu índice
    const fotoSelecionadaId = localStorage.getItem("fotoSelecionadaId");
    if (fotoSelecionadaId) {
      const indice = fotos.findIndex(f => f._id === fotoSelecionadaId);
      if (indice !== -1) {
        indiceAtual = indice;
      }
      localStorage.removeItem("fotoSelecionadaId"); // Limpar após usar
    }

    if (fotos.length === 0) {
      alert("Nenhuma foto encontrada. Voltando à tela inicial.");
      window.location.href = "telaInicial.html";
      return;
    }

    mostrarFoto(indiceAtual);
  } catch (error) {
    console.error("Erro ao carregar fotos:", error);
    alert("Erro ao carregar fotos. Verifique se a API está rodando.");
    window.location.href = "telaInicial.html";
    return;
  }

  //mostrar foto atual
  function mostrarFoto(indice) {
    const foto = fotos[indice];
    if (!foto) return;

    midiaContainer.innerHTML = "";

    // Criar imagem usando a URL da API
    const img = document.createElement("img");
    const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:5000`;
    img.src = `${API_BASE_URL}/api/photos/${foto._id}/file`;
    img.alt = foto.description || foto.filename;
    img.style.maxWidth = "100%";
    img.style.maxHeight = "500px";
    img.style.objectFit = "contain";
    midiaContainer.appendChild(img);

    // Formatar data
    const dataUpload = new Date(foto.upload_date);
    dataMidia.textContent = dataUpload.toLocaleDateString('pt-BR');
  }

  //navegar para foto anterior
  anterior.addEventListener("click", () => {
    indiceAtual = (indiceAtual - 1 + fotos.length) % fotos.length;
    mostrarFoto(indiceAtual);
  });

  //navegar para próxima foto
  proximo.addEventListener("click", () => {
    indiceAtual = (indiceAtual + 1) % fotos.length;
    mostrarFoto(indiceAtual);
  });

  //apagar foto usando a API
  excluir.addEventListener("click", async () => {
    if (confirm("Deseja realmente excluir esta foto?")) {
      try {
        const fotoId = fotos[indiceAtual]._id;
        await PhotoLeaderAPI.deletePhoto(fotoId);
        
        // Remover da lista local
        fotos.splice(indiceAtual, 1);

        if (fotos.length === 0) {
          alert("Nenhuma foto restante. Voltando à tela inicial.");
          window.location.href = "telaInicial.html";
          return;
        }

        // Ajustar índice e mostrar próxima foto
        indiceAtual = Math.min(indiceAtual, fotos.length - 1);
        mostrarFoto(indiceAtual);
        
        alert("Foto excluída com sucesso!");
      } catch (error) {
        console.error("Erro ao excluir foto:", error);
        alert("Erro ao excluir foto: " + error.message);
      }
    }
  });

  //voltar para tela inicial
  botaoFechar.addEventListener("click", () => {
    window.location.href = "telaInicial.html";
  });
});
