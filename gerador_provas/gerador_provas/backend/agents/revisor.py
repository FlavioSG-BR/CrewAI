from crewai import Agent, Tool

class AgenteRevisor:
    def __init__(self):
        # Definir a tool ANTES de usar no agent
        self._tool_validacao = Tool(
            name="Validador",
            func=self.validar_questao,
            description="Valida erros conceituais e gramaticais"
        )
        
        self.agent = Agent(
            role="Revisor Pedagógico",
            goal="Validar questões quanto a precisão conceitual e clareza",
            backstory="Especialista em avaliação educacional com 15 anos de experiência",
            tools=[self._tool_validacao]
        )

    def validar_questao(self, enunciado: str, resposta: str) -> bool:
        """Valida uma questão quanto a erros conceituais e gramaticais"""
        # Validações básicas
        if not enunciado or len(enunciado.strip()) == 0:
            return False
        
        if not resposta or len(resposta.strip()) == 0:
            return False
        
        # TODO: Implementar validações mais sofisticadas
        # - Verificar gramática
        # - Verificar coerência matemática com SymPy
        # - Verificar se a resposta está correta
        
        return True
