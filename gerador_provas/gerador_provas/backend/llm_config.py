# -*- coding: utf-8 -*-
"""
Configuração de LLM para o Gerador de Provas.

Suporta:
- Ollama (local, gratuito)
- OpenAI (API)
- Anthropic Claude (API)
- Outros providers compatíveis com LiteLLM

DETECÇÃO AUTOMÁTICA:
- Se OPENAI_API_KEY está configurada → usa OpenAI
- Se ANTHROPIC_API_KEY está configurada → usa Anthropic
- Senão → usa Ollama local
"""

import os
from typing import Optional
from crewai import LLM


def detectar_provider_automatico() -> tuple[str, str]:
    """
    Detecta automaticamente qual provider usar baseado nas API keys configuradas.
    
    Prioridade:
    1. LLM_PROVIDER explícito no .env
    2. OPENAI_API_KEY presente → openai
    3. ANTHROPIC_API_KEY presente → anthropic
    4. Fallback → ollama
    
    Returns:
        Tupla (provider, model)
    """
    # Se o usuário especificou explicitamente, usa isso
    explicit_provider = os.getenv("LLM_PROVIDER", "").lower()
    explicit_model = os.getenv("LLM_MODEL", "")
    
    if explicit_provider and explicit_provider != "auto":
        return explicit_provider, explicit_model or get_default_model(explicit_provider)
    
    # Detecção automática baseada nas API keys
    if os.getenv("OPENAI_API_KEY"):
        return "openai", explicit_model or "gpt-4o-mini"
    
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic", explicit_model or "claude-3-sonnet-20240229"
    
    # Fallback para Ollama local
    return "ollama", explicit_model or "llama3.2"


def get_default_model(provider: str) -> str:
    """Retorna o modelo padrão para cada provider."""
    defaults = {
        "ollama": "llama3.2",
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-sonnet-20240229",
    }
    return defaults.get(provider.lower(), "llama3.2")


def get_llm(
    provider: str = None,
    model: str = None,
    temperature: float = 0.7,
    base_url: str = None
) -> LLM:
    """
    Retorna uma instância de LLM configurada.
    
    DETECÇÃO AUTOMÁTICA:
    Se provider não for especificado, detecta automaticamente:
    - OPENAI_API_KEY presente → usa OpenAI
    - ANTHROPIC_API_KEY presente → usa Anthropic
    - Senão → usa Ollama local
    
    Args:
        provider: Provider do LLM (ollama, openai, anthropic, ou None para auto)
        model: Nome do modelo
        temperature: Temperatura para geração (0.0 a 1.0)
        base_url: URL base para APIs locais (Ollama)
    
    Returns:
        Instância de LLM configurada
    
    Exemplos:
        # Detecção automática (recomendado)
        llm = get_llm()
        
        # Forçar Ollama local
        llm = get_llm(provider="ollama", model="llama3.2")
        
        # Forçar OpenAI
        llm = get_llm(provider="openai", model="gpt-4")
    """
    
    # Detecta automaticamente se não especificado
    if provider is None:
        provider, detected_model = detectar_provider_automatico()
        model = model or detected_model
    else:
        model = model or os.getenv("LLM_MODEL") or get_default_model(provider)
    
    base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Configuração por provider
    if provider.lower() == "ollama":
        return LLM(
            model=f"ollama/{model}",
            base_url=base_url,
            temperature=temperature,
        )
    
    elif provider.lower() == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY não configurada!")
        return LLM(
            model=f"openai/{model}",
            api_key=api_key,
            temperature=temperature,
        )
    
    elif provider.lower() == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY não configurada!")
        return LLM(
            model=f"anthropic/{model}",
            api_key=api_key,
            temperature=temperature,
        )
    
    else:
        # Tenta usar o formato direto do LiteLLM
        return LLM(
            model=model,
            base_url=base_url,
            temperature=temperature,
        )


def get_default_llm() -> LLM:
    """Retorna o LLM padrão configurado no ambiente."""
    return get_llm()


# Modelos recomendados por provider
MODELOS_RECOMENDADOS = {
    "ollama": {
        "leves": ["llama3.2", "mistral", "phi3"],
        "medios": ["llama3.1:8b", "codellama", "gemma2"],
        "pesados": ["llama3.1:70b", "mixtral", "qwen2.5:32b"],
        "medicina": ["meditron", "medllama2"],  # Modelos especializados em medicina
    },
    "openai": {
        "rapidos": ["gpt-4o-mini", "gpt-3.5-turbo"],
        "potentes": ["gpt-4o", "gpt-4-turbo"],
    },
    "anthropic": {
        "rapidos": ["claude-3-haiku-20240307"],
        "balanceados": ["claude-3-sonnet-20240229"],
        "potentes": ["claude-3-opus-20240229", "claude-3-5-sonnet-20241022"],
    }
}


def listar_modelos_disponiveis() -> dict:
    """Retorna lista de modelos recomendados por provider."""
    return MODELOS_RECOMENDADOS

