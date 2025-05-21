from crewai import Agent
from rdkit import Chem

class AgenteQuimica:
    def __init__(self):
        self.agent = Agent(
            role="Professor de Química",
            goal="Elaborar questões sobre tabela periódica, ligações e reações",
            backstory="Especialista em Química Orgânica com 10 anos de ensino",
            allow_delegation=False
        )

    def gerar_questao_tabela_periodica(self) -> dict:
        """Gera questão sobre elementos químicos"""
        enunciado = "Qual o número atômico do Oxigênio?"
        return {
            "enunciado": enunciado,
            "resposta": "8",
            "tipo": "Tabela Periódica"
        }
