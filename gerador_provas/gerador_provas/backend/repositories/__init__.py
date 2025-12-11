"""
Repositórios para acesso ao banco de dados.

Implementa o padrão Repository para abstrair o acesso aos dados.
"""

from backend.repositories.base import BaseRepository, get_db_engine
from backend.repositories.questao_repository import QuestaoRepository
from backend.repositories.prova_repository import ProvaRepository

__all__ = [
    'BaseRepository',
    'get_db_engine',
    'QuestaoRepository',
    'ProvaRepository'
]

