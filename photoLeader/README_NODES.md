# Instruções para os notebooks (nós) — Preparação para o PhotoLeader Replica Set

Este documento destina-se às máquinas que serão usadas como nós do cluster MongoDB (os 5 notebooks da rede).
Coloque este arquivo no GitHub do projeto para que cada membro da equipe siga as instruções.

IMPORTANTE: execute os comandos abaixo no PowerShell com privilégios administrativos.

---

## 1) Objetivo

Preparar cada notebook para receber o container MongoDB (nome `mongo1`..`mongo5`) e permitir que a máquina central execute o deploy remoto via PowerShell Remoting (WinRM). Essas instruções cobrem:
- instalação/checagem do Docker Desktop;
- criação da pasta de dados (`C:\mongo\data`);
- habilitação do WinRM (PowerShell Remoting);
- liberação de portas necessárias (27017 para MongoDB; 5985/5986 para WinRM);
- execução local do script `setup-mongo.ps1` (caso prefira executar manualmente);
- como verificar o status do container e do Replica Set.

---

## 2) Pré-requisitos (instalar se não estiver presente)

Requisitos mínimos em cada notebook:
- Windows 10/11 (ou Windows Server compatível).
- Docker Desktop (com WSL2/Hyper-V habilitado). Baixe em: https://www.docker.com/get-started
- PowerShell (Windows PowerShell 5.1 já presente; PowerShell 7 opcional).
- Conta local com permissões administrativas (para instalar, habilitar WinRM e executar Docker).
- Conectividade na mesma rede local (mesma subnet) com os demais notebooks.

---

## 3) Passos de preparação (execute como Administrador)

1) Atualize o Docker Desktop e verifique que o serviço está rodando. Abra o Docker Desktop e confirme que o `Engine` está em execução.

2) Crie a pasta de dados usada pelo MongoDB:

```powershell
mkdir C:\mongo\data -Force
```

3) Habilite o PowerShell Remoting (WinRM) para permitir que a máquina central execute comandos remotamente:

```powershell
# Habilita PSRemoting
Enable-PSRemoting -Force

# Permite receber conexões WinRM HTTP (5985)
if (-not (Get-NetFirewallRule -DisplayName 'Windows Remote Management (HTTP-In)' -ErrorAction SilentlyContinue)) {
    Enable-NetFirewallRule -DisplayName 'Windows Remote Management (HTTP-In)'
}
```

Observação: por padrão `Enable-PSRemoting` cria regras de firewall para WinRM; se tiver políticas corporativas, peça ao administrador de rede para permitir a porta.

4) (Opcional) Se sua rede NÃO estiver em domínio, confirme que o host que fará o deploy adicionou este notebook em `TrustedHosts` (feito na máquina central). Você não precisa alterar TrustedHosts no notebook alvo.

5) Garanta que a porta 27017 esteja liberada localmente para o Docker (normalmente o Docker mapeia portas do container; se houver firewall estrito, libere a porta):

```powershell
# Checar porta local (ainda sem container em execução, apenas para validar comando)
Test-NetConnection -ComputerName localhost -Port 27017
```

6) Verifique se o Docker responde:

```powershell
docker version --format '{{.Server.Version}}'
```

Se o comando falhar, abra o Docker Desktop e verifique logs.

---

## 4) Recebendo o deploy remoto (opção recomendada: central executa `deploy-remote.ps1`)

Se a equipe usar o script central `deploy-remote.ps1`, você só precisa:
- ter WinRM habilitado (etapa 3);
- garantir que seu usuário administrador exista e aceite conexões remotas;
- deixar a máquina ligada e conectada à rede no momento do deploy.

O responsável central executará o deploy e a criação do container. Você receberá o container `mongo{N}` criado automaticamente (nome definido pelo NodeIndex).

---

## 5) Execução manual (se preferir configurar localmente)

Se quiser rodar o `setup-mongo.ps1` localmente (por exemplo, se não usar deploy remoto), baixe o arquivo do repositório e execute no PowerShell como Administrador. Exemplos:

- Notebook que será o `mongo1` (NodeIndex 1):

```powershell
# No notebook 1
.\setup-mongo.ps1 -NodeIndex 1 -MemberIPs '192.168.0.11,192.168.0.12,192.168.0.13,192.168.0.14,192.168.0.15' -CreateAdmin
```

- Notebook que será o `mongo2` (NodeIndex 2):

```powershell
# No notebook 2
.\setup-mongo.ps1 -NodeIndex 2 -MemberIPs '192.168.0.11,192.168.0.12,192.168.0.13,192.168.0.14,192.168.0.15'
```

Repita em cada notebook definindo `-NodeIndex` corretamente (1..5). O parâmetro `-CreateAdmin` é recomendado apenas no NodeIndex 1 para criar o usuário `admin`.

O script fará:
- criar o diretório `C:\mongo\data` (se não existir);
- executar `docker run` com `mongod --replSet rsUpload --bind_ip_all`;
- no NodeIndex 1 ele gerará `init-replica.js` e chamará `mongosh` para `rs.initiate()`.

---

## 6) Verificando o container e o Replica Set

No notebook em que o container foi criado (ou em qualquer máquina que tenha mongosh/portas reachables):

```powershell
# Listar containers
docker ps

# Ver logs do mongod
docker logs mongo1

# Verificar status do Replica Set (execute dentro do container que tenha mongod)
docker exec -it mongo1 mongosh --eval "rs.status()"
```

Procure `stateStr: "PRIMARY"` em um dos membros e `SECONDARY` nos demais.

---

## 7) Se algo falhar — passos rápidos de troubleshooting

- Docker não inicia: abra Docker Desktop, verifique se WSL2/Hyper-V está habilitado e se os recursos de virtualização estão ativos no BIOS.
- WinRM falhou: execute `Enable-PSRemoting -Force` e reinicie o serviço WinRM:

```powershell
Restart-Service WinRM
```

- Firewall bloqueando: peça ao administrador para liberar 5985 (WinRM) e 27017 (MongoDB) na rede local ou adicione regras locais via PowerShell.

- Permissões: confirme que a conta usada pelo deploy tem privilégios administrativos (para rodar Docker).

---

## 8) Segurança e boas práticas

- Não habilite `AllowUnencrypted` ou `Basic` authentication em ambientes de produção sem HTTPS/Certificado.
- Prefira WinRM sobre HTTPS (5986) em redes não confiáveis.
- Use senhas fortes para o usuário admin caso crie via `-CreateAdmin`.
- Ao finalizar a demo, pare e remova containers se desejar:

```powershell
docker stop mongo1; docker rm mongo1
```

---

## 9) Contato e coordenação

Combine com a equipe:
- IPs que cada notebook terá (definir mapeamento nodeIndex ↔ IP);
- horário do deploy;
- usuário administrador que será usado para o deploy remoto.

---

Se quiser, eu posso adicionar este arquivo ao repositório (fazer commit) e criar um trecho no `README.md` principal apontando para ele. Deseja que eu faça o commit automático aqui no workspace (posso criar o commit message e listar os arquivos modificados)?
