# ============================================================================
# GERADOR DE PROVAS - Script de Gerenciamento Docker/Podman (PowerShell)
# ============================================================================
# Uso: .\script.ps1 [start|stop|restart|status|logs|build|migrate|clean|help]
# ============================================================================

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "build", "migrate", "shell", "db-shell", "test", "clean", "help")]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [string]$SubCommand = ""
)

$ErrorActionPreference = "Stop"

# Diretorio do script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# ============================================================================
# Variaveis globais para Docker/Podman
# ============================================================================
$script:ContainerCmd = $null
$script:ComposeCmd = $null

# ============================================================================
# Funcoes auxiliares
# ============================================================================

function Write-Header {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "         GERADOR DE PROVAS - CrewAI                            " -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Status {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Warning-Msg {
    param([string]$Message)
    Write-Host "[!] $Message" -ForegroundColor Yellow
}

function Write-Error-Msg {
    param([string]$Message)
    Write-Host "[X] $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "[i] $Message" -ForegroundColor Blue
}

function Find-Podman {
    # Procurar Podman em locais comuns
    $possiblePaths = @(
        "$env:LOCALAPPDATA\Microsoft\WindowsApps\podman.exe",
        "$env:ProgramFiles\RedHat\Podman\podman.exe",
        "$env:LOCALAPPDATA\Podman Desktop\resources\podman\bin\podman.exe",
        "C:\Program Files\RedHat\Podman\podman.exe"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            return $path
        }
    }
    
    # Tentar no PATH
    $pathCmd = Get-Command podman -ErrorAction SilentlyContinue
    if ($pathCmd) {
        return $pathCmd.Source
    }
    
    return $null
}

function Test-Docker {
    # Tentar Docker primeiro
    try {
        $dockerCheck = Get-Command docker -ErrorAction SilentlyContinue
        if ($dockerCheck) {
            $null = & docker info 2>&1
            if ($LASTEXITCODE -eq 0) {
                $script:ContainerCmd = "docker"
                # Verificar docker compose (sem hifen)
                $null = & docker compose version 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $script:ComposeCmd = "docker compose"
                    Write-Info "Usando Docker com 'docker compose'"
                    return $true
                }
                # Tentar docker-compose (com hifen)
                $dockerComposeCheck = Get-Command docker-compose -ErrorAction SilentlyContinue
                if ($dockerComposeCheck) {
                    $script:ComposeCmd = "docker-compose"
                    Write-Info "Usando Docker com 'docker-compose'"
                    return $true
                }
            }
        }
    }
    catch { }
    
    # Tentar Podman
    $podmanPath = Find-Podman
    if ($podmanPath) {
        Write-Info "Podman encontrado em: $podmanPath"
        
        # Verificar se Podman esta rodando
        $podmanInfoResult = & $podmanPath info 2>&1
        $podmanInfoText = $podmanInfoResult | Out-String
        
        if ($podmanInfoText -match "APIVersion" -or $podmanInfoText -match "host:") {
            $script:ContainerCmd = $podmanPath
            Write-Status "Podman esta rodando!"
            
            # Verificar se podman-compose esta instalado (Python)
            $podmanComposeCheck = Get-Command podman-compose -ErrorAction SilentlyContinue
            if ($podmanComposeCheck) {
                $script:ComposeCmd = "podman-compose"
                Write-Info "Usando 'podman-compose' (Python)"
                return $true
            }
            
            # Tentar 'podman compose' (pode usar docker-compose como provider)
            $ErrorActionPreference = "SilentlyContinue"
            $composeResult = & $podmanPath compose version 2>&1 | Out-String
            $ErrorActionPreference = "Stop"
            
            # Verificar se retornou algo (mesmo com aviso)
            if ($composeResult -match "version" -or $composeResult -match "compose" -or $composeResult -match "docker-compose") {
                $script:ComposeCmd = "$podmanPath compose"
                Write-Info "Usando 'podman compose'"
                return $true
            }
            
            # Compose nao encontrado - tentar instalar podman-compose via pip
            Write-Warning-Msg "podman-compose nao encontrado."
            Write-Info "Tentando instalar podman-compose..."
            
            try {
                $pipResult = pip install podman-compose 2>&1
                $podmanComposeCheck = Get-Command podman-compose -ErrorAction SilentlyContinue
                if ($podmanComposeCheck) {
                    $script:ComposeCmd = "podman-compose"
                    Write-Status "podman-compose instalado com sucesso!"
                    return $true
                }
            }
            catch { }
            
            Write-Error-Msg "Nao foi possivel configurar compose."
            Write-Info "Instale manualmente: pip install podman-compose"
            exit 1
        }
        else {
            Write-Warning-Msg "Podman encontrado mas nao esta rodando."
            Write-Info "Execute: podman machine start"
            exit 1
        }
    }
    
    Write-Error-Msg "Docker/Podman nao esta instalado ou nao esta rodando."
    Write-Info "Por favor, inicie o Docker Desktop ou execute: podman machine start"
    exit 1
}

# Funcao auxiliar para executar comandos compose
function Invoke-Compose {
    param([string[]]$Arguments)
    
    if ($script:ComposeCmd -eq "docker compose") {
        & docker compose @Arguments
    }
    elseif ($script:ComposeCmd -eq "docker-compose") {
        & docker-compose @Arguments
    }
    elseif ($script:ComposeCmd -like "*podman* compose") {
        # Podman com compose plugin (pode ter caminho completo)
        $podmanExe = $script:ComposeCmd -replace " compose$", ""
        & $podmanExe compose @Arguments
    }
    elseif ($script:ComposeCmd -eq "podman-compose") {
        & podman-compose @Arguments
    }
    else {
        Write-Error-Msg "Comando compose nao configurado: $($script:ComposeCmd)"
        exit 1
    }
}

function Test-EnvFile {
    if (-not (Test-Path ".env")) {
        Write-Warning-Msg "Arquivo .env nao encontrado. Criando a partir do template..."
        if (Test-Path "env.template") {
            Copy-Item "env.template" ".env"
            # Ajustar DATABASE_URL para Docker
            $content = Get-Content ".env" -Raw
            $content = $content -replace "DATABASE_URL=postgresql://user:password@localhost:5432/provas_db", "DATABASE_URL=postgresql://user:password@db:5432/provas_db"
            $content = $content -replace "POSTGRES_HOST=localhost", "POSTGRES_HOST=db"
            Set-Content ".env" $content
            Write-Status "Arquivo .env criado com sucesso!"
        }
        else {
            Write-Error-Msg "Template env.template nao encontrado!"
            exit 1
        }
    }
}

function Wait-ForDatabase {
    Write-Info "Aguardando banco de dados ficar pronto..."
    $maxAttempts = 30
    $attempt = 1
    
    while ($attempt -le $maxAttempts) {
        try {
            Invoke-Compose @("exec", "-T", "db", "pg_isready", "-U", "provas_user", "-d", "provas_db") 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Status "Banco de dados esta pronto!"
                return $true
            }
        }
        catch { }
        
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 2
        $attempt++
    }
    
    Write-Host ""
    Write-Error-Msg "Timeout aguardando o banco de dados."
    return $false
}

function Ensure-Directories {
    $dirs = @("output/pdf", "output/latex", "static/diagramas", "logs")
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
}

# ============================================================================
# Comandos principais
# ============================================================================

function Invoke-Start {
    Write-Header
    Write-Info "Iniciando aplicacao..."
    
    Test-Docker
    Test-EnvFile
    Ensure-Directories
    
    Write-Info "Subindo containers..."
    Invoke-Compose @("up", "-d")
    
    Wait-ForDatabase
    
    Write-Host ""
    Write-Status "Aplicacao iniciada com sucesso!"
    Write-Host ""
    Write-Host "  Web:      http://localhost:5000" -ForegroundColor Green
    Write-Host "  Database: localhost:5432" -ForegroundColor Green
    Write-Host ""
    Write-Info "Use '.\script.ps1 logs' para ver os logs"
    Write-Info "Use '.\script.ps1 stop' para parar"
    Write-Host ""
}

function Invoke-Stop {
    Write-Header
    Write-Info "Parando aplicacao..."
    
    Test-Docker
    
    Invoke-Compose @("down")
    
    Write-Status "Aplicacao parada com sucesso!"
}

function Invoke-Restart {
    Write-Header
    Write-Info "Reiniciando aplicacao..."
    
    Invoke-Stop
    Start-Sleep -Seconds 2
    Invoke-Start
}

function Invoke-Status {
    Write-Header
    Write-Info "Status dos containers:"
    Write-Host ""
    
    Test-Docker
    
    Invoke-Compose @("ps")
    
    Write-Host ""
    
    # Verificar se a web esta respondendo
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Status "API esta respondendo (http://localhost:5000)"
        }
    }
    catch {
        Write-Warning-Msg "API nao esta respondendo"
    }
    
    # Verificar se o DB esta ok
    try {
        Invoke-Compose @("exec", "-T", "db", "pg_isready", "-U", "provas_user", "-d", "provas_db") 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Banco de dados esta pronto"
        }
        else {
            Write-Warning-Msg "Banco de dados nao esta respondendo"
        }
    }
    catch {
        Write-Warning-Msg "Banco de dados nao esta respondendo"
    }
    
    Write-Host ""
}

function Invoke-Logs {
    param([string]$Service = "")
    
    Write-Header
    Write-Info "Exibindo logs (Ctrl+C para sair)..."
    Write-Host ""
    
    Test-Docker
    
    if ($Service) {
        Invoke-Compose @("logs", "-f", $Service)
    }
    else {
        Invoke-Compose @("logs", "-f")
    }
}

function Invoke-Build {
    Write-Header
    Write-Info "Reconstruindo imagens..."
    
    Test-Docker
    Test-EnvFile
    
    Invoke-Compose @("build", "--no-cache")
    
    Write-Status "Build concluido!"
}

function Invoke-Migrate {
    Write-Header
    Write-Info "Executando migracoes do banco de dados..."
    
    Test-Docker
    
    # Verificar se o container esta rodando
    $dbStatus = Invoke-Compose @("ps", "db") 2>&1
    if ($dbStatus -notmatch "Up" -and $dbStatus -notmatch "running") {
        Write-Warning-Msg "Banco de dados nao esta rodando. Iniciando..."
        Invoke-Compose @("up", "-d", "db")
        Wait-ForDatabase
    }
    
    # Executar migracoes
    Write-Info "Aplicando scripts SQL..."
    
    $sqlFiles = Get-ChildItem -Path "database" -Filter "0*.sql" -ErrorAction SilentlyContinue | Sort-Object Name
    foreach ($sqlFile in $sqlFiles) {
        Write-Info "Executando: $($sqlFile.Name)"
        Invoke-Compose @("exec", "-T", "db", "psql", "-U", "provas_user", "-d", "provas_db", "-f", "/docker-entrypoint-initdb.d/$($sqlFile.Name)") 2>$null
    }
    
    Write-Status "Migracoes concluidas!"
}

function Invoke-Shell {
    Write-Header
    Write-Info "Abrindo shell no container web..."
    
    Test-Docker
    
    Invoke-Compose @("exec", "web", "/bin/bash")
}

function Invoke-DbShell {
    Write-Header
    Write-Info "Abrindo shell do PostgreSQL..."
    
    Test-Docker
    
    Invoke-Compose @("exec", "db", "psql", "-U", "provas_user", "-d", "provas_db")
}

function Invoke-Test {
    Write-Header
    Write-Info "Executando testes..."
    
    Test-Docker
    
    Invoke-Compose @("exec", "web", "python", "-m", "pytest", "tests/", "-v")
}

function Invoke-Clean {
    Write-Header
    Write-Warning-Msg "ATENCAO: Isso ira remover todos os dados!"
    Write-Host ""
    
    $response = Read-Host "Tem certeza que deseja continuar? (y/N)"
    
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Info "Limpando containers e volumes..."
        
        Invoke-Compose @("down", "-v", "--remove-orphans")
        
        # Limpar arquivos gerados
        if (Test-Path "output/pdf") { Remove-Item "output/pdf/*" -Force -ErrorAction SilentlyContinue }
        if (Test-Path "output/latex") { Remove-Item "output/latex/*" -Force -ErrorAction SilentlyContinue }
        if (Test-Path "static/diagramas") { Remove-Item "static/diagramas/*" -Force -ErrorAction SilentlyContinue }
        if (Test-Path "logs") { Remove-Item "logs/*" -Force -ErrorAction SilentlyContinue }
        
        Write-Status "Limpeza concluida!"
    }
    else {
        Write-Info "Operacao cancelada."
    }
}

function Invoke-Help {
    Write-Header
    Write-Host "Comandos disponiveis:" -ForegroundColor Blue
    Write-Host ""
    Write-Host "  start      " -NoNewline -ForegroundColor Green
    Write-Host "- Inicia a aplicacao (containers Docker)"
    Write-Host "  stop       " -NoNewline -ForegroundColor Green
    Write-Host "- Para a aplicacao"
    Write-Host "  restart    " -NoNewline -ForegroundColor Green
    Write-Host "- Reinicia a aplicacao"
    Write-Host "  status     " -NoNewline -ForegroundColor Green
    Write-Host "- Mostra o status dos containers"
    Write-Host "  logs       " -NoNewline -ForegroundColor Green
    Write-Host "- Exibe logs em tempo real"
    Write-Host "  logs web   " -NoNewline -ForegroundColor Green
    Write-Host "- Exibe logs apenas do container web"
    Write-Host "  logs db    " -NoNewline -ForegroundColor Green
    Write-Host "- Exibe logs apenas do banco de dados"
    Write-Host "  build      " -NoNewline -ForegroundColor Green
    Write-Host "- Reconstroi as imagens Docker"
    Write-Host "  migrate    " -NoNewline -ForegroundColor Green
    Write-Host "- Executa migracoes do banco de dados"
    Write-Host "  shell      " -NoNewline -ForegroundColor Green
    Write-Host "- Abre um shell no container da aplicacao"
    Write-Host "  db-shell   " -NoNewline -ForegroundColor Green
    Write-Host "- Abre o shell do PostgreSQL"
    Write-Host "  test       " -NoNewline -ForegroundColor Green
    Write-Host "- Executa os testes"
    Write-Host "  clean      " -NoNewline -ForegroundColor Green
    Write-Host "- Remove containers e dados (CUIDADO!)"
    Write-Host "  help       " -NoNewline -ForegroundColor Green
    Write-Host "- Mostra esta ajuda"
    Write-Host ""
    Write-Host "Exemplos:" -ForegroundColor Blue
    Write-Host "  .\script.ps1 start"
    Write-Host "  .\script.ps1 logs web"
    Write-Host "  .\script.ps1 restart"
    Write-Host ""
}

# ============================================================================
# Main
# ============================================================================

switch ($Command) {
    "start"    { Invoke-Start }
    "stop"     { Invoke-Stop }
    "restart"  { Invoke-Restart }
    "status"   { Invoke-Status }
    "logs"     { Invoke-Logs -Service $SubCommand }
    "build"    { Invoke-Build }
    "migrate"  { Invoke-Migrate }
    "shell"    { Invoke-Shell }
    "db-shell" { Invoke-DbShell }
    "test"     { Invoke-Test }
    "clean"    { Invoke-Clean }
    "help"     { Invoke-Help }
    default    { Invoke-Help }
}
