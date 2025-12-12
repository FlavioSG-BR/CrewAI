@echo off
REM ============================================================================
REM GERADOR DE PROVAS - Script de Gerenciamento Docker (Windows CMD)
REM ============================================================================
REM Uso: script.bat [start|stop|restart|status|logs|build|migrate|clean|help]
REM ============================================================================

setlocal enabledelayedexpansion

REM Ir para o diretório do script
cd /d "%~dp0"

REM Verificar comando
set "COMMAND=%~1"
if "%COMMAND%"=="" set "COMMAND=help"

REM Redirecionar para PowerShell (mais funcionalidade)
if "%COMMAND%"=="start" goto :start
if "%COMMAND%"=="stop" goto :stop
if "%COMMAND%"=="restart" goto :restart
if "%COMMAND%"=="status" goto :status
if "%COMMAND%"=="logs" goto :logs
if "%COMMAND%"=="build" goto :build
if "%COMMAND%"=="migrate" goto :migrate
if "%COMMAND%"=="clean" goto :clean
if "%COMMAND%"=="help" goto :help
goto :help

:header
echo.
echo ================================================================
echo          GERADOR DE PROVAS - CrewAI
echo ================================================================
echo.
goto :eof

:check_docker
docker info >nul 2>&1
if errorlevel 1 (
    echo [X] Docker nao esta instalado ou nao esta rodando.
    echo     Por favor, instale o Docker Desktop e inicie-o.
    exit /b 1
)
goto :eof

:check_env
if not exist ".env" (
    echo [!] Arquivo .env nao encontrado. Criando a partir do template...
    if exist "env.template" (
        copy "env.template" ".env" >nul
        echo [OK] Arquivo .env criado com sucesso!
    ) else (
        echo [X] Template env.template nao encontrado!
        exit /b 1
    )
)
goto :eof

:ensure_dirs
if not exist "output\pdf" mkdir "output\pdf"
if not exist "output\latex" mkdir "output\latex"
if not exist "static\diagramas" mkdir "static\diagramas"
if not exist "logs" mkdir "logs"
goto :eof

:start
call :header
echo [i] Iniciando aplicacao...
call :check_docker
call :check_env
call :ensure_dirs
echo [i] Subindo containers...
docker-compose up -d
echo.
echo [OK] Aplicacao iniciada!
echo.
echo   Web:      http://localhost:5000
echo   Database: localhost:5432
echo.
echo Use 'script.bat logs' para ver os logs
echo Use 'script.bat stop' para parar
goto :end

:stop
call :header
echo [i] Parando aplicacao...
call :check_docker
docker-compose down
echo [OK] Aplicacao parada com sucesso!
goto :end

:restart
call :header
echo [i] Reiniciando aplicacao...
call :stop
timeout /t 2 /nobreak >nul
call :start
goto :end

:status
call :header
echo [i] Status dos containers:
echo.
call :check_docker
docker-compose ps
echo.
goto :end

:logs
call :header
echo [i] Exibindo logs (Ctrl+C para sair)...
echo.
call :check_docker
if "%~2"=="" (
    docker-compose logs -f
) else (
    docker-compose logs -f %~2
)
goto :end

:build
call :header
echo [i] Reconstruindo imagens...
call :check_docker
call :check_env
docker-compose build --no-cache
echo [OK] Build concluido!
goto :end

:migrate
call :header
echo [i] Executando migracoes do banco de dados...
call :check_docker
echo [i] Aplicando scripts SQL...
for %%f in (database\0*.sql) do (
    echo [i] Executando: %%~nxf
    docker-compose exec -T db psql -U user -d provas_db -f /docker-entrypoint-initdb.d/%%~nxf 2>nul
)
echo [OK] Migracoes concluidas!
goto :end

:clean
call :header
echo [!] ATENCAO: Isso ira remover todos os dados!
echo.
set /p "CONFIRM=Tem certeza que deseja continuar? (y/N): "
if /i "%CONFIRM%"=="y" (
    echo [i] Limpando containers e volumes...
    docker-compose down -v --remove-orphans
    if exist "output\pdf\*" del /q "output\pdf\*" 2>nul
    if exist "output\latex\*" del /q "output\latex\*" 2>nul
    if exist "static\diagramas\*" del /q "static\diagramas\*" 2>nul
    if exist "logs\*" del /q "logs\*" 2>nul
    echo [OK] Limpeza concluida!
) else (
    echo [i] Operacao cancelada.
)
goto :end

:help
call :header
echo Comandos disponiveis:
echo.
echo   start      - Inicia a aplicacao (containers Docker)
echo   stop       - Para a aplicacao
echo   restart    - Reinicia a aplicacao
echo   status     - Mostra o status dos containers
echo   logs       - Exibe logs em tempo real
echo   logs web   - Exibe logs apenas do container web
echo   logs db    - Exibe logs apenas do banco de dados
echo   build      - Reconstroi as imagens Docker
echo   migrate    - Executa migracoes do banco de dados
echo   clean      - Remove containers e dados (CUIDADO!)
echo   help       - Mostra esta ajuda
echo.
echo Exemplos:
echo   script.bat start
echo   script.bat logs web
echo   script.bat restart
echo.
echo Para mais funcionalidades, use o PowerShell:
echo   .\script.ps1 start
echo.
goto :end

:end
endlocal

