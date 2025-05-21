FROM python:3.11-slim

# Instala dependências de sistema necessárias (para reportlab, sympy, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Instala dependências Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["python", "app.py"]