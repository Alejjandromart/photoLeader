# Demo MongoDB Replica Set (5 nós) — PhotoLeader

Este repositório contém arquivos para demonstrar um Replica Set MongoDB com 5 nós
(1 Primary + 4 Secondaries) para um sistema de upload de mídia onde apenas os
metadados são salvos no MongoDB.

Arquivos adicionados:

- `docker-compose.yml` — orquestra 5 instâncias `mongod` e um serviço de setup para iniciar o replica set.
- `mongo-init.js` — script que chama `rs.initiate()` com a configuração dos 5 membros.
- `client/upload_sim.py` — script Python que simula uploads (inserção de metadados) com writeConcern majority.
- `client/read_sim.py` — script Python que realiza leituras preferindo Secondaries (readPreference=secondaryPreferred).
- `requirements.txt` — dependências Python (pymongo).
- `README_WINDOWS.md` — guia completo para instalar e rodar o cluster em 5 notebooks Windows (PowerShell + Docker Desktop).
- `setup-mongo.ps1` — script PowerShell para automatizar criação de container MongoDB e inicialização do Replica Set (Windows).

Como executar (Windows PowerShell):

1) Levantar o cluster:

```powershell
# a partir da pasta onde está o docker-compose.yml
docker-compose up -d
```

O serviço `mongo-setup` tentará rodar `mongo-init.js` e iniciar o replica set. Aguarde alguns segundos e verifique os containers:

```powershell
docker ps
```

2) Instalar dependências Python:

```powershell
python -m pip install -r requirements.txt
```

3) Simular uploads:

```powershell
python client\upload_sim.py --count 10
```

Este script insere documentos com writeConcern majority para garantir que a escrita foi registrada pelo quórum.

4) Ler a galeria a partir dos Secondaries:

```powershell
python client\read_sim.py --tag natureza
```

5) Simular falha do Primary (em outra janela PowerShell):

Primeiro identifique o Primary (em um container execute `rs.status()` ou verifique logs). Para simular:

```powershell
# pare o container mongo1 (supondo que seja o Primary)
docker stop mongo1
```

Observe que o Replica Set fará uma nova eleição. Você pode continuar inserindo (o cliente Python irá apontar para o novo Primary depois da eleição) e medir o tempo de failover.

Observações:

- Os scripts Python usam `localhost:27017..27021` como seeds — execute-os localmente na máquina que está rodando os containers.
- Em ambientes diferentes (por exemplo, deploy em VMs separadas), ajuste os hosts/ports na `docker-compose.yml` e nos scripts.

Próximos passos sugeridos:

- Adicionar testes automáticos (latência de failover, latência de escrita/ leitura de segundo nível).
- Instrumentar logs para medir tempos de failover em diferentes condições.
- Integrar com um storage de objetos (S3) para arquivos binários; MongoDB fica apenas com metadados.

Instruções para os notebooks (nós) — deploy em múltiplas máquinas
-----------------------------------------------------------------------

Se você vai executar o cluster distribuído em 5 notebooks (cada um como um nó do Replica Set), siga o guia específico para os nós disponível em `README_NODES.md`. Esse arquivo contém passo-a-passo para cada notebook:

- pré-requisitos (Docker Desktop, PowerShell/WinRM, permissões administrativas);
- criação da pasta de dados (`C:\\mongo\\data`);
- habilitação do PowerShell Remoting (`Enable-PSRemoting -Force`) e instruções sobre TrustedHosts;
- opção de executar `setup-mongo.ps1` localmente em cada nó ou receber o deploy remoto via `deploy-remote.ps1`;
- checagens de verificação e troubleshooting básicos.

Link rápido para o guia dos nós: `README_NODES.md` (recomendo adicioná-lo ao GitHub junto com este repositório).

Setup rápido para cada notebook (copiar para o GitHub)
-------------------------------------------------------

Se você for um dos donos dos notebooks que participarão do cluster, siga este resumo rápido antes do deploy remoto:

1) Abra PowerShell como Administrador.
2) Instale e inicie o Docker Desktop; confirme com:

```powershell
docker version --format '{{.Server.Version}}'
```

3) Crie a pasta de dados local que será montada pelo container:

```powershell
mkdir C:\mongo\data -Force
```

4) Habilite PowerShell Remoting (WinRM) para permitir deploy remoto:

```powershell
Enable-PSRemoting -Force
# (opcional na máquina central) Set-Item WSMan:\localhost\Client\TrustedHosts -Value "<lista-de-hosts>" -Concatenate
```

5) Abra as portas necessárias no firewall se aplicável: 5985 (WinRM HTTP) e 27017 (MongoDB).
6) Aguarde o administrador rodar o deploy remoto ou execute localmente `setup-mongo.ps1` com o NodeIndex correto:

```powershell
# No notebook 1 (nodeIndex 1)
.\setup-mongo.ps1 -NodeIndex 1 -MemberIPs '192.168.0.11,192.168.0.12,192.168.0.13,192.168.0.14,192.168.0.15' -CreateAdmin

# Em outros notebooks (nodeIndex 2..5)
.\setup-mongo.ps1 -NodeIndex 2 -MemberIPs '192.168.0.11,192.168.0.12,192.168.0.13,192.168.0.14,192.168.0.15'
```

7) Verifique que o Replica Set está ativo (no node 1):

```powershell
docker exec -it mongo1 mongosh --eval "rs.status()"
```

8) Confirme que a base `uploadDB` e a collection `files` existem:

```powershell
docker exec -it mongo1 mongosh --eval "use uploadDB; show collections; db.files.getIndexes();"
```

Observação: instruções completas e troubleshooting estão em `README_NODES.md`.
