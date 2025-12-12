"""
Módulo principal de orquestração CrewAI.

Coordena os agentes para geração de questões e provas.
"""

import os
from crewai import Crew, Task

# Agentes de ciências básicas
from backend.agents.matematica import AgenteMatematica
from backend.agents.fisica import AgenteFisica
from backend.agents.quimica import AgenteQuimica
from backend.agents.biologia import AgenteBiologia
from backend.agents.revisor import AgenteRevisor
from backend.agents.classificador import AgenteClassificador

# Agentes de Medicina
from backend.agents.medicina.farmacologia import AgenteFarmacologia
from backend.agents.medicina.histologia import AgenteHistologia
from backend.agents.medicina.anatomia import AgenteAnatomia
from backend.agents.medicina.fisiologia import AgenteFisiologia
from backend.agents.medicina.patologia import AgentePatologia
from backend.agents.medicina.bioquimica import AgenteBioquimica
from backend.agents.medicina.microbiologia import AgenteMicrobiologia
from backend.agents.medicina.casos_clinicos import AgenteCasosClinico

from backend.utils.logger import log_questao_gerada


# Criar diretório para diagramas se não existir
DIAGRAMAS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "diagramas")
os.makedirs(DIAGRAMAS_DIR, exist_ok=True)


def obter_agente_por_materia(materia: str):
    """
    Retorna o agente apropriado baseado na matéria.
    
    Args:
        materia: Nome da matéria (fisica, quimica, matematica, biologia, farmacologia, etc.)
    
    Returns:
        Tupla (instância do agente, agent CrewAI)
    """
    agentes = {
        # Ciências básicas
        "fisica": AgenteFisica,
        "quimica": AgenteQuimica,
        "matematica": AgenteMatematica,
        "biologia": AgenteBiologia,
        # Medicina
        "farmacologia": AgenteFarmacologia,
        "histologia": AgenteHistologia,
        "anatomia": AgenteAnatomia,
        "fisiologia": AgenteFisiologia,
        "patologia": AgentePatologia,
        "bioquimica": AgenteBioquimica,
        "microbiologia": AgenteMicrobiologia,
        "casos_clinicos": AgenteCasosClinico,
    }
    
    if materia not in agentes:
        raise ValueError(f"Matéria '{materia}' não suportada. Opções: {list(agentes.keys())}")
    
    instancia = agentes[materia]()
    return instancia, instancia.agent


def gerar_questao_simples(materia: str, topico: str = None, dificuldade: str = "medio",
                          com_diagrama: bool = False, observacoes: str = "") -> dict:
    """
    Gera uma questão simples usando o agente específico da matéria.
    
    Args:
        materia: Nome da matéria (fisica, quimica, matematica, biologia, farmacologia, etc.)
        topico: Tópico específico (opcional)
        dificuldade: Nível de dificuldade (facil, medio, dificil)
        com_diagrama: Se True, gera diagrama junto com a questão
        observacoes: Observações do professor para direcionar a questão
    
    Returns:
        Dicionário com enunciado, resposta, tipo e opcionalmente diagrama
    """
    instancia, _ = obter_agente_por_materia(materia)
    
    # Chama o método apropriado baseado na matéria
    topico_lower = (topico or "geral").lower()
    
    # Matérias que suportam diagrama
    materias_com_diagrama = ["fisica", "quimica", "matematica", "biologia"]
    
    if materia in materias_com_diagrama:
        questao = instancia.gerar_questao(topico_lower, dificuldade, com_diagrama)
    else:
        # Matérias médicas usam observacoes ao invés de com_diagrama
        questao = instancia.gerar_questao(topico_lower, dificuldade, observacoes)
    
    # Adiciona metadados se não existirem
    if "materia" not in questao:
        questao["materia"] = materia
    if "dificuldade" not in questao:
        questao["dificuldade"] = dificuldade
    
    return questao


def gerar_prova_completa(requisitos: dict) -> dict:
    """
    Gera uma prova completa usando o fluxo de agentes CrewAI.
    Inclui classificação, geração, e revisão.
    
    Args:
        requisitos: Dicionário com:
            - materia: str (fisica, quimica, matematica, biologia)
            - topico: str (opcional)
            - num_questoes: int (padrão: 1)
            - dificuldade: str (facil, medio, dificil)
            - com_diagrama: bool (se True, gera diagrama)
    
    Returns:
        Questão gerada e validada com tags de classificação
    """
    materia = requisitos.get("materia", "matematica")
    topico = requisitos.get("topico", "geral")
    dificuldade = requisitos.get("dificuldade", "medio")
    com_diagrama = requisitos.get("com_diagrama", False)
    
    # Classificação automática do tópico
    classificador = AgenteClassificador()
    tags = classificador.classificar(topico)
    tags["dificuldade_solicitada"] = dificuldade
    
    # Gera a questão com dificuldade especificada
    questao_gerada = gerar_questao_simples(materia, topico, dificuldade, com_diagrama)
    
    # Revisão da questão
    revisor = AgenteRevisor()
    enunciado = questao_gerada.get("enunciado", "")
    resposta = questao_gerada.get("resposta", "")
    
    if not revisor.validar_questao(enunciado, resposta):
        # Se falhar na revisão, tenta gerar novamente
        print("Questão reprovada na revisão, gerando nova questão...")
        questao_gerada = gerar_questao_simples(materia, topico, dificuldade, com_diagrama)
    
    # Adiciona metadados
    questao_gerada["tags"] = tags
    questao_gerada["materia"] = materia
    questao_gerada["dificuldade"] = dificuldade
    
    # Log da geração
    log_questao_gerada(materia)
    
    return questao_gerada


def gerar_com_crewai(materia: str, topico: str, dificuldade: str = "medio") -> dict:
    """
    Gera questão usando CrewAI com LLM (requer OPENAI_API_KEY configurada).
    
    Args:
        materia: Nome da matéria
        topico: Tópico da questão
        dificuldade: Nível de dificuldade
    
    Returns:
        Questão gerada pelo CrewAI
    """
    instancia, agente_crewai = obter_agente_por_materia(materia)
    
    # Cria a tarefa para o CrewAI
    tarefa = Task(
        description=f"""
        Crie uma questão de {materia.upper()} sobre o tópico: {topico}.
        Nível de dificuldade: {dificuldade}.
        
        A questão deve conter:
        1. Enunciado claro e bem formulado
        2. Resposta correta com explicação detalhada
        3. Nível compatível com ensino médio/vestibular
        4. Se dificuldade for 'dificil', incluir múltiplas etapas de resolução
        """,
        agent=agente_crewai,
        expected_output="Questão formatada com enunciado e resposta detalhada"
    )
    
    # Executa o Crew
    crew = Crew(
        agents=[agente_crewai],
        tasks=[tarefa],
        verbose=True
    )
    
    try:
        resultado = crew.kickoff()
        return {
            "enunciado": str(resultado),
            "resposta": "Gerado via CrewAI",
            "materia": materia,
            "topico": topico,
            "dificuldade": dificuldade,
            "fonte": "crewai"
        }
    except Exception as e:
        print(f"Erro no CrewAI: {e}")
        # Fallback para geração simples
        return gerar_questao_simples(materia, topico, dificuldade)


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
                questao = gerar_questao_simples(materia, topico, dificuldade, com_diagrama)
                questao["numero"] = i + 1
                questoes.append(questao)
            except:
                continue
    
    return questoes


def gerar_questao_com_diagrama(materia: str, topico: str = None, dificuldade: str = "medio") -> dict:
    """
    Gera uma questão com diagrama obrigatório.
    
    Args:
        materia: Nome da matéria
        topico: Tópico da questão
        dificuldade: Nível de dificuldade
    
    Returns:
        Questão com diagrama incluído
    """
    return gerar_questao_simples(materia, topico, dificuldade, com_diagrama=True)


# Listar matérias disponíveis
MATERIAS_DISPONIVEIS = ["fisica", "quimica", "matematica", "biologia"]
