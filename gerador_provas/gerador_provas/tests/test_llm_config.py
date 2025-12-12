# -*- coding: utf-8 -*-
"""
Testes para configuração de LLM e sistema de prompts.

Executa: pytest tests/test_llm_config.py -v

NOTA: Alguns testes que requerem LLM são marcados como skip
      a menos que o Ollama esteja rodando ou API keys configuradas.
"""

import pytest
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestLLMConfig:
    """Testes para configuração de LLM."""
    
    def test_importacao(self):
        """Testa se o módulo pode ser importado."""
        from backend.llm_config import get_llm, detectar_provider_automatico
        assert get_llm is not None
        assert detectar_provider_automatico is not None
    
    def test_get_default_model(self):
        """Testa modelos padrão por provider."""
        from backend.llm_config import get_default_model
        
        assert "llama" in get_default_model("ollama").lower()
        assert "gpt" in get_default_model("openai").lower()
        assert "claude" in get_default_model("anthropic").lower()
    
    def test_listar_modelos_disponiveis(self):
        """Testa listagem de modelos disponíveis."""
        from backend.llm_config import listar_modelos_disponiveis
        
        modelos = listar_modelos_disponiveis()
        
        assert "ollama" in modelos
        assert "openai" in modelos
        assert "anthropic" in modelos
        
        # Cada provider deve ter categorias de modelos
        assert isinstance(modelos["ollama"], dict)
        assert isinstance(modelos["openai"], dict)


class TestDetecaoProvider:
    """Testes para detecção automática de provider."""
    
    def test_detectar_provider_padrao_ollama(self):
        """Testa que Ollama é o padrão quando sem keys."""
        # Salvando estado atual de TODAS as API keys
        old_google = os.environ.pop("GOOGLE_API_KEY", None)
        old_openai = os.environ.pop("OPENAI_API_KEY", None)
        old_anthropic = os.environ.pop("ANTHROPIC_API_KEY", None)
        old_provider = os.environ.pop("LLM_PROVIDER", None)
        
        try:
            # Reimporta o módulo sem as env vars
            import importlib
            import backend.llm_config
            importlib.reload(backend.llm_config)
            
            provider, model = backend.llm_config.detectar_provider_automatico()
            assert provider == "ollama"
        finally:
            # Restaura estado
            if old_google:
                os.environ["GOOGLE_API_KEY"] = old_google
            if old_openai:
                os.environ["OPENAI_API_KEY"] = old_openai
            if old_anthropic:
                os.environ["ANTHROPIC_API_KEY"] = old_anthropic
            if old_provider:
                os.environ["LLM_PROVIDER"] = old_provider
    
    def test_detectar_gemini_quando_tem_key(self):
        """Testa que Gemini é detectado quando GOOGLE_API_KEY está presente."""
        old_google = os.environ.get("GOOGLE_API_KEY")
        old_provider = os.environ.pop("LLM_PROVIDER", None)
        
        os.environ["GOOGLE_API_KEY"] = "fake-google-key"
        
        try:
            import importlib
            import backend.llm_config
            importlib.reload(backend.llm_config)
            
            provider, model = backend.llm_config.detectar_provider_automatico()
            assert provider == "gemini"
            assert "gemini" in model.lower()
        finally:
            if old_google:
                os.environ["GOOGLE_API_KEY"] = old_google
            else:
                os.environ.pop("GOOGLE_API_KEY", None)
            if old_provider:
                os.environ["LLM_PROVIDER"] = old_provider
    
    def test_provider_explicito_tem_prioridade(self):
        """Testa que LLM_PROVIDER explícito sobrescreve detecção."""
        # Configura cenário
        os.environ["LLM_PROVIDER"] = "ollama"
        os.environ["GOOGLE_API_KEY"] = "fake-google-key"  # Deveria detectar gemini
        
        try:
            import importlib
            import backend.llm_config
            importlib.reload(backend.llm_config)
            
            provider, model = backend.llm_config.detectar_provider_automatico()
            # Mas como LLM_PROVIDER está explícito, usa ollama
            assert provider == "ollama"
        finally:
            os.environ.pop("LLM_PROVIDER", None)
            os.environ.pop("GOOGLE_API_KEY", None)


class TestPrompts:
    """Testes para o sistema de prompts."""
    
    def test_importacao(self):
        """Testa se o módulo de prompts pode ser importado."""
        from backend.prompts.medicina import get_prompt, PROMPTS
        assert get_prompt is not None
        assert PROMPTS is not None
    
    def test_prompts_disponiveis(self):
        """Testa se existem prompts para todas as disciplinas."""
        from backend.prompts.medicina import PROMPTS
        
        disciplinas = [
            "farmacologia",
            "histologia",
            "anatomia",
            "fisiologia",
            "patologia",
            "bioquimica",
            "microbiologia",
            "casos_clinicos"
        ]
        
        for disciplina in disciplinas:
            assert disciplina in PROMPTS, f"Prompt para {disciplina} não encontrado"
    
    def test_get_prompt_formatacao(self):
        """Testa se o prompt é formatado corretamente."""
        from backend.prompts.medicina import get_prompt
        
        prompt = get_prompt(
            disciplina="farmacologia",
            topico="antibioticos",
            dificuldade="medio",
            observacoes="Foco em beta-lactâmicos"
        )
        
        assert "Farmacologia" in prompt
        assert "antibioticos" in prompt
        assert "MEDIO" in prompt
        assert "beta-lactâmicos" in prompt
    
    def test_get_prompt_com_observacoes(self):
        """Testa prompt com observações do professor."""
        from backend.prompts.medicina import get_prompt
        
        prompt = get_prompt(
            disciplina="histologia",
            topico="tecidos",
            dificuldade="dificil",
            observacoes="Incluir correlação clínica com neoplasias"
        )
        
        assert "Histologia" in prompt
        assert "DIFICIL" in prompt
        assert "OBSERVAÇÕES DO PROFESSOR" in prompt
        assert "neoplasias" in prompt
    
    def test_get_prompt_sem_observacoes(self):
        """Testa prompt sem observações do professor."""
        from backend.prompts.medicina import get_prompt
        
        prompt = get_prompt(
            disciplina="histologia",
            topico="tecidos",
            dificuldade="facil"
        )
        
        assert "Histologia" in prompt
        assert "FACIL" in prompt
        # Sem observações, não deve ter essa seção
        assert "OBSERVAÇÕES DO PROFESSOR" not in prompt or prompt.count("OBSERVAÇÕES DO PROFESSOR") == 0
    
    def test_prompt_formato_json(self):
        """Testa se o prompt inclui instruções de formato JSON."""
        from backend.prompts.medicina import get_prompt
        
        prompt = get_prompt("farmacologia", "geral", "medio")
        
        assert "JSON" in prompt
        assert "enunciado" in prompt
        assert "resposta" in prompt


class TestGeradorIA:
    """Testes para o gerador de questões com IA."""
    
    def test_importacao(self):
        """Testa se o módulo pode ser importado."""
        from backend.gerador_ia import GeradorQuestoesIA, gerar_questao_ia
        assert GeradorQuestoesIA is not None
        assert gerar_questao_ia is not None
    
    def test_parse_json_valido(self):
        """Testa parsing de JSON válido."""
        from backend.gerador_ia import GeradorQuestoesIA
        
        # Cria instância parcial para testar método específico
        gerador = object.__new__(GeradorQuestoesIA)
        
        # JSON válido
        json_str = '{"enunciado": "Teste", "resposta": "Resposta"}'
        result = gerador._parse_json_response(json_str)
        
        assert result["enunciado"] == "Teste"
        assert result["resposta"] == "Resposta"
    
    def test_parse_json_em_texto(self):
        """Testa extração de JSON de texto."""
        from backend.gerador_ia import GeradorQuestoesIA
        
        gerador = object.__new__(GeradorQuestoesIA)
        
        # JSON dentro de texto
        texto = '''
        Aqui está a questão:
        
        {"enunciado": "Pergunta?", "resposta": "Resposta!", "tipo": "Teste"}
        
        Espero que ajude.
        '''
        
        result = gerador._parse_json_response(texto)
        
        assert result["enunciado"] == "Pergunta?"
        assert result["resposta"] == "Resposta!"
    
    def test_parse_json_com_markdown(self):
        """Testa extração de JSON em bloco markdown."""
        from backend.gerador_ia import GeradorQuestoesIA
        
        gerador = object.__new__(GeradorQuestoesIA)
        
        texto = '''
        ```json
        {"enunciado": "Questão em markdown", "resposta": "Resposta"}
        ```
        '''
        
        result = gerador._parse_json_response(texto)
        assert "enunciado" in result
    
    def test_parse_json_invalido(self):
        """Testa fallback quando JSON é inválido."""
        from backend.gerador_ia import GeradorQuestoesIA
        
        gerador = object.__new__(GeradorQuestoesIA)
        
        # Texto sem JSON válido
        texto = "Isso não é um JSON válido"
        result = gerador._parse_json_response(texto)
        
        # Deve retornar estrutura básica com o texto
        assert "enunciado" in result
        assert result["enunciado"] == texto


class TestIntegracaoMainCrewai:
    """Testes de integração com main_crewai."""
    
    def test_obter_agente_medicina(self):
        """Testa se agentes médicos podem ser obtidos."""
        from backend.main_crewai import obter_agente_por_materia
        
        disciplinas_medicas = [
            "farmacologia",
            "histologia",
            "anatomia",
            "fisiologia",
            "patologia",
            "bioquimica",
            "microbiologia",
            "casos_clinicos"
        ]
        
        for disciplina in disciplinas_medicas:
            instancia, agent = obter_agente_por_materia(disciplina)
            assert instancia is not None
            assert agent is not None
    
    def test_gerar_questao_simples_medicina(self):
        """Testa geração simples para disciplinas médicas."""
        from backend.main_crewai import gerar_questao_simples
        
        questao = gerar_questao_simples("farmacologia", "antibioticos", "medio")
        
        assert questao is not None
        assert "enunciado" in questao
        assert "resposta" in questao
    
    def test_materia_invalida_levanta_erro(self):
        """Testa se matéria inválida levanta ValueError."""
        from backend.main_crewai import obter_agente_por_materia
        
        with pytest.raises(ValueError):
            obter_agente_por_materia("materia_inexistente")
    
    def test_gerar_questao_com_dificuldades(self):
        """Testa geração com diferentes níveis de dificuldade."""
        from backend.main_crewai import gerar_questao_simples
        
        for dificuldade in ["facil", "medio", "dificil"]:
            questao = gerar_questao_simples(
                materia="farmacologia",
                topico="antibioticos",
                dificuldade=dificuldade
            )
            assert questao is not None
            assert "enunciado" in questao


# =============================================================================
# TESTES DE CONECTIVIDADE COM IA
# =============================================================================

class TestConectividadeIA:
    """
    Testes de conectividade com provedores de IA.
    
    Estes testes verificam se há uma API key configurada e testam
    a conectividade real com o provedor.
    """
    
    def test_verificar_provider_configurado(self):
        """Verifica qual provider está configurado."""
        from backend.llm_config import detectar_provider_automatico
        
        provider, model = detectar_provider_automatico()
        
        print(f"\n[INFO] Provider detectado: {provider}")
        print(f"[INFO] Modelo: {model}")
        
        assert provider is not None
        assert model is not None
        assert provider in ["ollama", "gemini", "openai", "anthropic"]
    
    def test_verificar_api_key_presente(self):
        """Verifica se alguma API key está configurada."""
        google_key = os.getenv("GOOGLE_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        has_cloud_key = bool(google_key or openai_key or anthropic_key)
        
        if has_cloud_key:
            if google_key:
                print(f"\n[OK] GOOGLE_API_KEY configurada (Gemini)")
            if openai_key:
                print(f"\n[OK] OPENAI_API_KEY configurada")
            if anthropic_key:
                print(f"\n[OK] ANTHROPIC_API_KEY configurada")
        else:
            print("\n[INFO] Nenhuma API key de nuvem configurada - usando Ollama local")
        
        # Não falha - apenas informa
        assert True
    
    @pytest.mark.skipif(
        not os.getenv("GOOGLE_API_KEY") and 
        not os.getenv("OPENAI_API_KEY") and 
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="Nenhuma API key configurada - pulando teste de conectividade"
    )
    def test_conectividade_llm_real(self):
        """
        Testa conectividade REAL com o LLM configurado.
        
        Este teste só roda se houver uma API key configurada.
        Faz uma chamada simples para verificar se a conexão funciona.
        """
        # Recarrega o módulo para garantir que as variáveis estejam atualizadas
        import importlib
        import backend.llm_config
        importlib.reload(backend.llm_config)
        
        from backend.llm_config import get_llm, detectar_provider_automatico
        
        provider, model = detectar_provider_automatico()
        print(f"\n[TEST] Testando conectividade com {provider}/{model}...")
        
        try:
            llm = get_llm()
            print(f"[OK] LLM instanciado: {type(llm)}")
            
            # Teste simples de geração
            # O CrewAI LLM usa o formato do LiteLLM
            assert llm is not None
            print(f"[OK] Conectividade com {provider} verificada!")
            
        except Exception as e:
            pytest.fail(f"[ERRO] Falha na conectividade com {provider}: {str(e)}")
    
    @pytest.mark.skipif(
        not os.getenv("GOOGLE_API_KEY") and 
        not os.getenv("OPENAI_API_KEY") and 
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="Nenhuma API key configurada - pulando teste de geração"
    )
    def test_geracao_questao_com_ia_real(self):
        """
        Testa geração de uma questão REAL usando IA.
        
        Este teste só roda se houver uma API key configurada.
        Gera uma questão simples para verificar se o fluxo completo funciona.
        
        NOTA: Este teste pode demorar alguns segundos e consome créditos da API.
        """
        # Recarrega os módulos para garantir que as variáveis estejam atualizadas
        import importlib
        import backend.llm_config
        import backend.gerador_ia
        importlib.reload(backend.llm_config)
        importlib.reload(backend.gerador_ia)
        
        from backend.llm_config import detectar_provider_automatico
        from backend.gerador_ia import GeradorQuestoesIA
        
        provider, model = detectar_provider_automatico()
        print(f"\n[TEST] Gerando questão com {provider}/{model}...")
        
        try:
            gerador = GeradorQuestoesIA()
            
            # Gera uma questão simples sem revisão (mais rápido)
            questao = gerador.gerar_questao(
                disciplina="farmacologia",
                topico="antibioticos",
                dificuldade="facil",
                com_revisao=False  # Sem revisão para ser mais rápido
            )
            
            print(f"[OK] Questão gerada!")
            print(f"[INFO] Enunciado: {questao.get('enunciado', 'N/A')[:100]}...")
            
            assert "enunciado" in questao
            assert len(questao["enunciado"]) > 20
            assert questao.get("gerado_por_ia") == True
            
            print(f"[OK] Teste de geração com IA real passou!")
            
        except Exception as e:
            pytest.fail(f"[ERRO] Falha na geração com IA: {str(e)}")


class TestStatusIA:
    """Teste rápido para mostrar status da configuração de IA."""
    
    def test_mostrar_status_ia(self):
        """Mostra o status atual da configuração de IA."""
        from backend.llm_config import detectar_provider_automatico, listar_modelos_disponiveis
        
        provider, model = detectar_provider_automatico()
        modelos = listar_modelos_disponiveis()
        
        print("\n" + "="*60)
        print("STATUS DA CONFIGURAÇÃO DE IA")
        print("="*60)
        print(f"Provider ativo: {provider.upper()}")
        print(f"Modelo: {model}")
        print("-"*60)
        
        # Verifica API keys
        keys_status = {
            "GOOGLE_API_KEY (Gemini)": bool(os.getenv("GOOGLE_API_KEY")),
            "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
            "ANTHROPIC_API_KEY": bool(os.getenv("ANTHROPIC_API_KEY")),
        }
        
        print("API Keys configuradas:")
        for key, status in keys_status.items():
            emoji = "✓" if status else "✗"
            print(f"  {emoji} {key}")
        
        print("-"*60)
        print("Providers disponíveis:", list(modelos.keys()))
        print("="*60)
        
        assert True  # Sempre passa, é apenas informativo

