document.addEventListener("DOMContentLoaded", () => {
  const botaoAdicionar = document.getElementById("botaoAdicionar");
  const modalUpload = document.getElementById("modalUpload");
  const fecharModal = document.getElementById("fecharModal");
  const formUpload = document.getElementById("formUpload");
  const galeria = document.getElementById("galeria");
  const inputArquivo = document.getElementById("fotoAdicionar");
  const botaoSair = document.getElementById("botaoSair");

  //mostrar os arquivos salvos
  const todasMidias = JSON.parse(localStorage.getItem("todasMidias")) || [];
  todasMidias.forEach((midia) => criarItemGaleria(midia));

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

    //converte o arquivo pra base64 para persistir
    const base64 = await fileToBase64(arquivo);

    const midia = {
      url: base64,
      tipo: arquivo.type,
      descricao,
      data: new Date().toLocaleDateString()
    };

    //salvar arq no localStorage
    const todasMidias = JSON.parse(localStorage.getItem("todasMidias")) || [];
    todasMidias.unshift(midia);
    localStorage.setItem("todasMidias", JSON.stringify(todasMidias));

    criarItemGaleria(midia);

    //fechar o modal (caixa de adicionar arquivos)
    modalUpload.style.display = "none";
    formUpload.reset();
  });

  //o base64 é só pra manter a persistencia dos arquivos, mas ele não suporta vídeos acima de 5mb, então é necessário ter um bd
  function fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
    });
  }

  //criar aquele formato de galeria a cada inserção
  function criarItemGaleria(midia) {
    const item = document.createElement("div");
    item.classList.add("item-galeria");

    if (midia.tipo.startsWith("image/")) {
      const img = document.createElement("img");
      img.src = midia.url;
      img.alt = midia.descricao;
      item.appendChild(img);
    } else if (midia.tipo.startsWith("video/")) {
      const video = document.createElement("video");
      video.src = midia.url;
      video.controls = true;
      item.appendChild(video);
    }

    const legenda = document.createElement("p");
    legenda.textContent = midia.descricao;
    item.appendChild(legenda);

    //qnd clicar na foto ou vídeo, vc vai ser direcionado pra outra página
    item.addEventListener("click", () => {
      localStorage.setItem("midiaSelecionada", JSON.stringify(midia));
      window.location.href = "telaVisualizar.html";
    });

    galeria.prepend(item);
  }
});
