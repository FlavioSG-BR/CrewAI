"""
Dashboard e geração de gráficos de métricas.

Usa Plotly para visualizações interativas.
"""

import os
import sys
from typing import Optional, Dict, List

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Tentar importar configurações
try:
    from config import settings
    OUTPUT_DIR = settings.OUTPUT_DIR
    DATABASE_URL = settings.DATABASE_URL
except ImportError:
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'output')
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/provas_db')

# Criar diretório de output se não existir
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _get_engine():
    """Obtém a engine do banco de dados."""
    from sqlalchemy import create_engine
    return create_engine(DATABASE_URL)


def gerar_grafico_acertos(caminho_saida: str = None) -> str:
    """
    Gera gráfico de questões por tópico.
    
    Args:
        caminho_saida: Caminho para salvar o HTML
    
    Returns:
        Caminho do arquivo gerado
    """
    if caminho_saida is None:
        caminho_saida = os.path.join(OUTPUT_DIR, "dashboard.html")
    
    try:
        engine = _get_engine()
        
        query = """
            SELECT t.nome as topico, COUNT(*) as total 
            FROM provas.questoes q
            LEFT JOIN provas.topicos t ON q.topico_id = t.id
            WHERE q.deleted_at IS NULL
            GROUP BY t.nome
            ORDER BY total DESC
        """
        
        df = pd.read_sql(query, engine)
        
        if df.empty:
            # Dados de exemplo se não houver dados reais
            df = pd.DataFrame({
                'topico': ['MRU', 'MRUV', 'Álgebra', 'Geometria', 'Tabela Periódica'],
                'total': [10, 8, 15, 12, 7]
            })
        
        fig = px.pie(
            df, 
            values="total", 
            names="topico", 
            title="Questões por Tópico",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_layout(
            font_family="Arial",
            title_font_size=20
        )
        
        fig.write_html(caminho_saida)
        return caminho_saida
        
    except Exception as e:
        print(f"Erro ao gerar gráfico: {e}")
        return None


def gerar_dashboard_completo(caminho_saida: str = None) -> str:
    """
    Gera dashboard completo com múltiplos gráficos.
    
    Args:
        caminho_saida: Caminho para salvar o HTML
    
    Returns:
        Caminho do arquivo gerado
    """
    if caminho_saida is None:
        caminho_saida = os.path.join(OUTPUT_DIR, "dashboard_completo.html")
    
    try:
        engine = _get_engine()
        
        # Query para questões por matéria
        query_materias = """
            SELECT m.nome as materia, COUNT(*) as total 
            FROM provas.questoes q
            JOIN provas.materias m ON q.materia_id = m.id
            WHERE q.deleted_at IS NULL
            GROUP BY m.nome
        """
        
        # Query para questões por dificuldade
        query_dificuldade = """
            SELECT dificuldade, COUNT(*) as total 
            FROM provas.questoes 
            WHERE deleted_at IS NULL
            GROUP BY dificuldade
        """
        
        # Query para questões por dia
        query_diario = """
            SELECT DATE(created_at) as data, COUNT(*) as total 
            FROM provas.questoes 
            WHERE deleted_at IS NULL AND created_at > CURRENT_DATE - INTERVAL '30 days'
            GROUP BY DATE(created_at)
            ORDER BY data
        """
        
        df_materias = pd.read_sql(query_materias, engine)
        df_dificuldade = pd.read_sql(query_dificuldade, engine)
        df_diario = pd.read_sql(query_diario, engine)
        
        # Criar subplots
        fig = make_subplots(
            rows=2, cols=2,
            specs=[
                [{"type": "pie"}, {"type": "bar"}],
                [{"type": "scatter", "colspan": 2}, None]
            ],
            subplot_titles=(
                "Questões por Matéria",
                "Questões por Dificuldade",
                "Questões Geradas por Dia"
            )
        )
        
        # Gráfico de pizza - Matérias
        if not df_materias.empty:
            fig.add_trace(
                go.Pie(labels=df_materias['materia'], values=df_materias['total'], hole=0.3),
                row=1, col=1
            )
        
        # Gráfico de barras - Dificuldade
        if not df_dificuldade.empty:
            colors = {'facil': 'green', 'medio': 'orange', 'dificil': 'red'}
            fig.add_trace(
                go.Bar(
                    x=df_dificuldade['dificuldade'],
                    y=df_dificuldade['total'],
                    marker_color=[colors.get(d, 'blue') for d in df_dificuldade['dificuldade']]
                ),
                row=1, col=2
            )
        
        # Gráfico de linha - Questões por dia
        if not df_diario.empty:
            fig.add_trace(
                go.Scatter(
                    x=df_diario['data'],
                    y=df_diario['total'],
                    mode='lines+markers',
                    line=dict(color='royalblue', width=2)
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text="Dashboard - Gerador de Provas",
            title_font_size=24,
            font_family="Arial"
        )
        
        fig.write_html(caminho_saida)
        return caminho_saida
        
    except Exception as e:
        print(f"Erro ao gerar dashboard: {e}")
        return None


def obter_estatisticas() -> Dict:
    """
    Obtém estatísticas gerais do sistema.
    
    Returns:
        Dicionário com estatísticas
    """
    try:
        engine = _get_engine()
        
        stats = {}
        
        # Total de questões
        query = "SELECT COUNT(*) FROM provas.questoes WHERE deleted_at IS NULL"
        result = pd.read_sql(query, engine)
        stats['total_questoes'] = int(result.iloc[0, 0])
        
        # Total de provas
        query = "SELECT COUNT(*) FROM provas.provas WHERE deleted_at IS NULL"
        result = pd.read_sql(query, engine)
        stats['total_provas'] = int(result.iloc[0, 0])
        
        # Total de diagramas
        query = "SELECT COUNT(*) FROM provas.diagramas"
        result = pd.read_sql(query, engine)
        stats['total_diagramas'] = int(result.iloc[0, 0])
        
        return stats
        
    except Exception as e:
        return {"erro": str(e)}
