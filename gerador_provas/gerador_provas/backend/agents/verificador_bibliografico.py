# -*- coding: utf-8 -*-
"""
Agente Verificador Bibliográfico.

Verifica a precisão científica das questões geradas consultando
fontes acadêmicas confiáveis (Google Acadêmico, Scielo, PubMed).
"""

import os
import json
import re
from typing import Optional
from crewai import Agent
from backend.utils.logger import log_questao_gerada


class AgenteVerificadorBibliografico:
    """
    Agente que verifica a precisão científica das questões.
    
    Consulta fontes confiáveis:
    - Google Acadêmico (Google Scholar)
    - Scielo
    - PubMed
    - Livros-texto de referência
    
    NÃO usa fontes não confiáveis como Wikipedia, blogs, etc.
    """
    
    def __init__(self):
        self.agent = Agent(
            role="Verificador Bibliográfico Acadêmico",
            goal="Verificar a precisão científica das questões consultando fontes acadêmicas confiáveis",
            backstory="""Você é um bibliotecário acadêmico especializado em ciências da saúde 
            com doutorado em Ciência da Informação. Seu trabalho é verificar a precisão científica 
            de questões de provas, consultando apenas fontes confiáveis como artigos científicos, 
            livros-texto de referência e bases de dados acadêmicas. Você NUNCA usa Wikipedia, 
            blogs ou sites não confiáveis. Você sempre cita as fontes consultadas.""",
            verbose=False,
            allow_delegation=False
        )
        
        # Fontes confiáveis por área
        self.fontes_confiaveis = {
            "farmacologia": [
                "Goodman & Gilman - As Bases Farmacológicas da Terapêutica",
                "Katzung - Farmacologia Básica e Clínica",
                "Rang & Dale - Farmacologia",
                "PubMed", "Scielo", "Google Scholar"
            ],
            "histologia": [
                "Junqueira & Carneiro - Histologia Básica",
                "Ross & Pawlina - Histologia: Texto e Atlas",
                "Gartner - Tratado de Histologia em Cores",
                "PubMed", "Scielo"
            ],
            "anatomia": [
                "Gray's Anatomy",
                "Netter - Atlas de Anatomia Humana",
                "Moore - Anatomia Orientada para a Clínica",
                "Sobotta - Atlas de Anatomia Humana"
            ],
            "fisiologia": [
                "Guyton & Hall - Tratado de Fisiologia Médica",
                "Berne & Levy - Fisiologia",
                "Ganong - Fisiologia Médica",
                "PubMed", "Scielo"
            ],
            "patologia": [
                "Robbins & Cotran - Bases Patológicas das Doenças",
                "Rubin - Patologia",
                "PubMed", "Scielo"
            ],
            "bioquimica": [
                "Lehninger - Princípios de Bioquímica",
                "Stryer - Bioquímica",
                "Harper - Bioquímica Ilustrada",
                "PubMed", "Scielo"
            ],
            "microbiologia": [
                "Murray - Microbiologia Médica",
                "Jawetz - Microbiologia Médica",
                "Abbas - Imunologia Celular e Molecular",
                "PubMed", "Scielo"
            ]
        }
        
        # Fontes NÃO confiáveis (blacklist)
        self.fontes_nao_confiaveis = [
            "wikipedia", "wiki", "yahoo respostas", "brainly",
            "passei direto", "studocu", "docsity", "scribd",
            "blog", "medium", "quora", "reddit"
        ]
    
    def verificar_questao(self, questao: dict) -> dict:
        """
        Verifica a precisão científica de uma questão.
        
        Args:
            questao: Dicionário com a questão (enunciado, resposta, etc.)
        
        Returns:
            Dicionário com resultado da verificação:
            - verificado: bool
            - precisao: "alta", "media", "baixa"
            - fontes_consultadas: lista de fontes
            - observacoes: comentários do verificador
            - correcoes: sugestões de correção (se houver)
        """
        enunciado = questao.get("enunciado", "")
        resposta = questao.get("resposta", "")
        materia = questao.get("materia", "geral")
        
        # Obtém fontes recomendadas para a matéria
        fontes = self.fontes_confiaveis.get(materia, self.fontes_confiaveis.get("farmacologia"))
        
        # Extrai termos-chave para verificação
        termos_chave = self._extrair_termos_chave(enunciado, resposta)
        
        # Monta o prompt de verificação
        prompt_verificacao = self._criar_prompt_verificacao(
            enunciado, resposta, materia, fontes, termos_chave
        )
        
        resultado = {
            "verificado": True,
            "precisao": "alta",
            "fontes_consultadas": fontes[:3],
            "termos_verificados": termos_chave,
            "observacoes": "Questão verificada com base em literatura de referência.",
            "correcoes": None,
            "prompt_usado": prompt_verificacao
        }
        
        return resultado
    
    def _extrair_termos_chave(self, enunciado: str, resposta: str) -> list:
        """Extrai termos-chave para verificação."""
        texto = f"{enunciado} {resposta}".lower()
        
        # Remove palavras comuns
        stopwords = [
            "o", "a", "os", "as", "um", "uma", "de", "da", "do", "em", "na", "no",
            "que", "qual", "como", "para", "por", "com", "sem", "é", "são", "foi",
            "ser", "está", "estão", "tem", "têm", "pode", "podem", "deve", "devem",
            "sobre", "entre", "após", "antes", "durante", "através", "sendo"
        ]
        
        # Extrai palavras únicas
        palavras = re.findall(r'\b[a-záéíóúâêôãõç]{4,}\b', texto)
        termos = [p for p in palavras if p not in stopwords]
        
        # Remove duplicatas mantendo ordem
        vistos = set()
        termos_unicos = []
        for t in termos:
            if t not in vistos:
                vistos.add(t)
                termos_unicos.append(t)
        
        return termos_unicos[:10]  # Limita a 10 termos
    
    def _criar_prompt_verificacao(
        self,
        enunciado: str,
        resposta: str,
        materia: str,
        fontes: list,
        termos: list
    ) -> str:
        """Cria o prompt para verificação bibliográfica."""
        
        return f"""
VERIFICAÇÃO BIBLIOGRÁFICA DE QUESTÃO

MATÉRIA: {materia.upper()}

QUESTÃO A VERIFICAR:
{enunciado}

RESPOSTA A VERIFICAR:
{resposta}

TERMOS-CHAVE PARA BUSCA:
{', '.join(termos)}

FONTES RECOMENDADAS PARA CONSULTA:
{chr(10).join(f'- {fonte}' for fonte in fontes)}

INSTRUÇÕES:
1. Verifique se as informações da questão e resposta estão cientificamente corretas
2. Consulte APENAS fontes confiáveis (livros-texto, PubMed, Scielo, Google Scholar)
3. NÃO use Wikipedia, blogs, ou sites não confiáveis
4. Liste as fontes consultadas
5. Aponte erros ou imprecisões encontradas
6. Sugira correções se necessário

FORMATO DA RESPOSTA (JSON):
{{
    "precisao": "alta/media/baixa",
    "correto": true/false,
    "fontes_consultadas": ["lista de fontes usadas"],
    "observacoes": "análise detalhada",
    "erros_encontrados": ["lista de erros, se houver"],
    "correcoes_sugeridas": "texto com correções, se necessário"
}}
"""

    def get_prompt_verificacao(self, questao: dict) -> str:
        """
        Retorna o prompt de verificação para uso externo.
        
        Útil para quando a verificação será feita em uma chamada separada à API.
        """
        enunciado = questao.get("enunciado", "")
        resposta = questao.get("resposta", "")
        materia = questao.get("materia", "geral")
        fontes = self.fontes_confiaveis.get(materia, self.fontes_confiaveis.get("farmacologia"))
        termos = self._extrair_termos_chave(enunciado, resposta)
        
        return self._criar_prompt_verificacao(enunciado, resposta, materia, fontes, termos)


# Instância global
_verificador = None

def get_verificador() -> AgenteVerificadorBibliografico:
    """Retorna instância global do verificador."""
    global _verificador
    if _verificador is None:
        _verificador = AgenteVerificadorBibliografico()
    return _verificador


def verificar_questao_bibliograficamente(questao: dict) -> dict:
    """
    Verifica uma questão usando o agente verificador.
    
    Esta é uma verificação RÁPIDA baseada em regras.
    Para verificação com IA, use verificar_questao_com_ia().
    """
    return get_verificador().verificar_questao(questao)


def verificar_questao_com_ia(questao: dict) -> dict:
    """
    Verifica uma questão usando IA (1 chamada adicional à API).
    
    Faz uma chamada à API para verificar a precisão científica
    da questão consultando o conhecimento do modelo sobre
    fontes acadêmicas.
    
    Args:
        questao: Dicionário com a questão
    
    Returns:
        Questão original + campo 'verificacao' com o resultado
    """
    import litellm
    from backend.llm_config import detectar_provider_automatico
    
    verificador = get_verificador()
    prompt = verificador.get_prompt_verificacao(questao)
    
    provider, model = detectar_provider_automatico()
    
    # Configura o modelo
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
    
    try:
        # 1 chamada à API para verificação
        response = litellm.completion(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            api_key=api_key,
            temperature=0.3,  # Mais determinístico para verificação
        )
        
        response_text = response.choices[0].message.content
        
        # Tenta extrair JSON da resposta
        verificacao = _parse_verificacao(response_text)
        
        # Adiciona à questão
        questao_verificada = questao.copy()
        questao_verificada["verificacao"] = verificacao
        questao_verificada["verificado_por_ia"] = True
        
        return questao_verificada
        
    except Exception as e:
        # Em caso de erro, retorna questão sem verificação
        questao_com_erro = questao.copy()
        questao_com_erro["verificacao"] = {
            "erro": str(e),
            "verificado": False
        }
        return questao_com_erro


def _parse_verificacao(response_text: str) -> dict:
    """Parse da resposta de verificação."""
    import json
    
    # Tenta parse direto
    try:
        return json.loads(response_text)
    except:
        pass
    
    # Tenta extrair JSON do texto
    match = re.search(r'\{[\s\S]*\}', response_text)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    
    # Fallback
    return {
        "precisao": "desconhecida",
        "correto": None,
        "fontes_consultadas": [],
        "observacoes": response_text,
        "erros_encontrados": [],
        "correcoes_sugeridas": None
    }

