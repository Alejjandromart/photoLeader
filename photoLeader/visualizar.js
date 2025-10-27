document.addEventListener("DOMContentLoaded", () => {
  const botaoFechar = document.getElementById("botaoFechar");
  const dataMidia = document.getElementById("dataMidia");
  const anterior = document.getElementById("anterior");
  const proximo = document.getElementById("proximo");
  const excluir = document.getElementById("excluir");
  const midiaContainer = document.querySelector(".midia-container");

  //qnd vc voltar pra tela inicial, meio q vai ficar salvo na telaVisualizar.html (é a persistencia)
  const midias = JSON.parse(localStorage.getItem("todasMidias")) || [];
  const midiaSelecionada = JSON.parse(localStorage.getItem("midiaSelecionada"));

  let indiceAtual = 0;
  if (midiaSelecionada) {
    indiceAtual = midias.findIndex(m => m.url === midiaSelecionada.url);
    if (indiceAtual === -1) {
      midias.push(midiaSelecionada);
      indiceAtual = midias.length - 1;
    }
  }

  //mostrar arquivos
  function mostrarMidia(indice) {
    const midia = midias[indice];
    if (!midia) return;

    midiaContainer.innerHTML = "";

    if (midia.tipo.startsWith("image/")) {
      const img = document.createElement("img");
      img.src = midia.url;
      img.alt = midia.descricao || "Imagem";
      midiaContainer.appendChild(img);
    } else if (midia.tipo.startsWith("video/")) {
      const video = document.createElement("video");
      video.src = midia.url;
      video.controls = true;
      video.style.maxHeight = "400px";
      midiaContainer.appendChild(video);
    }

    dataMidia.textContent = midia.data || "—";
  }

  mostrarMidia(indiceAtual);

  //navegar pelos arquivos
  anterior.addEventListener("click", () => {
    indiceAtual = (indiceAtual - 1 + midias.length) % midias.length;
    mostrarMidia(indiceAtual);
  });

  proximo.addEventListener("click", () => {
    indiceAtual = (indiceAtual + 1) % midias.length;
    mostrarMidia(indiceAtual);
  });

  //apagar arquivo
  excluir.addEventListener("click", () => {
    if (confirm("Deseja realmente excluir esta mídia?")) {
      midias.splice(indiceAtual, 1);
      localStorage.setItem("todasMidias", JSON.stringify(midias));

      if (midias.length === 0) {
        alert("Nenhuma mídia restante. Voltando à tela inicial.");
        window.location.href = "inicial.html";
        return;
      }

      indiceAtual = Math.max(0, indiceAtual - 1);
      mostrarMidia(indiceAtual);
    }
  });

  //voltar pra tela incial
  botaoFechar.addEventListener("click", () => {
    window.location.href = "inicial.html";
  });
});