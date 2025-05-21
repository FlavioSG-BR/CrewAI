import logging
from datetime import datetime

logging.basicConfig(
    filename=f"logs/app_{datetime.now().strftime('%Y%m%d')}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_questao_gerada(materia: str):
    logging.info(f"Questão de {materia} gerada com sucesso")
