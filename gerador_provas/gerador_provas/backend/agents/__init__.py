"""
Agentes CrewAI para geração de questões.

Agentes disponíveis:
- AgenteFisica: Questões de física (MRU, MRUV, forças, circuitos)
- AgenteQuimica: Questões de química (tabela periódica, ligações, etc.)
- AgenteMatematica: Questões de matemática (álgebra, geometria, funções)
- AgenteRevisor: Revisão e validação de questões
- AgenteClassificador: Classificação por tópico e dificuldade
- AgenteImagens: Geração de diagramas
- AgentePersistencia: Salvamento no banco de dados
"""

from backend.agents.fisica import AgenteFisica
from backend.agents.quimica import AgenteQuimica
from backend.agents.matematica import AgenteMatematica
from backend.agents.revisor import AgenteRevisor
from backend.agents.classificador import AgenteClassificador
from backend.agents.imagens import AgenteImagens
from backend.agents.persistencia import AgentePersistencia

__all__ = [
    'AgenteFisica',
    'AgenteQuimica', 
    'AgenteMatematica',
    'AgenteRevisor',
    'AgenteClassificador',
    'AgenteImagens',
    'AgentePersistencia'
]

