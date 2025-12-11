"""
Backend do Gerador de Provas.

Módulos:
- agents: Agentes CrewAI para geração de questões
- utils: Utilitários (logger, validator, etc.)
- services: Serviços de negócio
- repositories: Acesso ao banco de dados
"""

from backend.main_crewai import (
    gerar_questao_simples,
    gerar_prova_completa,
    gerar_multiplas_questoes,
    gerar_questao_com_diagrama
)

__all__ = [
    'gerar_questao_simples',
    'gerar_prova_completa', 
    'gerar_multiplas_questoes',
    'gerar_questao_com_diagrama'
]

