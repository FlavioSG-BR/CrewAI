"""
Agentes CrewAI para geração de questões.

Agentes disponíveis:
- AgenteFisica: Questões de física (mecânica, termodinâmica, ondulatória, eletricidade)
- AgenteQuimica: Questões de química (tabela periódica, ligações, reações)
- AgenteMatematica: Questões de matemática (álgebra, geometria, funções)
- AgenteBiologia: Questões de biologia (farmacologia, anatomia, genética, ecologia)
- AgenteRevisor: Revisão e validação de questões
- AgenteClassificador: Classificação por tópico e dificuldade
- AgenteImagens: Geração de diagramas
- AgentePersistencia: Salvamento no banco de dados
"""

from backend.agents.fisica import AgenteFisica
from backend.agents.quimica import AgenteQuimica
from backend.agents.matematica import AgenteMatematica
from backend.agents.biologia import AgenteBiologia
from backend.agents.revisor import AgenteRevisor
from backend.agents.classificador import AgenteClassificador
from backend.agents.imagens import AgenteImagens
from backend.agents.persistencia import AgentePersistencia

__all__ = [
    'AgenteFisica',
    'AgenteQuimica', 
    'AgenteMatematica',
    'AgenteBiologia',
    'AgenteRevisor',
    'AgenteClassificador',
    'AgenteImagens',
    'AgentePersistencia'
]

