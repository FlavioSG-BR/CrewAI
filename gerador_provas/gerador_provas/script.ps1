# ============================================================================
# GERADOR DE PROVAS - Script de Gerenciamento Docker (PowerShell)
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

# Diretório do script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# ============================================================================
# Funções auxiliares
# ============================================================================

function Write-Header {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║         🎓 GERADOR DE PROVAS - CrewAI                        ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Status {
    param([string]$Message)
    Write-Host "[✓] $Message" -ForegroundColor Green
}

function Write-Warning-Msg {
    param([string]$Message)
    Write-Host "[!] $Message" -ForegroundColor Yellow
}

function Write-Error-Msg {
    param([string]$Message)
    Write-Host "[✗] $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "[i] $Message" -ForegroundColor Blue
}

function Test-Docker {
    try {
        $null = docker info 2>&1
        return $true
    }
    catch {
        Write-Error-Msg "Docker não está instalado ou não está rodando."
        Write-Info "Por favor, instale o Docker Desktop e inicie-o."
        exit 1
    }
}

function Test-EnvFile {
    if (-not (Test-Path ".env")) {
        Write-Warning-Msg "Arquivo .env não encontrado. Criando a partir do template..."
        if (Test-Path "env.template") {
            Copy-Item "env.template" ".env"
            Write-Status "Arquivo .env criado com sucesso!"
            Write-Warning-Msg "Revise o arquivo .env e ajuste as configurações se necessário."
        }
        else {
            Write-Error-Msg "Template env.template não encontrado!"
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
            $result = docker-compose exec -T db pg_isready -U user -d provas_db 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Status "Banco de dados está pronto!"
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
    Write-Info "Iniciando aplicação..."
    
    Test-Docker
    Test-EnvFile
    Ensure-Directories
    
    Write-Info "Subindo containers..."
    docker-compose up -d
    
    Wait-ForDatabase
    
    Write-Host ""
    Write-Status "Aplicação iniciada com sucesso!"
    Write-Host ""
    Write-Host "  🌐 Web:      " -NoNewline -ForegroundColor Green
    Write-Host "http://localhost:5000"
    Write-Host "  🗄️  Database: " -NoNewline -ForegroundColor Green
    Write-Host "localhost:5432"
    Write-Host ""
    Write-Info "Use '.\script.ps1 logs' para ver os logs"
    Write-Info "Use '.\script.ps1 stop' para parar"
    Write-Host ""
}

function Invoke-Stop {
    Write-Header
    Write-Info "Parando aplicação..."
    
    Test-Docker
    
    docker-compose down
    
    Write-Status "Aplicação parada com sucesso!"
}

function Invoke-Restart {
    Write-Header
    Write-Info "Reiniciando aplicação..."
    
    Invoke-Stop
    Start-Sleep -Seconds 2
    Invoke-Start
}

function Invoke-Status {
    Write-Header
    Write-Info "Status dos containers:"
    Write-Host ""
    
    Test-Docker
    
    docker-compose ps
    
    Write-Host ""
    
    # Verificar se a web está respondendo
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Status "API está respondendo (http://localhost:5000)"
        }
    }
    catch {
        Write-Warning-Msg "API não está respondendo"
    }
    
    # Verificar se o DB está ok
    try {
        $result = docker-compose exec -T db pg_isready -U user -d provas_db 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Banco de dados está pronto"
        }
        else {
            Write-Warning-Msg "Banco de dados não está respondendo"
        }
    }
    catch {
        Write-Warning-Msg "Banco de dados não está respondendo"
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
        docker-compose logs -f $Service
    }
    else {
        docker-compose logs -f
    }
}

function Invoke-Build {
    Write-Header
    Write-Info "Reconstruindo imagens..."
    
    Test-Docker
    Test-EnvFile
    
    docker-compose build --no-cache
    
    Write-Status "Build concluído!"
}

function Invoke-Migrate {
    Write-Header
    Write-Info "Executando migrações do banco de dados..."
    
    Test-Docker
    
    # Verificar se o container está rodando
    $dbStatus = docker-compose ps db 2>&1
    if ($dbStatus -notmatch "Up") {
        Write-Warning-Msg "Banco de dados não está rodando. Iniciando..."
        docker-compose up -d db
        Wait-ForDatabase
    }
    
    # Executar migrações
    Write-Info "Aplicando scripts SQL..."
    
    $sqlFiles = Get-ChildItem -Path "database" -Filter "0*.sql" | Sort-Object Name
    foreach ($sqlFile in $sqlFiles) {
        Write-Info "Executando: $($sqlFile.Name)"
        $content = Get-Content $sqlFile.FullName -Raw
        docker-compose exec -T db psql -U user -d provas_db -c "$content" 2>$null
    }
    
    Write-Status "Migrações concluídas!"
}

function Invoke-Shell {
    Write-Header
    Write-Info "Abrindo shell no container web..."
    
    Test-Docker
    
    docker-compose exec web /bin/bash
}

function Invoke-DbShell {
    Write-Header
    Write-Info "Abrindo shell do PostgreSQL..."
    
    Test-Docker
    
    docker-compose exec db psql -U user -d provas_db
}

function Invoke-Test {
    Write-Header
    Write-Info "Executando testes..."
    
    Test-Docker
    
    docker-compose exec web python -m pytest tests/ -v
}

function Invoke-Clean {
    Write-Header
    Write-Warning-Msg "ATENÇÃO: Isso irá remover todos os dados!"
    Write-Host ""
    
    $response = Read-Host "Tem certeza que deseja continuar? (y/N)"
    
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Info "Limpando containers e volumes..."
        
        docker-compose down -v --remove-orphans
        
        # Limpar arquivos gerados
        if (Test-Path "output/pdf") { Remove-Item "output/pdf/*" -Force -ErrorAction SilentlyContinue }
        if (Test-Path "output/latex") { Remove-Item "output/latex/*" -Force -ErrorAction SilentlyContinue }
        if (Test-Path "static/diagramas") { Remove-Item "static/diagramas/*" -Force -ErrorAction SilentlyContinue }
        if (Test-Path "logs") { Remove-Item "logs/*" -Force -ErrorAction SilentlyContinue }
        
        Write-Status "Limpeza concluída!"
    }
    else {
        Write-Info "Operação cancelada."
    }
}

function Invoke-Help {
    Write-Header
    Write-Host "Comandos disponíveis:" -ForegroundColor Blue
    Write-Host ""
    Write-Host "  start      " -NoNewline -ForegroundColor Green
    Write-Host "- Inicia a aplicação (containers Docker)"
    Write-Host "  stop       " -NoNewline -ForegroundColor Green
    Write-Host "- Para a aplicação"
    Write-Host "  restart    " -NoNewline -ForegroundColor Green
    Write-Host "- Reinicia a aplicação"
    Write-Host "  status     " -NoNewline -ForegroundColor Green
    Write-Host "- Mostra o status dos containers"
    Write-Host "  logs       " -NoNewline -ForegroundColor Green
    Write-Host "- Exibe logs em tempo real"
    Write-Host "  logs web   " -NoNewline -ForegroundColor Green
    Write-Host "- Exibe logs apenas do container web"
    Write-Host "  logs db    " -NoNewline -ForegroundColor Green
    Write-Host "- Exibe logs apenas do banco de dados"
    Write-Host "  build      " -NoNewline -ForegroundColor Green
    Write-Host "- Reconstrói as imagens Docker"
    Write-Host "  migrate    " -NoNewline -ForegroundColor Green
    Write-Host "- Executa migrações do banco de dados"
    Write-Host "  shell      " -NoNewline -ForegroundColor Green
    Write-Host "- Abre um shell no container da aplicação"
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

