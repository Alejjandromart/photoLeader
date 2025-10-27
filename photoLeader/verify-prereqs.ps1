<#
verify-prereqs.ps1

Valida pré-requisitos em hosts remotos (ou local se nenhum host informado):
- Ping (Test-Connection)
- WinRM (Test-WSMan)
- Porta WinRM (5985) e porta MongoDB (27017) com Test-NetConnection
- Docker acessível (invoca `docker version` remotamente)

Uso (local checks):
  .\verify-prereqs.ps1

Uso (remote checks):
  $hosts = '192.168.0.11','192.168.0.12','192.168.0.13'
  .\verify-prereqs.ps1 -Hosts $hosts

Se os hosts não forem parte do mesmo domínio, você será solicitado a fornecer credenciais para PSRemoting.
#>

param(
    [string[]]$Hosts,
    [switch]$UseHttps, # caso sua WinRM esteja em HTTPS
    [int]$TimeoutSeconds = 3
)

function Write-Result($name, $ok, $msg='') {
    if ($ok) {
        Write-Host "[OK]   $name" -ForegroundColor Green
        if ($msg) { Write-Host "       $msg" }
    } else {
        Write-Host "[FAIL] $name" -ForegroundColor Red
        if ($msg) { Write-Host "       $msg" }
    }
}

if (-not $Hosts -or $Hosts.Count -eq 0) {
    Write-Host "== Executando checagens localmente =="

    # Ping local
    $pong = Test-Connection -ComputerName localhost -Count 1 -Quiet
    Write-Result "Ping localhost" $pong

    # Teste WSMan local
    try {
        Test-WSMan -ErrorAction Stop | Out-Null
        Write-Result "WinRM (WSMan) local" $true
    } catch {
        Write-Result "WinRM (WSMan) local" $false $_.Exception.Message
    }

    # Teste Docker local
    try {
        docker version --format '{{.Server.Version}}' > $null 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Result "Docker local" $true
        } else {
            Write-Result "Docker local" $false "docker não retornou corretamente"
        }
    } catch {
        Write-Result "Docker local" $false $_.Exception.Message
    }

    # Porta 27017 local
    $portCheck = Test-NetConnection -ComputerName localhost -Port 27017 -WarningAction SilentlyContinue
    Write-Result "Porta 27017 local" $portCheck.TcpTestSucceeded ($portCheck | Out-String)

    exit 0
}

# Se aqui, temos hosts remotos
$cred = Get-Credential -Message "Insira credenciais para conectar aos hosts remotos (admin)"

for ($i = 0; $i -lt $Hosts.Count; $i++) {
    $target = $Hosts[$i]
    Write-Host "\n== Checando host: $target (index $i) =="

    # Ping
    try {
        $pong = Test-Connection -ComputerName $target -Count 1 -Quiet -TimeoutSeconds $TimeoutSeconds
        Write-Result "Ping $target" $pong
    } catch {
        Write-Result "Ping $target" $false $_.Exception.Message
    }

    # Test-WSMan (verifica WinRM)
    try {
        if ($UseHttps) {
            Test-WSMan -ComputerName $target -UseSsl -Credential $cred -ErrorAction Stop | Out-Null
        } else {
            Test-WSMan -ComputerName $target -Credential $cred -ErrorAction Stop | Out-Null
        }
        Write-Result "WinRM (WSMan) $target" $true
    } catch {
        Write-Result "WinRM (WSMan) $target" $false $_.Exception.Message
    }

    # Test ports (5985/5986 optional) and 27017
    try {
        $r = Test-NetConnection -ComputerName $target -Port 27017 -WarningAction SilentlyContinue
        Write-Result "Porta 27017 em $target" $r.TcpTestSucceeded ($r | Out-String)
    } catch {
        Write-Result "Porta 27017 em $target" $false $_.Exception.Message
    }

    # Checar Docker via PSRemoting: tenta criar uma PSSession e executar 'docker version'
    try {
        $session = New-PSSession -ComputerName $target -Credential $cred -ErrorAction Stop
        try {
            $dockerOk = Invoke-Command -Session $session -ScriptBlock {
                try {
                    docker version --format '{{.Server.Version}}' > $null 2>&1
                    return $LASTEXITCODE -eq 0
                } catch {
                    return $false
                }
            } -ErrorAction Stop

            if ($dockerOk -is [System.Array]) { $dockerOk = $dockerOk[0] }
            Write-Result "Docker em $target" $dockerOk
        } catch {
            Write-Result "Docker em $target" $false $_.Exception.Message
        } finally {
            Remove-PSSession -Session $session
        }
    } catch {
        Write-Result "PSSession em $target" $false $_.Exception.Message
    }
}

Write-Host "\n== Checagem concluída =="