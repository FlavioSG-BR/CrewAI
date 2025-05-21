from crewai import Agent

class AgenteMatematica:
    def __init__(self):
        self.agent = Agent(
            role="Professor de Matemática",
            goal="Criar questões de álgebra e geometria.",
            allow_delegation=False
        )
from utils.logger import log_questao_gerada

def gerar_questao(self, topico: str):
    log_questao_gerada("matematica")
