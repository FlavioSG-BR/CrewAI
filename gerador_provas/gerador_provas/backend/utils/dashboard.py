import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine

def gerar_grafico_acertos():
    engine = create_engine("postgresql://user:password@localhost:5432/provas_db")
    df = pd.read_sql("SELECT topico, COUNT(*) as total FROM questoes GROUP BY topico", engine)
    fig = px.pie(df, values="total", names="topico", title="Questões por Tópico")
    fig.write_html("output/dashboard.html")
