"""
Repositório base e utilitários de conexão com banco de dados.
"""

import os
import sys
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

# Importar configurações
try:
    from config import settings
    DATABASE_URL = settings.DATABASE_URL
except ImportError:
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/provas_db'
    )

# Engine global (singleton)
_engine = None


def get_db_engine():
    """
    Retorna a engine do banco de dados (singleton).
    """
    global _engine
    if _engine is None:
        _engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True  # Verifica conexão antes de usar
        )
    return _engine


def get_session() -> Session:
    """
    Cria uma nova sessão do banco de dados.
    """
    engine = get_db_engine()
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


@contextmanager
def get_db_session():
    """
    Context manager para sessão do banco de dados.
    Garante commit/rollback e fechamento da sessão.
    
    Usage:
        with get_db_session() as session:
            session.execute(...)
    """
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class BaseRepository:
    """
    Repositório base com métodos comuns de CRUD.
    """
    
    def __init__(self, schema: str = "provas"):
        self.engine = get_db_engine()
        self.schema = schema
    
    def execute_query(self, query: str, params: dict = None) -> List[Dict]:
        """
        Executa uma query SELECT e retorna os resultados.
        """
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
    
    def execute_insert(self, query: str, params: dict) -> Optional[str]:
        """
        Executa uma query INSERT e retorna o ID inserido.
        """
        with self.engine.connect() as conn:
            result = conn.execute(text(query + " RETURNING id"), params)
            conn.commit()
            row = result.fetchone()
            return str(row[0]) if row else None
    
    def execute_update(self, query: str, params: dict) -> int:
        """
        Executa uma query UPDATE e retorna o número de linhas afetadas.
        """
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params)
            conn.commit()
            return result.rowcount
    
    def execute_delete(self, query: str, params: dict) -> int:
        """
        Executa uma query DELETE e retorna o número de linhas afetadas.
        """
        return self.execute_update(query, params)
    
    def health_check(self) -> bool:
        """
        Verifica se a conexão com o banco está funcionando.
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

