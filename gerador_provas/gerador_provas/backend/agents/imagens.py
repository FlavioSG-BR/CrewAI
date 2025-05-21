from crewai import Agent

class AgenteImagens:
    def __init__(self):
        self.agent = Agent(
            role="Gerador de Diagramas",
            goal="Criar imagens para questões de Física/Química",
            backstory="Especialista em visualização científica",
            tools=[self._tool_gerador_imagens]
        )
        self._tool_gerador_imagens = Tool(
            name="GeradorImagens",
            func=self.gerar_diagrama,
            description="Gera diagramas a partir de descrições textuais"
        )

    def gerar_diagrama(self, descricao: str) -> str:
        return "caminho/para/diagrama.png"
