import os
from crewai import Crew, Process, Task
from backend.agents.matematica import AgenteMatematica
from backend.agents.fisica import AgenteFisica
from backend.agents.quimica import AgenteQuimica
from backend.agents.revisor import AgenteRevisor
from backend.agents.classificador import AgenteClassificador
from backend.utils.logger import log_questao_gerada


# Criar diretório para diagramas se não existir
DIAGRAMAS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "diagramas")
os.makedirs(DIAGRAMAS_DIR, exist_ok=True)


def obter_agente_por_materia(materia: str):
    """
    Retorna o agente apropriado baseado na matéria.
    
    Args:
        materia: Nome da matéria (fisica, quimica, matematica)
    
    Returns:
        Tupla (instância do agente, agent CrewAI)
    """
    agentes = {
        "fisica": AgenteFisica,
        "quimica": AgenteQuimica,
        "matematica": AgenteMatematica
    }
    
    if materia not in agentes:
        raise ValueError(f"Matéria '{materia}' não suportada. Opções: {list(agentes.keys())}")
    
    instancia = agentes[materia]()
    return instancia, instancia.agent


def gerar_questao_simples(materia: str, topico: str = None, com_diagrama: bool = False) -> dict:
    """
    Gera uma questão simples usando o agente específico da matéria.
    
    Args:
        materia: Nome da matéria (fisica, quimica, matematica)
        topico: Tópico específico (opcional)
        com_diagrama: Se True, gera diagrama junto com a questão
    
    Returns:
        Dicionário com enunciado, resposta, tipo e opcionalmente diagrama
    """
    instancia, _ = obter_agente_por_materia(materia)
    
    # Chama o método apropriado baseado na matéria
    if materia == "fisica":
        topico_lower = (topico or "mru").lower()
        questao = instancia.gerar_questao(topico_lower, com_diagrama)
    elif materia == "quimica":
        topico_lower = (topico or "tabela_periodica").lower()
        questao = instancia.gerar_questao(topico_lower, com_diagrama)
    elif materia == "matematica":
        questao = instancia.gerar_questao(topico or "algebra", com_diagrama)
    
    # Adiciona matéria se não existir
    if "materia" not in questao:
        questao["materia"] = materia
    
    return questao


def gerar_prova_completa(requisitos: dict) -> dict:
    """
    Gera uma prova completa usando o fluxo de agentes CrewAI.
    Inclui classificação, geração, e revisão.
    
    Args:
        requisitos: Dicionário com:
            - materia: str (fisica, quimica, matematica)
            - topico: str (opcional)
            - num_questoes: int (padrão: 1)
            - dificuldade: str (facil, medio, dificil - opcional)
            - com_diagrama: bool (se True, gera diagrama)
    
    Returns:
        Questão gerada e validada com tags de classificação
    """
    materia = requisitos.get("materia", "matematica")
    topico = requisitos.get("topico", "geral")
    num_questoes = requisitos.get("num_questoes", 1)
    dificuldade = requisitos.get("dificuldade", "medio")
    com_diagrama = requisitos.get("com_diagrama", False)
    
    # Classificação automática do tópico
    classificador = AgenteClassificador()
    tags = classificador.classificar(topico)
    tags["dificuldade_solicitada"] = dificuldade
    
    # Obtém o agente apropriado
    instancia, agente_crewai = obter_agente_por_materia(materia)
    
    # Cria a tarefa para o CrewAI
    tarefa = Task(
        description=f"""
        Crie {num_questoes} questão(ões) de {materia.upper()} sobre o tópico: {topico}.
        Nível de dificuldade: {dificuldade}.
        
        A questão deve conter:
        1. Enunciado claro e bem formulado
        2. Resposta correta
        3. Explicação do raciocínio (opcional)
        """,
        agent=agente_crewai,
        expected_output="Questão formatada com enunciado, resposta e tipo"
    )
    
    # Executa o Crew
    crew = Crew(
        agents=[agente_crewai],
        tasks=[tarefa],
        process=Process.sequential,
        verbose=True
    )
    
    try:
        resultado_crew = crew.kickoff()
        
        # Processa o resultado do CrewAI
        if isinstance(resultado_crew, dict):
            questao_gerada = resultado_crew
        else:
            # Se o resultado for string, usa o método simples como fallback
            questao_gerada = gerar_questao_simples(materia, topico, com_diagrama)
    except Exception as e:
        # Fallback: usa geração simples se o CrewAI falhar
        print(f"CrewAI falhou, usando geração simples: {e}")
        questao_gerada = gerar_questao_simples(materia, topico, com_diagrama)
    
    # Revisão da questão
    revisor = AgenteRevisor()
    enunciado = questao_gerada.get("enunciado", "")
    resposta = questao_gerada.get("resposta", "")
    
    if not revisor.validar_questao(enunciado, resposta):
        # Se falhar na revisão, tenta gerar novamente
        print("Questão reprovada na revisão, gerando nova questão...")
        questao_gerada = gerar_questao_simples(materia, topico, com_diagrama)
    
    # Adiciona metadados
    questao_gerada["tags"] = tags
    questao_gerada["materia"] = materia
    questao_gerada["dificuldade"] = dificuldade
    
    # Log da geração
    log_questao_gerada(materia)
    
    return questao_gerada


def gerar_multiplas_questoes(materia: str, topico: str, quantidade: int, 
                             dificuldade: str = "medio", com_diagrama: bool = False) -> list:
    """
    Gera múltiplas questões de uma matéria.
    
    Args:
        materia: Nome da matéria
        topico: Tópico das questões
        quantidade: Número de questões a gerar
        dificuldade: Nível de dificuldade
        com_diagrama: Se True, gera diagramas para as questões
    
    Returns:
        Lista de questões geradas
    """
    questoes = []
    
    for i in range(quantidade):
        requisitos = {
            "materia": materia,
            "topico": topico,
            "num_questoes": 1,
            "dificuldade": dificuldade,
            "com_diagrama": com_diagrama
        }
        
        try:
            questao = gerar_prova_completa(requisitos)
            questao["numero"] = i + 1
            questoes.append(questao)
        except Exception as e:
            print(f"Erro ao gerar questão {i + 1}: {e}")
            # Tenta geração simples como fallback
            try:
                questao = gerar_questao_simples(materia, topico, com_diagrama)
                questao["numero"] = i + 1
                questoes.append(questao)
            except:
                continue
    
    return questoes


def gerar_questao_com_diagrama(materia: str, topico: str = None) -> dict:
    """
    Gera uma questão com diagrama obrigatório.
    
    Args:
        materia: Nome da matéria
        topico: Tópico da questão
    
    Returns:
        Questão com diagrama incluído
    """
    return gerar_questao_simples(materia, topico, com_diagrama=True)
