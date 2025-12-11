"""
Serviços de negócio do Gerador de Provas.

Camada que coordena agentes e repositórios.
"""

from backend.services.questao_service import QuestaoService
from backend.services.prova_service import ProvaService, ConfiguracaoProva, criar_prova
from backend.services.alternativas_generator import AlternativasGenerator

__all__ = [
    'QuestaoService',
    'ProvaService',
    'ConfiguracaoProva',
    'criar_prova',
    'AlternativasGenerator'
]

