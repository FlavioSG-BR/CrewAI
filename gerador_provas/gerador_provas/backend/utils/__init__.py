"""
Utilitários do Gerador de Provas.

Módulos:
- logger: Sistema de logging
- validator: Validação de respostas matemáticas
- latex_generator: Geração de PDFs simples
- prova_pdf_generator: Geração de provas ABNT com gabarito
- dashboard: Gráficos e métricas
"""

from backend.utils.logger import log_questao_gerada, get_logger
from backend.utils.validator import validar_resposta
from backend.utils.latex_generator import gerar_pdf
from backend.utils.prova_pdf_generator import ProvaPDFGenerator
from backend.utils.dashboard import gerar_grafico_acertos

__all__ = [
    'log_questao_gerada',
    'get_logger',
    'validar_resposta',
    'gerar_pdf',
    'ProvaPDFGenerator',
    'gerar_grafico_acertos'
]

