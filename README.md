# Gerador de Provas Automatizado com CrewAI

![CrewAI + Flask](https://img.shields.io/badge/Powered%20by-CrewAI%20%2B%20Flask-blueviolet)

Um sistema inteligente para criação de provas personalizadas de **Matemática, Física e Química**, utilizando agentes de IA especializados.

## 🚀 Funcionalidades Principais

- **Geração automática de questões** por matéria/tópico
- **Validação especializada**:
  - Matemática: Verificação de equações com SymPy
  - Física: Checagem de unidades e fórmulas
  - Química: Validação de fórmulas com RDKit
- **Exportação para**:
  - PDF (com ReportLab)
  - LaTeX (para editores acadêmicos)
- **Dashboard de métricas** com Plotly

## 🛠️ Como Usar

### Pré-requisitos
- Python 3.11+
- Docker (opcional)
- PostgreSQL (para armazenamento)

### Instalação Local
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/gerador-provas.git
cd gerador-provas

# Instale as dependências
pip install -r requirements.txt

# Execute o Flask
python app.py
```

### Com Docker

```bash
docker-compose up -d
Acesse: http://localhost:5000
```

🧩 Estrutura do Projeto
gerador_provas/
├── backend/          # Lógica de IA e banco de dados
├── frontend/         # Interface web (Flask)
├── output/           # Provas geradas
├── templates/        # HTML da interface
└── agents/           # Agentes especializados
    ├── matematica.py
    ├── fisica.py
    └── quimica.py
🤖 Agentes Implementados
Agente	Função
Matemática	Gera questões de álgebra, geometria, cálculo
Física	Cria problemas de mecânica, termodinâmica
Química	Elabora questões sobre tabela periódica, reações
Revisor	Valida questões pedagogicamente
Persistência	Armazena questões no PostgreSQL
📌 Exemplo de Uso
python
from backend.main_crewai import gerar_prova

prova = gerar_prova({
    "materia": "fisica",
    "topico": "movimento_uniforme", 
    "num_questoes": 5
})
📄 Licença
MIT License - Consulte o arquivo LICENSE para detalhes.

Desenvolvido com ❤️ por Flavio Godoy | 2025