const botaoCadastro = document.getElementById("botaoCadastro");
if (botaoCadastro) {
  botaoCadastro.addEventListener("click", () => {
    window.location.href = "cadastro.html";
  });
}

const botaoLogin = document.getElementById("botaoLogin");
if (botaoLogin) {
  botaoLogin.addEventListener("click", () => {
    window.location.href = "login.html";
  });
}

const esqueceuSenha = document.getElementById("esqueceuSenha");
if (esqueceuSenha) {
  esqueceuSenha.addEventListener("click", () => {
    window.location.href = "esqueceu.html";
  });
}

const voltarLogin = document.getElementById("voltarLogin");
if (voltarLogin) {
  voltarLogin.addEventListener("click", () => {
    window.location.href = "login.html";
  });
}

//login
const formLogin = document.getElementById("formLogin");
if (formLogin) {
  formLogin.addEventListener("submit", (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const senha = document.getElementById("senha").value;

    if (email && senha) {
      //pra ligar o bd 
      window.location.href = "telainicial.html";
    } else {
      alert("Preencha todos os campos.");
    }
  });
}

//cadastro
const formCadastro = document.getElementById("formCadastro");
if (formCadastro) {
  formCadastro.addEventListener("submit", (e) => {
    e.preventDefault();
    const nome = document.getElementById("nome").value;
    const email = document.getElementById("email").value;
    const senha = document.getElementById("senha").value;

    if (nome && email && senha) {
      alert("Cadastro realizado com sucesso!");
      window.location.href = "login.html";
    } else {
      alert("Preencha todos os campos antes de continuar.");
    }
  });
}

//esqueceu senha
const formEsqueceu = document.getElementById("formEsqueceu");
if (formEsqueceu) {
  formEsqueceu.addEventListener("submit", (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;

    if (email) {
      alert("Um link de recuperação foi enviado para o seu e-mail.");
      window.location.href = "login.html";
    } else {
      alert("Por favor, insira seu e-mail ou usuário.");
    }
  });
}