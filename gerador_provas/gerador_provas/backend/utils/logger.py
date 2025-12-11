"""
Sistema de logging centralizado do Gerador de Provas.

Usa configuração do config.py para definir diretórios e níveis.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Tentar importar configurações
try:
    from config import settings
    LOG_DIR = settings.LOG_DIR
    LOG_LEVEL = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
except ImportError:
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    LOG_LEVEL = logging.INFO

# Criar diretório de logs se não existir
os.makedirs(LOG_DIR, exist_ok=True)

# Formato do log
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Configuração global já feita?
_configured = False


def _configure_logging():
    """Configura o logging global."""
    global _configured
    if _configured:
        return
    
    # Arquivo de log do dia
    log_file = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Configurar logging
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    _configured = True


def get_logger(name: str = None) -> logging.Logger:
    """
    Obtém um logger configurado.
    
    Args:
        name: Nome do logger (geralmente __name__)
    
    Returns:
        Logger configurado
    
    Usage:
        logger = get_logger(__name__)
        logger.info("Mensagem")
    """
    _configure_logging()
    return logging.getLogger(name or "gerador_provas")


def log_questao_gerada(materia: str, topico: str = None, sucesso: bool = True):
    """
    Log específico para questões geradas.
    
    Args:
        materia: Nome da matéria
        topico: Tópico da questão
        sucesso: Se a geração foi bem sucedida
    """
    logger = get_logger("questoes")
    
    if sucesso:
        msg = f"Questão de {materia}"
        if topico:
            msg += f" ({topico})"
        msg += " gerada com sucesso"
        logger.info(msg)
    else:
        logger.warning(f"Falha ao gerar questão de {materia}")


def log_prova_criada(titulo: str, num_questoes: int):
    """
    Log específico para provas criadas.
    """
    logger = get_logger("provas")
    logger.info(f"Prova '{titulo}' criada com {num_questoes} questões")


def log_erro(mensagem: str, exc: Exception = None, modulo: str = None):
    """
    Log de erro com informações da exceção.
    
    Args:
        mensagem: Mensagem de erro
        exc: Exceção capturada
        modulo: Nome do módulo
    """
    logger = get_logger(modulo or "erro")
    
    if exc:
        logger.error(f"{mensagem}: {type(exc).__name__} - {str(exc)}")
        logger.debug("Stack trace:", exc_info=True)
    else:
        logger.error(mensagem)


def log_acesso(endpoint: str, metodo: str, ip: str = None, usuario_id: str = None):
    """
    Log de acesso às rotas.
    """
    logger = get_logger("acesso")
    msg = f"{metodo} {endpoint}"
    if ip:
        msg += f" from {ip}"
    if usuario_id:
        msg += f" by user {usuario_id}"
    logger.info(msg)


# Inicializar configuração ao importar
_configure_logging()
