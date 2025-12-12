# 🎓 Gerador de Provas Automatizado com CrewAI

![CrewAI + Flask](https://img.shields.io/badge/Powered%20by-CrewAI%20%2B%20Flask-blueviolet)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)
![Podman](https://img.shields.io/badge/Podman-Compatible-892CA0)
![License](https://img.shields.io/badge/License-MIT-green)

Um sistema inteligente para criação de provas personalizadas de **Matemática, Física e Química**, utilizando agentes de IA especializados.

---

## 🚀 Funcionalidades Principais

- **Geração automática de questões** por matéria/tópico
- **Múltiplos tipos de questão**: dissertativa, múltipla escolha, V/F
- **Geração de diagramas** em tempo real (gráficos, circuitos, geometria)
- **Validação especializada**:
  - Matemática: Verificação de equações com SymPy
  - Física: Checagem de unidades e fórmulas
  - Química: Validação de fórmulas moleculares com RDKit
- **Exportação para**:
  - PDF (formatação ABNT)
  - LaTeX (para editores acadêmicos)
  - Gabarito com respostas detalhadas
- **Dashboard de métricas** com Plotly

---

## 🛠️ Pré-requisitos

- **Python 3.11+**
- **Docker** ou **Podman** (recomendado)
- **PostgreSQL 15+** (incluído no Docker)

---

## 📦 Instalação e Execução

### Opção 1: Com Docker/Podman (Recomendado)

#### Windows (PowerShell)

```powershell
# Navegar até o diretório do projeto
cd gerador_provas\gerador_provas

# Iniciar a aplicação
.\script.ps1 start

# Ver logs em tempo real
.\script.ps1 logs

# Parar a aplicação
.\script.ps1 stop
```

#### Windows (CMD)

```cmd
cd gerador_provas\gerador_provas

script.bat start
script.bat logs
script.bat stop
```

#### Linux/Mac (Bash)

```bash
cd gerador_provas/gerador_provas

# Dar permissão de execução (primeira vez)
chmod +x script.sh

# Iniciar
./script.sh start

# Ver logs
./script.sh logs

# Parar
./script.sh stop
```

### Comandos Disponíveis no Script

| Comando | Descrição |
|---------|-----------|
| `start` | Inicia a aplicação (containers Docker/Podman) |
| `stop` | Para a aplicação |
| `restart` | Reinicia a aplicação |
| `status` | Mostra o status dos containers |
| `logs` | Exibe logs em tempo real |
| `logs web` | Logs apenas da aplicação web |
| `logs db` | Logs apenas do banco de dados |
| `build` | Reconstrói as imagens |
| `migrate` | Executa migrações do banco de dados |
| `shell` | Abre shell no container da aplicação |
| `db-shell` | Abre o shell do PostgreSQL |
| `test` | Executa os testes |
| `clean` | Remove containers e dados ⚠️ |
| `help` | Mostra ajuda |

---

### Opção 2: Instalação Local (sem Docker)

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/gerador-provas.git
cd gerador-provas/gerador_provas/gerador_provas

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate   # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp env.template .env
# Edite o arquivo .env com suas configurações

# Iniciar o PostgreSQL localmente (necessário)
# ... configure o DATABASE_URL no .env

# Executar a aplicação
python app.py
```

---

## 🐳 Usando com Podman (Windows)

Se você usa Podman em vez de Docker:

```powershell
# 1. Criar alias para docker (executar uma vez por sessão)
Set-Alias -Name docker -Value podman

# 2. Inicializar a máquina Podman (primeira vez)
podman machine init

# 3. Iniciar a máquina
podman machine start

# 4. Usar os scripts normalmente
.\script.ps1 start
```

Para alias permanente, adicione ao seu `$PROFILE`:

```powershell
# Abrir o profile
notepad $PROFILE

# Adicionar estas linhas:
Set-Alias -Name docker -Value podman
function docker-compose { podman compose @args }
```

---

## 🌐 Acessando a Aplicação

Após iniciar com `start`:

| Serviço | URL |
|---------|-----|
| **Web App** | http://localhost:5000 |
| **API Health** | http://localhost:5000/api/health |
| **Banco de Dados** | localhost:5432 |
| **Adminer** (debug) | http://localhost:8080 |

---

## 🧩 Estrutura do Projeto

```
gerador_provas/
├── app.py                 # Aplicação Flask principal
├── config.py              # Configurações centralizadas
├── script.sh/.ps1/.bat    # Scripts de gerenciamento
├── docker-compose.yml     # Orquestração de containers
├── Dockerfile             # Imagem da aplicação
├── requirements.txt       # Dependências Python
├── env.template           # Template de variáveis de ambiente
│
├── backend/
│   ├── agents/            # Agentes CrewAI especializados
│   │   ├── matematica.py
│   │   ├── fisica.py
│   │   ├── quimica.py
│   │   ├── revisor.py
│   │   ├── classificador.py
│   │   ├── imagens.py
│   │   └── persistencia.py
│   ├── services/          # Camada de serviços
│   ├── repositories/      # Acesso a dados
│   ├── utils/             # Utilitários
│   └── main_crewai.py     # Orquestração CrewAI
│
├── database/              # Migrações SQL
│   ├── 001_schema_base.sql
│   ├── 002_tabelas_dominio.sql
│   ├── ...
│   └── migrate.py
│
├── templates/             # Templates HTML (Jinja2)
├── static/                # Arquivos estáticos
│   └── diagramas/         # Diagramas gerados
├── output/                # Provas exportadas
│   ├── pdf/
│   └── latex/
├── logs/                  # Logs da aplicação
└── tests/                 # Testes unitários
```

---

## 🤖 Agentes Implementados

| Agente | Função |
|--------|--------|
| **Matemática** | Gera questões de álgebra, geometria, funções, probabilidade |
| **Física** | Cria problemas de mecânica, termodinâmica, eletromagnetismo |
| **Química** | Elabora questões sobre tabela periódica, reações, estequiometria |
| **Revisor** | Valida questões pedagogicamente |
| **Classificador** | Categoriza questões por dificuldade e tópico |
| **Imagens** | Gera diagramas e gráficos automaticamente |
| **Persistência** | Armazena questões no PostgreSQL |

---

## 📌 Exemplo de Uso (API)

### Gerar uma questão simples

```python
from backend.main_crewai import gerar_questao_simples

questao = gerar_questao_simples(
    materia="matematica",
    topico="algebra",
    com_diagrama=True
)
print(questao)
```

### Gerar uma prova completa

```python
from backend.main_crewai import gerar_prova_completa

prova = gerar_prova_completa({
    "materia": "fisica",
    "topico": "cinematica",
    "num_questoes": 10,
    "dificuldade": "medio",
    "tipo": "multipla_escolha"
})
```

### Via API REST

```bash
# Gerar questão
curl -X POST http://localhost:5000/api/questao \
  -H "Content-Type: application/json" \
  -d '{"materia": "matematica", "topico": "algebra"}'

# Gerar prova
curl -X POST http://localhost:5000/api/prova \
  -H "Content-Type: application/json" \
  -d '{"materia": "fisica", "quantidade": 5}'
```

---

## 🧪 Executando Testes

```bash
# Com Docker
.\script.ps1 test       # Windows
./script.sh test        # Linux/Mac

# Local
python -m pytest tests/ -v
```

---

## 📋 Variáveis de Ambiente

Copie `env.template` para `.env` e configure:

```bash
# Flask
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta

# Banco de Dados
DATABASE_URL=postgresql://user:password@db:5432/provas_db
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=provas_db

# Diagramas
DIAGRAMAS_DIR=static/diagramas
DIAGRAMAS_DPI=150

# Logs
LOG_LEVEL=INFO
LOG_DIR=logs
```

---

## 🗺️ Roadmap

Consulte o arquivo `PROGRESSO.txt` para ver o status detalhado de todas as funcionalidades planejadas:

- [x] Agentes base (Matemática, Física, Química)
- [x] Sistema de provas com PDF ABNT
- [x] Geração de diagramas
- [ ] Autenticação JWT
- [ ] Multi-tenancy (corporações)
- [ ] Frontend React
- [ ] E-commerce (planos pagos)
- [ ] Painel Admin

---

## 📄 Licença

MIT License - Consulte o arquivo [LICENSE](LICENSE) para detalhes.

---

## 👨‍💻 Autor

Desenvolvido com ❤️ por **Flavio Godoy** | 2025

[![GitHub](https://img.shields.io/badge/GitHub-Profile-black)](https://github.com/seu-usuario)
