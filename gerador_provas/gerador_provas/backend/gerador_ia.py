# -*- coding: utf-8 -*-
"""
Gerador de Questões com Inteligência Artificial Real.

Este módulo usa CrewAI com LLM (Ollama/OpenAI/Anthropic) para gerar
questões verdadeiramente originais e contextualizadas.
"""

import json
import re
from typing import Optional
from crewai import Agent, Task, Crew, Process

from backend.llm_config import get_llm, get_default_llm
from backend.prompts.medicina import get_prompt, SYSTEM_PROMPT_PROFESSOR
from backend.utils.logger import log_questao_gerada


class GeradorQuestoesIA:
    """
    Gerador de questões usando IA real (LLM).
    
    Diferente dos agentes template-based, este gerador:
    - Usa LLM para criar questões originais
    - Permite observações do professor
    - Gera conteúdo verdadeiramente novo
    - Suporta Ollama local ou APIs cloud
    """
    
    def __init__(self, llm=None):
        """
        Inicializa o gerador com um LLM específico.
        
        Args:
            llm: Instância de LLM (opcional, usa padrão se não fornecido)
        """
        self.llm = llm or get_default_llm()
        self._setup_agents()
    
    def _setup_agents(self):
        """Configura os agentes CrewAI."""
        
        # Agente Professor - Gera a questão
        self.professor = Agent(
            role="Professor Universitário de Medicina",
            goal="Criar questões de alta qualidade para avaliação de estudantes de medicina",
            backstory="""Você é um professor experiente com mais de 20 anos de docência 
            em cursos de medicina. Especialista em elaboração de provas, você cria questões 
            que avaliam não apenas memorização, mas também raciocínio clínico e aplicação 
            prática do conhecimento. Suas questões são baseadas em evidências científicas 
            atuais e seguem as diretrizes curriculares nacionais.""",
            verbose=False,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Agente Revisor - Revisa a questão
        self.revisor = Agent(
            role="Revisor de Questões Médicas",
            goal="Garantir a qualidade, precisão científica e clareza das questões",
            backstory="""Você é um especialista em avaliação educacional com formação 
            em medicina. Seu papel é revisar questões verificando: precisão científica, 
            clareza do enunciado, adequação do nível de dificuldade, e qualidade das 
            alternativas (quando aplicável). Você também sugere melhorias.""",
            verbose=False,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _parse_json_response(self, response: str) -> dict:
        """
        Extrai JSON da resposta do LLM.
        
        O LLM pode retornar JSON puro ou texto com JSON embutido.
        Esta função tenta extrair o JSON de qualquer formato.
        """
        # Tenta parse direto
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Tenta encontrar JSON no texto
        json_patterns = [
            r'\{[\s\S]*\}',  # Qualquer coisa entre { }
            r'```json\s*([\s\S]*?)\s*```',  # Bloco de código JSON
            r'```\s*([\s\S]*?)\s*```',  # Bloco de código genérico
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response)
            for match in matches:
                try:
                    # Remove possíveis caracteres extras
                    clean = match.strip()
                    if not clean.startswith('{'):
                        continue
                    return json.loads(clean)
                except json.JSONDecodeError:
                    continue
        
        # Se não conseguiu extrair JSON, retorna estrutura básica
        return {
            "enunciado": response,
            "resposta": "Resposta não estruturada - verifique o output.",
            "tipo": "Geral",
            "referencias": [],
            "palavras_chave": []
        }
    
    def gerar_questao(
        self,
        disciplina: str,
        topico: str = "geral",
        dificuldade: str = "medio",
        observacoes: str = "",
        com_revisao: bool = False  # Desabilitado por padrão para economizar API
    ) -> dict:
        """
        Gera uma questão usando IA.
        
        Args:
            disciplina: Nome da disciplina (farmacologia, histologia, etc.)
            topico: Tópico específico
            dificuldade: Nível (facil, medio, dificil)
            observacoes: Instruções específicas do professor
            com_revisao: Se True, a questão passa pelo agente revisor
        
        Returns:
            Dicionário com a questão gerada
        """
        # Obtém o prompt apropriado
        prompt = get_prompt(disciplina, topico, dificuldade, observacoes)
        
        # Task de geração
        task_gerar = Task(
            description=prompt,
            expected_output="""Uma questão em formato JSON com campos:
            - enunciado: texto completo da questão
            - resposta: resposta detalhada
            - tipo: subtópico específico
            - referencias: lista de referências
            - palavras_chave: lista de termos importantes""",
            agent=self.professor
        )
        
        tasks = [task_gerar]
        
        # Task de revisão (opcional)
        if com_revisao:
            task_revisar = Task(
                description="""Revise a questão gerada verificando:
                1. Precisão científica do conteúdo
                2. Clareza e objetividade do enunciado
                3. Adequação ao nível de dificuldade solicitado
                4. Completude da resposta
                
                Se necessário, faça correções e melhorias.
                Retorne a questão final no mesmo formato JSON.""",
                expected_output="Questão revisada e melhorada em formato JSON",
                agent=self.revisor,
                context=[task_gerar]
            )
            tasks.append(task_revisar)
        
        # Executa o Crew
        crew = Crew(
            agents=[self.professor, self.revisor] if com_revisao else [self.professor],
            tasks=tasks,
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        
        # Extrai o resultado
        response_text = str(result.raw) if hasattr(result, 'raw') else str(result)
        questao = self._parse_json_response(response_text)
        
        # Adiciona metadados
        questao["materia"] = disciplina
        questao["dificuldade"] = dificuldade
        questao["topico"] = topico
        questao["gerado_por_ia"] = True
        
        if observacoes:
            questao["observacoes_professor"] = observacoes
        
        log_questao_gerada(disciplina)
        
        return questao
    
    def gerar_multiplas_questoes(
        self,
        disciplina: str,
        quantidade: int = 5,
        topico: str = "geral",
        dificuldade: str = "medio",
        observacoes: str = ""
    ) -> list:
        """
        Gera múltiplas questões sobre um tema.
        
        Args:
            disciplina: Nome da disciplina
            quantidade: Número de questões a gerar
            topico: Tópico específico
            dificuldade: Nível de dificuldade
            observacoes: Instruções do professor
        
        Returns:
            Lista de questões geradas
        """
        prompt = f"""
        {SYSTEM_PROMPT_PROFESSOR}
        
        TAREFA: Gerar {quantidade} questões DIFERENTES sobre {topico} em {disciplina}.
        DIFICULDADE: {dificuldade}
        {f'OBSERVAÇÕES DO PROFESSOR: {observacoes}' if observacoes else ''}
        
        IMPORTANTE: As questões devem ser VARIADAS, cobrindo diferentes aspectos do tema.
        
        FORMATO: Retorne um array JSON com {quantidade} questões, cada uma contendo:
        - enunciado
        - resposta
        - tipo (subtópico específico)
        
        Exemplo de formato:
        [
            {{"enunciado": "...", "resposta": "...", "tipo": "..."}},
            {{"enunciado": "...", "resposta": "...", "tipo": "..."}}
        ]
        """
        
        task = Task(
            description=prompt,
            expected_output=f"Array JSON com {quantidade} questões diferentes",
            agent=self.professor
        )
        
        crew = Crew(
            agents=[self.professor],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        response_text = str(result.raw) if hasattr(result, 'raw') else str(result)
        
        # Tenta extrair array JSON
        try:
            questoes = json.loads(response_text)
            if not isinstance(questoes, list):
                questoes = [questoes]
        except json.JSONDecodeError:
            # Tenta encontrar array no texto
            match = re.search(r'\[[\s\S]*\]', response_text)
            if match:
                try:
                    questoes = json.loads(match.group())
                except:
                    questoes = [{"enunciado": response_text, "resposta": "Ver texto", "tipo": "Geral"}]
            else:
                questoes = [{"enunciado": response_text, "resposta": "Ver texto", "tipo": "Geral"}]
        
        # Adiciona metadados a cada questão
        for q in questoes:
            q["materia"] = disciplina
            q["dificuldade"] = dificuldade
            q["gerado_por_ia"] = True
            log_questao_gerada(disciplina)
        
        return questoes


# =============================================================================
# Geração Direta (1 única chamada - mais eficiente)
# =============================================================================

def gerar_questao_direta(
    disciplina: str,
    topico: str = "geral",
    dificuldade: str = "medio",
    observacoes: str = ""
) -> dict:
    """
    Gera uma questão com 1 ÚNICA chamada à API (mais eficiente).
    
    Esta função NÃO usa CrewAI, faz uma chamada direta ao LLM.
    Ideal para APIs com limite de quota.
    
    Args:
        disciplina: Nome da disciplina
        topico: Tópico específico
        dificuldade: Nível (facil, medio, dificil)
        observacoes: Instruções específicas do professor
    
    Returns:
        Dicionário com a questão gerada
    """
    import litellm
    from backend.llm_config import detectar_provider_automatico
    import os
    
    provider, model = detectar_provider_automatico()
    prompt = get_prompt(disciplina, topico, dificuldade, observacoes)
    
    # Configura o modelo no formato do LiteLLM
    if provider == "gemini":
        model_name = f"gemini/{model}"
        api_key = os.getenv("GOOGLE_API_KEY")
    elif provider == "openai":
        model_name = model
        api_key = os.getenv("OPENAI_API_KEY")
    elif provider == "anthropic":
        model_name = f"anthropic/{model}"
        api_key = os.getenv("ANTHROPIC_API_KEY")
    else:
        model_name = f"ollama/{model}"
        api_key = None
    
    # 1 única chamada à API
    response = litellm.completion(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        api_key=api_key,
        temperature=0.7,
    )
    
    # Extrai a resposta
    response_text = response.choices[0].message.content
    
    # Parse do JSON
    gerador = GeradorQuestoesIA.__new__(GeradorQuestoesIA)
    questao = gerador._parse_json_response(response_text)
    
    # Adiciona metadados
    questao["materia"] = disciplina
    questao["dificuldade"] = dificuldade
    questao["topico"] = topico
    questao["gerado_por_ia"] = True
    
    if observacoes:
        questao["observacoes_professor"] = observacoes
    
    log_questao_gerada(disciplina)
    
    return questao


# =============================================================================
# Funções de conveniência
# =============================================================================

_gerador_global = None

def get_gerador_ia() -> GeradorQuestoesIA:
    """Retorna instância global do gerador (singleton)."""
    global _gerador_global
    if _gerador_global is None:
        _gerador_global = GeradorQuestoesIA()
    return _gerador_global


def gerar_questao_ia(
    disciplina: str,
    topico: str = "geral",
    dificuldade: str = "medio",
    observacoes: str = "",
    verificar_bibliografia: bool = False
) -> dict:
    """
    Gera uma questão com IA.
    
    Args:
        disciplina: Nome da disciplina
        topico: Tópico específico
        dificuldade: Nível (facil, medio, dificil)
        observacoes: Instruções do professor
        verificar_bibliografia: Se True, verifica em fontes acadêmicas (+1 chamada API)
    
    Chamadas à API:
        - Sem verificação: 1 chamada
        - Com verificação: 2 chamadas
    
    Exemplo:
        questao = gerar_questao_ia("farmacologia", "antibioticos", "dificil")
        questao = gerar_questao_ia("farmacologia", "antibioticos", "dificil", verificar_bibliografia=True)
    """
    # Gera a questão (1 chamada)
    questao = gerar_questao_direta(disciplina, topico, dificuldade, observacoes)
    
    # Verifica bibliografia se solicitado (+1 chamada)
    if verificar_bibliografia:
        from backend.agents.verificador_bibliografico import verificar_questao_com_ia
        questao = verificar_questao_com_ia(questao)
    
    return questao


def gerar_multiplas_ia(
    disciplina: str,
    quantidade: int = 5,
    topico: str = "geral",
    dificuldade: str = "medio"
) -> list:
    """Função de conveniência para gerar múltiplas questões."""
    return get_gerador_ia().gerar_multiplas_questoes(disciplina, quantidade, topico, dificuldade)

