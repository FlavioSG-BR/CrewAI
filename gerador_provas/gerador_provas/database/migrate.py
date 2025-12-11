"""
Script de Migração do Banco de Dados - Gerador de Provas

Executa as migrações SQL em ordem para criar/atualizar o banco de dados.

Uso:
    python migrate.py --all          # Executa todas as migrações
    python migrate.py --file 001     # Executa migração específica
    python migrate.py --status       # Mostra status das migrações
    python migrate.py --rollback 1   # Reverte última migração (futuro)
"""

import os
import sys
import argparse
import hashlib
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from config import settings
    from sqlalchemy import create_engine, text
except ImportError:
    print("Erro: Não foi possível importar configurações.")
    print("Execute: pip install sqlalchemy python-dotenv")
    sys.exit(1)


# Diretório das migrações
MIGRATIONS_DIR = Path(__file__).parent

# Ordem das migrações
MIGRATIONS_ORDER = [
    "001_schema_base.sql",
    "002_tabelas_dominio.sql",
    "003_tabelas_questoes.sql",
    "004_tabelas_provas.sql",
    "005_tabelas_usuarios.sql",
    "006_tabelas_auditoria.sql",
    "007_indices.sql",
    "008_dados_iniciais.sql",
]


def get_engine():
    """Cria conexão com o banco de dados."""
    return create_engine(settings.DATABASE_URL)


def get_checksum(file_path: Path) -> str:
    """Calcula checksum MD5 do arquivo."""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def get_executed_migrations(engine) -> dict:
    """Retorna migrações já executadas."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT nome, checksum, executada_em FROM provas.migrations ORDER BY executada_em"
            ))
            return {row[0]: {"checksum": row[1], "executada_em": row[2]} for row in result}
    except Exception:
        return {}


def execute_migration(engine, file_name: str, force: bool = False) -> bool:
    """Executa uma migração específica."""
    file_path = MIGRATIONS_DIR / file_name
    
    if not file_path.exists():
        print(f"❌ Arquivo não encontrado: {file_name}")
        return False
    
    executed = get_executed_migrations(engine)
    checksum = get_checksum(file_path)
    
    if file_name in executed and not force:
        if executed[file_name]["checksum"] == checksum:
            print(f"⏭️  Já executada: {file_name}")
            return True
        else:
            print(f"⚠️  Checksum diferente: {file_name}")
            if not force:
                return False
    
    print(f"🔄 Executando: {file_name}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        with engine.connect() as conn:
            # Executar em blocos separados por ;
            for statement in sql.split(';'):
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        conn.execute(text(statement))
                    except Exception as e:
                        if 'already exists' not in str(e).lower():
                            raise
            conn.commit()
        
        print(f"✅ Concluída: {file_name}")
        return True
        
    except Exception as e:
        print(f"❌ Erro em {file_name}: {str(e)}")
        return False


def run_all_migrations(force: bool = False):
    """Executa todas as migrações em ordem."""
    print("=" * 60)
    print("GERADOR DE PROVAS - MIGRAÇÃO DO BANCO DE DADOS")
    print("=" * 60)
    print(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    print("=" * 60)
    
    engine = get_engine()
    success = 0
    errors = 0
    
    for migration in MIGRATIONS_ORDER:
        if execute_migration(engine, migration, force):
            success += 1
        else:
            errors += 1
            if not force:
                print("\n⚠️  Interrompido devido a erro. Use --force para continuar.")
                break
    
    print("=" * 60)
    print(f"Resultado: {success} sucesso, {errors} erros")
    print("=" * 60)
    
    return errors == 0


def show_status():
    """Mostra status das migrações."""
    print("=" * 60)
    print("STATUS DAS MIGRAÇÕES")
    print("=" * 60)
    
    engine = get_engine()
    executed = get_executed_migrations(engine)
    
    for migration in MIGRATIONS_ORDER:
        file_path = MIGRATIONS_DIR / migration
        
        if migration in executed:
            status = "✅"
            info = f"Executada em {executed[migration]['executada_em']}"
        elif file_path.exists():
            status = "⏳"
            info = "Pendente"
        else:
            status = "❓"
            info = "Arquivo não encontrado"
        
        print(f"{status} {migration}: {info}")
    
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Gerenciador de Migrações')
    parser.add_argument('--all', action='store_true', help='Executa todas as migrações')
    parser.add_argument('--file', type=str, help='Executa migração específica')
    parser.add_argument('--status', action='store_true', help='Mostra status das migrações')
    parser.add_argument('--force', action='store_true', help='Força execução mesmo com erros')
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    elif args.all:
        success = run_all_migrations(args.force)
        sys.exit(0 if success else 1)
    elif args.file:
        engine = get_engine()
        # Encontrar arquivo que corresponde
        file_name = None
        for m in MIGRATIONS_ORDER:
            if args.file in m:
                file_name = m
                break
        
        if file_name:
            success = execute_migration(engine, file_name, args.force)
            sys.exit(0 if success else 1)
        else:
            print(f"❌ Migração não encontrada: {args.file}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

