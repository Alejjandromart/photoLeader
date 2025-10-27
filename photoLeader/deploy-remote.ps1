<#
deploy-remote.ps1

Copia e executa localmente o script 'setup-mongo.ps1' em múltiplos notebooks/hosts via PowerShell Remoting (WinRM).

Pré-requisitos (em cada target):
- WinRM habilitado (Enable-PSRemoting -Force)
- Usuário com permissão administrativa
- Firewall permitindo WinRM (HTTP 5985 ou HTTPS 5986) ou hosts adicionados em TrustedHosts

Uso exemplo:
.
$hosts = '192.168.0.11','192.168.0.12','192.168.0.13','192.168.0.14','192.168.0.15'
.
PS> .\deploy-remote.ps1 -Hosts $hosts -LocalSetupScript .\setup-mongo.ps1 -ReplSetName rsUpload -CreateAdmin

O script fará, para cada host:
- criar uma sessão PS Remoting
- copiar `setup-mongo.ps1` para `C:\Temp\setup-mongo.ps1` no host
- executar o script remotamente passando NodeIndex e MemberIPs

Observação: o script assume que os hosts estão acessíveis e que as credenciais informadas têm permissão para executar Docker e criar pastas.
#>

param(
    [Parameter(Mandatory=$true)]
    [string[]]$Hosts,

    [Parameter(Mandatory=$true)]
    [string]$LocalSetupScript,

    [string]$ReplSetName = 'rsUpload',

    [switch]$CreateAdmin
)

if (-not (Test-Path $LocalSetupScript)) {
    Write-Error "Arquivo local '$LocalSetupScript' não encontrado. Execute o script a partir da pasta que contém 'setup-mongo.ps1' ou passe o caminho correto."
    exit 1
}

# Ler credenciais para conexão remota
$cred = Get-Credential -Message "Insira credenciais (usuário administrador) para conectar aos hosts remotos"

# Montar string com IPs dos membros (ordem é importante)
$memberIPs = ($Hosts -join ',')

for ($i = 0; $i -lt $Hosts.Count; $i++) {
    $target = $Hosts[$i]
    $nodeIndex = $i + 1

    Write-Host "== Preparando host $target (NodeIndex: $nodeIndex) =="

    try {
        $session = New-PSSession -ComputerName $target -Credential $cred -ErrorAction Stop
    } catch {
        Write-Error ("Falha ao criar PSSession para {0}: {1}" -f $target, $_.ToString())
        continue
    }

    # Copiar arquivo para o host (C:\Temp)
    $remoteScriptPath = 'C:\Temp\setup-mongo.ps1'
    try {
        Invoke-Command -Session $session -ScriptBlock { param($p) if (-not (Test-Path (Split-Path $p))) { New-Item -ItemType Directory -Path (Split-Path $p) -Force | Out-Null } } -ArgumentList $remoteScriptPath
        Copy-Item -Path $LocalSetupScript -Destination $remoteScriptPath -ToSession $session -Force
        Write-Host ("Arquivo copiado para {0}:{1}" -f $target, $remoteScriptPath)
    } catch {
        Write-Error ("Falha ao copiar script para {0}: {1}" -f $target, $_.ToString())
        Remove-PSSession -Session $session
        continue
    }

    # Executar o script remotamente com os parâmetros necessários
    try {
        $createAdminFlag = $false
        if ($CreateAdmin.IsPresent -and $nodeIndex -eq 1) { $createAdminFlag = $true }

        Invoke-Command -Session $session -ScriptBlock {
            param($scriptPath, $nodeIndex, $memberIPs, $createAdmin, $replSetName)
            Write-Host "Executando $scriptPath em NodeIndex=$nodeIndex..."
            if ($createAdmin) {
                & $scriptPath -NodeIndex $nodeIndex -MemberIPs $memberIPs -CreateAdmin -ReplSetName $replSetName
            } else {
                & $scriptPath -NodeIndex $nodeIndex -MemberIPs $memberIPs -ReplSetName $replSetName
            }
        } -ArgumentList $remoteScriptPath, $nodeIndex, $memberIPs, $createAdminFlag, $ReplSetName -ErrorAction Stop

        Write-Host "Execução concluída em $host"
    } catch {
        Write-Error ("Falha ao executar o script em {0}: {1}" -f $target, $_.ToString())
    }

    Remove-PSSession -Session $session
}

Write-Host "Deploy remoto finalizado. Verifique logs e rs.status() nos primários/segundos."