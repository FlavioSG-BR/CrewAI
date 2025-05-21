from crewai import Agent, Task
from sympy import symbols, Eq, solve

class AgenteFisica:
    def __init__(self):
        self.agent = Agent(
            role="Professor de Física",
            goal="Criar questões sobre mecânica, termodinâmica e ondulatória",
            backstory="Doutor em Física com experiência em Olimpíadas Científicas",
            allow_delegation=False
        )

    def gerar_questao_mru(self) -> dict:
        """Gera questão sobre Movimento Retilíneo Uniforme"""
        v, t = symbols('v t')
        distancia = v * t
        enunciado = f"Um objeto se move com velocidade constante de {v} m/s. Calcule a distância percorrida em {t} segundos."
        resposta = solve(Eq(distancia, 100))[0]  # Exemplo simplificado
        
        return {
            "enunciado": enunciado,
            "resposta": f"d = {resposta} metros",
            "tipo": "MRU"
        }
