from crewai import Crew, Process
from agents.matematica import AgenteMatematica
from agents.revisor import AgenteRevisor
from agents.classificador import AgenteClassificador

def gerar_prova(requisitos):
    # Classificação automática
    classificador = AgenteClassificador()
    tags = classificador.classificar(requisitos["topico"])
    
    # Geração da questão
    agente_matematica = AgenteMatematica().agent
    tarefa = Task(
        description=f"Crie {requisitos['num_questoes']} questões sobre {requisitos['topico']}.",
        agent=agente_matematica
    )
    
    # Revisão
    revisor = AgenteRevisor()
    questao_gerada = Crew(agents=[agente_matematica], tasks=[tarefa]).kickoff()
    if not revisor.validar_questao(questao_gerada["enunciado"], questao_gerada["resposta"]):
        raise ValueError("Questão reprovada na revisão!")
    
    return questao_gerada
