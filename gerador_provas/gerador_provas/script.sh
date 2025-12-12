#!/bin/bash
# ============================================================================
# GERADOR DE PROVAS - Script de Gerenciamento Docker
# ============================================================================
# Uso: ./script.sh [start|stop|restart|status|logs|build|migrate|clean|help]
# ============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Nome do projeto
PROJECT_NAME="gerador-provas"

# Comandos Docker/Podman (serão definidos em check_docker)
DOCKER_CMD=""
COMPOSE_CMD=""

# ============================================================================
# Funções auxiliares
# ============================================================================

print_header() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}         ${BLUE}🎓 GERADOR DE PROVAS - CrewAI${NC}                       ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

check_docker() {
    # Verificar se docker ou podman está disponível
    if command -v podman &> /dev/null; then
        DOCKER_CMD="podman"
        # Verificar se podman-compose existe, senão usar podman compose
        if command -v podman-compose &> /dev/null; then
            COMPOSE_CMD="podman-compose"
        else
            COMPOSE_CMD="podman compose"
        fi
    elif command -v docker &> /dev/null; then
        DOCKER_CMD="docker"
        COMPOSE_CMD="docker-compose"
    else
        print_error "Docker ou Podman não está instalado."
        print_info "Instale Docker: https://docs.docker.com/get-docker/"
        print_info "Ou Podman: https://podman.io/getting-started/installation"
        exit 1
    fi
    
    # Verificar se está rodando
    if ! $DOCKER_CMD info &> /dev/null; then
        print_error "$DOCKER_CMD não está rodando."
        if [ "$DOCKER_CMD" = "podman" ]; then
            print_info "Execute: podman machine start"
        else
            print_info "Inicie o Docker Desktop ou o serviço Docker."
        fi
        exit 1
    fi
    
    print_info "Usando: $DOCKER_CMD ($COMPOSE_CMD)"
}

check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning "Arquivo .env não encontrado. Criando a partir do template..."
        if [ -f "env.template" ]; then
            cp env.template .env
            # Ajustar DATABASE_URL para Docker (usar 'db' como host)
            sed -i 's|DATABASE_URL=postgresql://user:password@localhost:5432/provas_db|DATABASE_URL=postgresql://user:password@db:5432/provas_db|g' .env
            sed -i 's|POSTGRES_HOST=localhost|POSTGRES_HOST=db|g' .env
            print_status "Arquivo .env criado com sucesso!"
        else
            print_error "Template env.template não encontrado!"
            exit 1
        fi
    fi
}

wait_for_db() {
    print_info "Aguardando banco de dados ficar pronto..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if $COMPOSE_CMD exec -T db pg_isready -U user -d provas_db &> /dev/null; then
            print_status "Banco de dados está pronto!"
            return 0
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    print_error "Timeout aguardando o banco de dados."
    return 1
}

# ============================================================================
# Comandos principais
# ============================================================================

cmd_start() {
    print_header
    print_info "Iniciando aplicação..."
    
    check_docker
    check_env_file
    
    # Criar diretórios necessários
    mkdir -p output/pdf output/latex static/diagramas logs
    
    print_info "Subindo containers..."
    $COMPOSE_CMD up -d
    
    wait_for_db
    
    echo ""
    print_status "Aplicação iniciada com sucesso!"
    echo ""
    echo -e "  ${GREEN}🌐 Web:${NC}      http://localhost:5000"
    echo -e "  ${GREEN}🗄️  Database:${NC} localhost:5432"
    echo ""
    print_info "Use './script.sh logs' para ver os logs"
    print_info "Use './script.sh stop' para parar"
    echo ""
}

cmd_stop() {
    print_header
    print_info "Parando aplicação..."
    
    check_docker
    
    $COMPOSE_CMD down
    
    print_status "Aplicação parada com sucesso!"
}

cmd_restart() {
    print_header
    print_info "Reiniciando aplicação..."
    
    cmd_stop
    sleep 2
    cmd_start
}

cmd_status() {
    print_header
    print_info "Status dos containers:"
    echo ""
    
    check_docker
    
    $COMPOSE_CMD ps
    
    echo ""
    
    # Verificar se a web está respondendo
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/health 2>/dev/null | grep -q "200"; then
        print_status "API está respondendo (http://localhost:5000)"
    else
        print_warning "API não está respondendo"
    fi
    
    # Verificar se o DB está ok
    if $COMPOSE_CMD exec -T db pg_isready -U user -d provas_db &> /dev/null; then
        print_status "Banco de dados está pronto"
    else
        print_warning "Banco de dados não está respondendo"
    fi
    echo ""
}

cmd_logs() {
    print_header
    print_info "Exibindo logs (Ctrl+C para sair)..."
    echo ""
    
    check_docker
    
    if [ -n "$2" ]; then
        $COMPOSE_CMD logs -f "$2"
    else
        $COMPOSE_CMD logs -f
    fi
}

cmd_build() {
    print_header
    print_info "Reconstruindo imagens..."
    
    check_docker
    check_env_file
    
    $COMPOSE_CMD build --no-cache
    
    print_status "Build concluído!"
}

cmd_migrate() {
    print_header
    print_info "Executando migrações do banco de dados..."
    
    check_docker
    
    # Verificar se o container está rodando
    if ! $COMPOSE_CMD ps | grep -q "provas_db.*Up"; then
        print_warning "Banco de dados não está rodando. Iniciando..."
        $COMPOSE_CMD up -d db
        wait_for_db
    fi
    
    # Executar migrações
    print_info "Aplicando scripts SQL..."
    
    for sql_file in database/0*.sql; do
        if [ -f "$sql_file" ]; then
            filename=$(basename "$sql_file")
            print_info "Executando: $filename"
            $COMPOSE_CMD exec -T db psql -U user -d provas_db -f /app/$sql_file 2>/dev/null || true
        fi
    done
    
    print_status "Migrações concluídas!"
}

cmd_clean() {
    print_header
    print_warning "ATENÇÃO: Isso irá remover todos os dados!"
    echo ""
    read -p "Tem certeza que deseja continuar? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Limpando containers e volumes..."
        
        $COMPOSE_CMD down -v --remove-orphans
        
        # Limpar arquivos gerados
        rm -rf output/pdf/* output/latex/* static/diagramas/* logs/*
        
        print_status "Limpeza concluída!"
    else
        print_info "Operação cancelada."
    fi
}

cmd_shell() {
    print_header
    print_info "Abrindo shell no container web..."
    
    check_docker
    
    $COMPOSE_CMD exec web /bin/bash
}

cmd_db_shell() {
    print_header
    print_info "Abrindo shell do PostgreSQL..."
    
    check_docker
    
    $COMPOSE_CMD exec db psql -U user -d provas_db
}

cmd_test() {
    print_header
    print_info "Executando testes..."
    
    check_docker
    
    $COMPOSE_CMD exec web python -m pytest tests/ -v
}

cmd_help() {
    print_header
    echo -e "${BLUE}Comandos disponíveis:${NC}"
    echo ""
    echo -e "  ${GREEN}start${NC}      - Inicia a aplicação (containers Docker)"
    echo -e "  ${GREEN}stop${NC}       - Para a aplicação"
    echo -e "  ${GREEN}restart${NC}    - Reinicia a aplicação"
    echo -e "  ${GREEN}status${NC}     - Mostra o status dos containers"
    echo -e "  ${GREEN}logs${NC}       - Exibe logs em tempo real"
    echo -e "  ${GREEN}logs web${NC}   - Exibe logs apenas do container web"
    echo -e "  ${GREEN}logs db${NC}    - Exibe logs apenas do banco de dados"
    echo -e "  ${GREEN}build${NC}      - Reconstrói as imagens Docker"
    echo -e "  ${GREEN}migrate${NC}    - Executa migrações do banco de dados"
    echo -e "  ${GREEN}shell${NC}      - Abre um shell no container da aplicação"
    echo -e "  ${GREEN}db-shell${NC}   - Abre o shell do PostgreSQL"
    echo -e "  ${GREEN}test${NC}       - Executa os testes"
    echo -e "  ${GREEN}clean${NC}      - Remove containers e dados (CUIDADO!)"
    echo -e "  ${GREEN}help${NC}       - Mostra esta ajuda"
    echo ""
    echo -e "${BLUE}Exemplos:${NC}"
    echo "  ./script.sh start"
    echo "  ./script.sh logs web"
    echo "  ./script.sh restart"
    echo ""
}

# ============================================================================
# Main
# ============================================================================

case "${1:-help}" in
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    restart)
        cmd_restart
        ;;
    status)
        cmd_status
        ;;
    logs)
        cmd_logs "$@"
        ;;
    build)
        cmd_build
        ;;
    migrate)
        cmd_migrate
        ;;
    shell)
        cmd_shell
        ;;
    db-shell)
        cmd_db_shell
        ;;
    test)
        cmd_test
        ;;
    clean)
        cmd_clean
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        print_error "Comando desconhecido: $1"
        echo ""
        cmd_help
        exit 1
        ;;
esac

