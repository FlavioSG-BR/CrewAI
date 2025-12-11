"""
Configurações centralizadas do Gerador de Provas.

Carrega variáveis de ambiente do arquivo .env e fornece valores padrão.
"""

import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()


class Config:
    """Configuração base."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_APP = os.getenv('FLASK_APP', 'app.py')
    
    # Servidor
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Banco de Dados
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/provas_db'
    )
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'user')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'provas_db')
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))
    
    # Diagramas
    DIAGRAMAS_DIR = os.getenv('DIAGRAMAS_DIR', 'static/diagramas')
    DIAGRAMAS_DPI = int(os.getenv('DIAGRAMAS_DPI', 150))
    
    # Logs
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    
    # Exportação
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'output')
    PDF_OUTPUT_DIR = os.getenv('PDF_OUTPUT_DIR', 'output/pdf')
    LATEX_OUTPUT_DIR = os.getenv('LATEX_OUTPUT_DIR', 'output/latex')
    
    # LLM (Opcional)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')


class DevelopmentConfig(Config):
    """Configuração de desenvolvimento."""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Configuração de produção."""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Em produção, exige SECRET_KEY definida
    @property
    def SECRET_KEY(self):
        key = os.getenv('SECRET_KEY')
        if not key:
            raise ValueError("SECRET_KEY deve ser definida em produção!")
        return key


class TestingConfig(Config):
    """Configuração de testes."""
    TESTING = True
    DEBUG = True
    DATABASE_URL = 'sqlite:///:memory:'


# Mapeamento de ambientes
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Retorna a configuração baseada no ambiente."""
    env = os.getenv('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)()


# Instância global de configuração
settings = get_config()

