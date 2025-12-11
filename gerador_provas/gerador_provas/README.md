# 📚 Gerador de Provas com CrewAI

Sistema inteligente de geração automática de provas e questões utilizando **CrewAI** (framework de agentes de IA), com interface web Flask e persistência em PostgreSQL.

---

## 🎯 Visão Geral

O **Gerador de Provas** utiliza múltiplos agentes de IA especializados para criar questões de diferentes matérias (Física, Química, Matemática), validá-las pedagogicamente e armazená-las em um banco de dados.

### Funcionalidades Principais

- ✅ Geração de questões de **Física** (MRU, termodinâmica)
- ✅ Geração de questões de **Química** (tabela periódica, ligações)
- ✅ Geração de questões de **Matemática** (álgebra, geometria)
- ✅ **Validação automática** de respostas usando SymPy
- ✅ **Classificação** por tópico e dificuldade
- ✅ **Persistência** em PostgreSQL
- ✅ **Exportação** para PDF (PyLaTeX)
- ✅ **Dashboard** com gráficos (Plotly)

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Flask)                      │
│                    templates/index.html                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      app.py (Rotas)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   main_crewai.py (Orquestrador)              │
│                        CrewAI Crew                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│  Agente   │  │  Agente   │  │  Agente   │
│  Física   │  │  Química  │  │Matemática │
└───────────┘  └───────────┘  └───────────┘
        │             │             │
        └─────────────┼─────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agente Revisor                            │
│               (Validação Pedagógica)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 Agente Persistência                          │
│                    PostgreSQL                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 Agentes CrewAI

| Agente | Função | Tecnologias |
|--------|--------|-------------|
| **AgenteFisica** | Gera questões de mecânica e termodinâmica | SymPy |
| **AgenteQuimica** | Gera questões de química | RDKit |
| **AgenteMatematica** | Gera questões de álgebra e geometria | SymPy |
| **AgenteRevisor** | Valida precisão e clareza das questões | Custom Tools |
| **AgenteClassificador** | Categoriza por tópico e dificuldade | - |
| **AgenteImagens** | Gera diagramas para questões | Matplotlib (futuro) |
| **AgentePersistencia** | Armazena no banco de dados | SQLAlchemy |

---

## 📦 Instalação

### Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Git

### Passos

1. **Clone o repositório:**
```bash
git clone <url-do-repositorio>
cd gerador_provas
```

2. **Crie um ambiente virtual:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Inicie o banco de dados:**
```bash
docker-compose up -d db
```

5. **Execute o script de criação das tabelas:**
```sql
-- Conecte ao PostgreSQL e execute o conteúdo de populate-script.txt
```

6. **Inicie a aplicação:**
```bash
python app.py
```

7. **Acesse no navegador:**
```
http://localhost:5000
```

---

## 🐳 Usando Docker (Recomendado)

```bash
# Inicia todos os serviços
docker-compose up --build

# Para parar
docker-compose down
```

---

## 📁 Estrutura do Projeto

```
gerador_provas/
├── app.py                      # Aplicação Flask
├── Dockerfile                  # Configuração Docker
├── docker-compose.yml          # Orquestração de containers
├── requirements.txt            # Dependências Python
├── PROGRESSO.txt              # Acompanhamento do projeto
├── README.md                   # Este arquivo
│
├── backend/
│   ├── main_crewai.py         # Orquestrador CrewAI
│   │
│   ├── agents/                 # Agentes de IA
│   │   ├── classificador.py
│   │   ├── fisica.py
│   │   ├── imagens.py
│   │   ├── matematica.py
│   │   ├── persistencia.py
│   │   ├── quimica.py
│   │   └── revisor.py
│   │
│   └── utils/                  # Utilitários
│       ├── dashboard.py
│       ├── latex_generator.py
│       ├── logger.py
│       └── validator.py
│
└── templates/                  # Templates HTML
    ├── index.html
    ├── questao.html
    └── resultado.html
```

---

## 🔧 Configuração

### Variáveis de Ambiente (futuro .env)

```env
DATABASE_URL=postgresql://user:password@db:5432/provas_db
FLASK_ENV=development
FLASK_DEBUG=True
OPENAI_API_KEY=sua-chave-aqui  # Se usar LLM
```

### Banco de Dados

O schema do banco está em `populate-script.txt`:

- **questoes**: id, materia, topico, enunciado, dificuldade, data_criacao
- **resolucoes**: id, questao_id, solucao, explicacao, data_criacao

---

## 🚀 Uso

### Via Interface Web

1. Acesse `http://localhost:5000`
2. Selecione a matéria desejada
3. Clique em "Gerar Questão"
4. Visualize a questão gerada

### Via Código Python

```python
from backend.agents.fisica import AgenteFisica
from backend.agents.matematica import AgenteMatematica

# Gerar questão de Física
fisica = AgenteFisica()
questao = fisica.gerar_questao_mru()
print(questao)

# Gerar questão de Matemática
matematica = AgenteMatematica()
questao = matematica.gerar_questao("algebra")
print(questao)
```

---

## 📊 Dashboard

O dashboard de métricas está disponível em `utils/dashboard.py`:

```python
from backend.utils.dashboard import gerar_grafico_acertos

# Gera gráfico de questões por tópico
gerar_grafico_acertos()
# Output: output/dashboard.html
```

---

## 📄 Exportação

### PDF

```python
from backend.utils.latex_generator import gerar_pdf

questoes = [
    {"enunciado": "Questão 1..."},
    {"enunciado": "Questão 2..."}
]
gerar_pdf(questoes, "output/prova.pdf")
```

---

## 🧪 Testes (Em Desenvolvimento)

```bash
# Executar testes
pytest tests/

# Com cobertura
pytest --cov=backend tests/
```

---

## 📝 Acompanhamento do Projeto

Veja o arquivo **`PROGRESSO.txt`** para:
- Status de cada funcionalidade
- Bugs corrigidos
- Próximos passos planejados

---

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📜 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

## 👨‍💻 Autores

- Desenvolvido com CrewAI e Flask

---

## 📞 Suporte

Para dúvidas ou sugestões, abra uma issue no repositório.

