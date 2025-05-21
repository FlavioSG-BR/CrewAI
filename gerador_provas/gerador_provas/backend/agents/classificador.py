from crewai import Agent

class AgenteClassificador:
    def __init__(self):
        self.agent = Agent(
            role="Classificador de Questões",
            goal="Categorizar questões por tópico e dificuldade",
            backstory="Expert em taxonomia educacional",
            allow_delegation=False
        )

    def classificar(self, texto: str) -> dict:
        return {"topico": "Mecânica", "dificuldade": "Médio"}
