# ============================================================================
# GERADOR DE PROVAS - Dockerfile
# ============================================================================
# Build: docker build -t gerador-provas .
# Run:   docker run -p 5000:5000 gerador-provas
# ============================================================================

FROM python:3.11-slim

# Metadados
LABEL maintainer="Gerador de Provas Team"
LABEL description="Aplicação CrewAI para geração automática de provas"
LABEL version="1.0.0"

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Diretório de trabalho
WORKDIR /app

# Instala dependências de sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Para PostgreSQL
    libpq-dev \
    # Para compilação de algumas libs Python
    python3-dev \
    gcc \
    # Para healthcheck
    curl \
    # Para geração de PDF (LaTeX)
    # texlive-latex-base \
    # texlive-fonts-recommended \
    # Limpar cache apt
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar apenas requirements primeiro (para cache de layers)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar o resto do código
COPY . .

# Criar diretórios necessários
RUN mkdir -p output/pdf output/latex static/diagramas logs

# Expor porta
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Comando de inicialização
CMD ["python", "app.py"]
