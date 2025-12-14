"""
Testes para o Serviço de Embaralhamento de Questões e Alternativas.

Executa: pytest tests/test_embaralhamento_service.py -v
"""

import pytest
import sys
import os
from collections import Counter

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.services.embaralhamento_service import (
    EmbaralhamentoService,
    ProvaEmbaralhada,
    MapeamentoQuestao,
    MapeamentoAlternativas,
    TipoQuestao
)


class TestEmbaralhamentoBasico:
    """Testes básicos do serviço de embaralhamento."""
    
    @pytest.fixture
    def service(self):
        """Fixture com serviço com seed fixa para reprodutibilidade."""
        return EmbaralhamentoService(seed=42)
    
    @pytest.fixture
    def questoes_exemplo(self):
        """Fixture com questões de exemplo."""
        return [
            {
                "id": "q1",
                "enunciado": "Questão 1 sobre MRU",
                "resposta": "10 m/s",
                "alternativas": [
                    {"letra": "A", "texto": "10 m/s", "correta": True},
                    {"letra": "B", "texto": "20 m/s", "correta": False},
                    {"letra": "C", "texto": "5 m/s", "correta": False},
                    {"letra": "D", "texto": "15 m/s", "correta": False},
                    {"letra": "E", "texto": "25 m/s", "correta": False},
                ]
            },
            {
                "id": "q2",
                "enunciado": "Questão 2 sobre MRUV",
                "resposta": "20 m/s²",
                "alternativas": [
                    {"letra": "A", "texto": "5 m/s²", "correta": False},
                    {"letra": "B", "texto": "20 m/s²", "correta": True},
                    {"letra": "C", "texto": "10 m/s²", "correta": False},
                    {"letra": "D", "texto": "25 m/s²", "correta": False},
                    {"letra": "E", "texto": "15 m/s²", "correta": False},
                ]
            },
            {
                "id": "q3",
                "enunciado": "Questão 3 sobre Queda Livre",
                "resposta": "10 m/s²",
                "alternativas": [
                    {"letra": "A", "texto": "5 m/s²", "correta": False},
                    {"letra": "B", "texto": "15 m/s²", "correta": False},
                    {"letra": "C", "texto": "10 m/s²", "correta": True},
                    {"letra": "D", "texto": "20 m/s²", "correta": False},
                    {"letra": "E", "texto": "25 m/s²", "correta": False},
                ]
            }
        ]
    
    def test_instanciacao(self, service):
        """Testa instanciação do serviço."""
        assert service is not None
        assert service.seed == 42
    
    def test_instanciacao_sem_seed(self):
        """Testa instanciação sem seed."""
        service = EmbaralhamentoService()
        assert service is not None
        assert service.seed is None


class TestEmbaralhamentoLista:
    """Testes para embaralhamento de listas."""
    
    @pytest.fixture
    def service(self):
        return EmbaralhamentoService(seed=42)
    
    def test_embaralhar_lista(self, service):
        """Testa embaralhamento básico de lista."""
        lista_original = [1, 2, 3, 4, 5]
        
        lista_embaralhada, mapeamento = service.embaralhar_lista(lista_original)
        
        # Deve ter os mesmos elementos
        assert set(lista_embaralhada) == set(lista_original)
        assert len(lista_embaralhada) == len(lista_original)
        
        # Deve retornar mapeamento de índices
        assert len(mapeamento) == len(lista_original)
    
    def test_embaralhar_lista_reprodutivel(self, service):
        """Testa que o embaralhamento com seed é reprodutível."""
        lista = [1, 2, 3, 4, 5]
        
        # Primeira chamada
        resultado1, _ = service.embaralhar_lista(lista, seed_adicional=100)
        
        # Segunda chamada com mesma seed adicional
        resultado2, _ = service.embaralhar_lista(lista, seed_adicional=100)
        
        assert resultado1 == resultado2
    
    def test_embaralhar_lista_diferente_seed(self):
        """Testa que seeds diferentes produzem resultados diferentes."""
        lista = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        service1 = EmbaralhamentoService(seed=42)
        service2 = EmbaralhamentoService(seed=123)
        
        resultado1, _ = service1.embaralhar_lista(lista)
        resultado2, _ = service2.embaralhar_lista(lista)
        
        # Com alta probabilidade serão diferentes
        assert resultado1 != resultado2


class TestEmbaralhamentoAlternativas:
    """Testes para embaralhamento de alternativas."""
    
    @pytest.fixture
    def service(self):
        return EmbaralhamentoService(seed=42)
    
    @pytest.fixture
    def alternativas(self):
        return [
            {"letra": "A", "texto": "Opção A", "correta": True},
            {"letra": "B", "texto": "Opção B", "correta": False},
            {"letra": "C", "texto": "Opção C", "correta": False},
            {"letra": "D", "texto": "Opção D", "correta": False},
            {"letra": "E", "texto": "Opção E", "correta": False},
        ]
    
    def test_embaralhar_alternativas(self, service, alternativas):
        """Testa embaralhamento de alternativas."""
        alt_embaralhadas, mapeamento = service.embaralhar_alternativas(
            alternativas, "q1", 1
        )
        
        # Deve ter o mesmo número de alternativas
        assert len(alt_embaralhadas) == 5
        
        # Letras devem ser A-E em ordem
        letras = [a["letra"] for a in alt_embaralhadas]
        assert letras == ["A", "B", "C", "D", "E"]
        
        # Mapeamento deve existir
        assert mapeamento is not None
        assert mapeamento.questao_id == "q1"
        assert mapeamento.numero_questao == 1
    
    def test_mapeamento_resposta_correta(self, service, alternativas):
        """Testa que o mapeamento mantém a resposta correta."""
        alt_embaralhadas, mapeamento = service.embaralhar_alternativas(
            alternativas, "q1", 1
        )
        
        # A correta original era A
        assert mapeamento.correta_original == "A"
        
        # Encontrar a nova posição da correta
        correta_nova = mapeamento.correta_nova
        
        # Verificar que a alternativa marcada como correta tem a letra certa
        for alt in alt_embaralhadas:
            if alt.get("correta"):
                assert alt["letra"] == correta_nova
                break
    
    def test_embaralhar_alternativas_vazias(self, service):
        """Testa embaralhamento de lista vazia."""
        alt_embaralhadas, mapeamento = service.embaralhar_alternativas(
            [], "q1", 1
        )
        
        assert alt_embaralhadas == []
        assert mapeamento is None
    
    def test_textos_preservados(self, service, alternativas):
        """Testa que os textos das alternativas são preservados."""
        alt_embaralhadas, _ = service.embaralhar_alternativas(
            alternativas, "q1", 1
        )
        
        textos_originais = {a["texto"] for a in alternativas}
        textos_embaralhados = {a["texto"] for a in alt_embaralhadas}
        
        assert textos_originais == textos_embaralhados


class TestEmbaralhamentoQuestoes:
    """Testes para embaralhamento de questões."""
    
    @pytest.fixture
    def service(self):
        return EmbaralhamentoService(seed=42)
    
    @pytest.fixture
    def questoes(self):
        return [
            {"id": "q1", "enunciado": "Questão 1", "numero": 1},
            {"id": "q2", "enunciado": "Questão 2", "numero": 2},
            {"id": "q3", "enunciado": "Questão 3", "numero": 3},
            {"id": "q4", "enunciado": "Questão 4", "numero": 4},
            {"id": "q5", "enunciado": "Questão 5", "numero": 5},
        ]
    
    def test_embaralhar_questoes(self, service, questoes):
        """Testa embaralhamento de questões."""
        questoes_emb, mapeamento = service.embaralhar_questoes(questoes)
        
        # Mesmo número de questões
        assert len(questoes_emb) == 5
        
        # Mapeamento correto
        assert len(mapeamento) == 5
        
        # IDs preservados
        ids_originais = {q["id"] for q in questoes}
        ids_embaralhados = {q["id"] for q in questoes_emb}
        assert ids_originais == ids_embaralhados
    
    def test_numeros_atualizados(self, service, questoes):
        """Testa que os números das questões são atualizados."""
        questoes_emb, _ = service.embaralhar_questoes(questoes)
        
        numeros = [q["numero"] for q in questoes_emb]
        assert numeros == [1, 2, 3, 4, 5]
    
    def test_numero_original_preservado(self, service, questoes):
        """Testa que o número original é preservado."""
        questoes_emb, _ = service.embaralhar_questoes(questoes)
        
        for q in questoes_emb:
            assert "numero_original" in q
            assert q["numero_original"] in [1, 2, 3, 4, 5]
    
    def test_mapeamento_posicoes(self, service, questoes):
        """Testa que o mapeamento de posições está correto."""
        questoes_emb, mapeamento = service.embaralhar_questoes(questoes)
        
        for m in mapeamento:
            assert m.posicao_original in [1, 2, 3, 4, 5]
            assert m.nova_posicao in [1, 2, 3, 4, 5]
            assert m.questao_id.startswith("q")


class TestGeracaoProvaEmbaralhada:
    """Testes para geração de prova embaralhada."""
    
    @pytest.fixture
    def service(self):
        return EmbaralhamentoService(seed=42)
    
    @pytest.fixture
    def questoes_completas(self):
        return [
            {
                "id": "q1",
                "enunciado": "Questão 1",
                "alternativas": [
                    {"letra": "A", "texto": "A1", "correta": True},
                    {"letra": "B", "texto": "B1", "correta": False},
                    {"letra": "C", "texto": "C1", "correta": False},
                    {"letra": "D", "texto": "D1", "correta": False},
                    {"letra": "E", "texto": "E1", "correta": False},
                ]
            },
            {
                "id": "q2",
                "enunciado": "Questão 2",
                "alternativas": [
                    {"letra": "A", "texto": "A2", "correta": False},
                    {"letra": "B", "texto": "B2", "correta": True},
                    {"letra": "C", "texto": "C2", "correta": False},
                    {"letra": "D", "texto": "D2", "correta": False},
                    {"letra": "E", "texto": "E2", "correta": False},
                ]
            },
            {
                "id": "q3",
                "enunciado": "Questão 3",
                "alternativas": [
                    {"letra": "A", "texto": "A3", "correta": False},
                    {"letra": "B", "texto": "B3", "correta": False},
                    {"letra": "C", "texto": "C3", "correta": True},
                    {"letra": "D", "texto": "D3", "correta": False},
                    {"letra": "E", "texto": "E3", "correta": False},
                ]
            }
        ]
    
    def test_gerar_prova_embaralhada(self, service, questoes_completas):
        """Testa geração de prova embaralhada."""
        prova = service.gerar_prova_embaralhada(
            questoes=questoes_completas,
            numero_aluno=1
        )
        
        assert isinstance(prova, ProvaEmbaralhada)
        assert prova.numero_aluno == 1
        assert len(prova.questoes) == 3
        assert prova.codigo_prova is not None
        assert prova.hash_verificacao is not None
    
    def test_gabarito_correto(self, service, questoes_completas):
        """Testa que o gabarito está correto após embaralhamento."""
        prova = service.gerar_prova_embaralhada(
            questoes=questoes_completas,
            numero_aluno=1
        )
        
        # Verificar cada questão
        for i, questao in enumerate(prova.questoes, 1):
            numero_str = str(i)
            resposta_gabarito = prova.gabarito.get(numero_str)
            
            # A resposta no gabarito deve corresponder à alternativa correta
            for alt in questao["alternativas"]:
                if alt.get("correta"):
                    assert alt["letra"] == resposta_gabarito
    
    def test_codigo_prova_formato(self, service, questoes_completas):
        """Testa formato do código da prova."""
        prova = service.gerar_prova_embaralhada(
            questoes=questoes_completas,
            numero_aluno=1
        )
        
        # Formato esperado: LETRA + NUMERO (ex: A01, B02)
        assert len(prova.codigo_prova) == 3
        assert prova.codigo_prova[0].isalpha()
        assert prova.codigo_prova[1:].isdigit()
    
    def test_sem_embaralhamento(self, service, questoes_completas):
        """Testa geração sem embaralhamento."""
        prova = service.gerar_prova_embaralhada(
            questoes=questoes_completas,
            numero_aluno=1,
            embaralhar_questoes=False,
            embaralhar_alternativas=False
        )
        
        # Ordem das questões deve ser a original
        for i, q in enumerate(prova.questoes):
            assert q["numero"] == i + 1
    
    def test_apenas_embaralhar_questoes(self, service, questoes_completas):
        """Testa embaralhamento apenas das questões."""
        prova = service.gerar_prova_embaralhada(
            questoes=questoes_completas,
            numero_aluno=1,
            embaralhar_questoes=True,
            embaralhar_alternativas=False
        )
        
        # Gabarito deve refletir ordem original das alternativas
        assert prova.gabarito is not None


class TestGeracaoMultiplasProvas:
    """Testes para geração de múltiplas provas."""
    
    @pytest.fixture
    def service(self):
        return EmbaralhamentoService(seed=42)
    
    @pytest.fixture
    def questoes(self):
        return [
            {
                "id": f"q{i}",
                "enunciado": f"Questão {i}",
                "alternativas": [
                    {"letra": "A", "texto": "A", "correta": i == 1},
                    {"letra": "B", "texto": "B", "correta": i == 2},
                    {"letra": "C", "texto": "C", "correta": i == 3},
                    {"letra": "D", "texto": "D", "correta": i == 4},
                    {"letra": "E", "texto": "E", "correta": i == 5},
                ]
            }
            for i in range(1, 6)
        ]
    
    def test_gerar_multiplas_provas(self, service, questoes):
        """Testa geração de múltiplas provas."""
        provas = service.gerar_multiplas_provas(
            questoes=questoes,
            quantidade_alunos=10
        )
        
        assert len(provas) == 10
        
        for i, prova in enumerate(provas, 1):
            assert prova.numero_aluno == i
    
    def test_codigos_unicos(self, service, questoes):
        """Testa que cada prova tem código único."""
        provas = service.gerar_multiplas_provas(
            questoes=questoes,
            quantidade_alunos=30
        )
        
        codigos = [p.codigo_prova for p in provas]
        assert len(codigos) == len(set(codigos))  # Todos únicos
    
    def test_hashes_diferentes(self, service, questoes):
        """Testa que as provas têm hashes diferentes (provas diferentes)."""
        provas = service.gerar_multiplas_provas(
            questoes=questoes,
            quantidade_alunos=10
        )
        
        hashes = [p.hash_verificacao for p in provas]
        # A maioria deve ser diferente (algumas podem coincidir por acaso)
        assert len(set(hashes)) > 1
    
    def test_gabarito_consolidado(self, service, questoes):
        """Testa geração de gabarito consolidado."""
        provas = service.gerar_multiplas_provas(
            questoes=questoes,
            quantidade_alunos=5
        )
        
        gabarito = service.gerar_gabarito_consolidado(provas)
        
        assert len(gabarito) == 5
        
        for codigo, dados in gabarito.items():
            assert "numero_aluno" in dados
            assert "gabarito" in dados
            assert "hash" in dados
    
    def test_converter_para_dict(self, service, questoes):
        """Testa conversão de prova para dicionário."""
        prova = service.gerar_prova_embaralhada(questoes, 1)
        
        prova_dict = service.converter_para_dict(prova)
        
        assert isinstance(prova_dict, dict)
        assert prova_dict["numero_aluno"] == 1
        assert "questoes" in prova_dict
        assert "gabarito" in prova_dict
        assert "ordem_questoes" in prova_dict
        assert "ordem_alternativas" in prova_dict


class TestVerificacaoIntegridade:
    """Testes para verificação de integridade."""
    
    @pytest.fixture
    def service(self):
        return EmbaralhamentoService(seed=42)
    
    @pytest.fixture
    def prova_exemplo(self, service):
        questoes = [
            {
                "id": "q1",
                "enunciado": "Questão",
                "alternativas": [
                    {"letra": "A", "texto": "A", "correta": True},
                    {"letra": "B", "texto": "B", "correta": False},
                ]
            }
        ]
        return service.gerar_prova_embaralhada(questoes, 1)
    
    def test_verificar_integridade_valida(self, service, prova_exemplo):
        """Testa verificação de prova não alterada."""
        resultado = service.verificar_integridade(
            prova_exemplo,
            prova_exemplo.hash_verificacao
        )
        
        assert resultado is True
    
    def test_verificar_integridade_invalida(self, service, prova_exemplo):
        """Testa verificação de prova alterada."""
        # Hash incorreto
        resultado = service.verificar_integridade(
            prova_exemplo,
            "hash_invalido"
        )
        
        assert resultado is False


class TestTiposQuestao:
    """Testes para diferentes tipos de questão."""
    
    @pytest.fixture
    def service(self):
        return EmbaralhamentoService(seed=42)
    
    def test_identificar_multipla_escolha(self, service):
        """Testa identificação de múltipla escolha."""
        questao = {
            "enunciado": "Questão",
            "alternativas": [
                {"letra": "A", "texto": "A", "correta": True},
                {"letra": "B", "texto": "B", "correta": False},
                {"letra": "C", "texto": "C", "correta": False},
            ]
        }
        
        tipo = service.identificar_tipo_questao(questao)
        assert tipo == TipoQuestao.MULTIPLA_ESCOLHA
    
    def test_identificar_verdadeiro_falso(self, service):
        """Testa identificação de V/F."""
        questao = {
            "enunciado": "Afirmação",
            "alternativas": [
                {"letra": "V", "texto": "Verdadeiro", "correta": True},
                {"letra": "F", "texto": "Falso", "correta": False},
            ]
        }
        
        tipo = service.identificar_tipo_questao(questao)
        assert tipo == TipoQuestao.VERDADEIRO_FALSO
    
    def test_identificar_dissertativa(self, service):
        """Testa identificação de dissertativa."""
        questao = {
            "enunciado": "Explique o conceito...",
            "resposta": "A resposta é uma explicação textual longa",
            "alternativas": []
        }
        
        tipo = service.identificar_tipo_questao(questao)
        assert tipo == TipoQuestao.DISSERTATIVA
    
    def test_identificar_numerica(self, service):
        """Testa identificação de numérica."""
        questao = {
            "enunciado": "Calcule o valor de x",
            "resposta": "42.5",
            "alternativas": []
        }
        
        tipo = service.identificar_tipo_questao(questao)
        assert tipo == TipoQuestao.NUMERICA
    
    def test_identificar_multipla_resposta(self, service):
        """Testa identificação de múltipla resposta."""
        questao = {
            "enunciado": "Marque todas as corretas",
            "alternativas": [
                {"letra": "A", "texto": "A", "correta": True},
                {"letra": "B", "texto": "B", "correta": False},
                {"letra": "C", "texto": "C", "correta": True},
                {"letra": "D", "texto": "D", "correta": False},
            ]
        }
        
        tipo = service.identificar_tipo_questao(questao)
        assert tipo == TipoQuestao.MULTIPLA_RESPOSTA
    
    def test_identificar_tipo_explicito(self, service):
        """Testa identificação quando tipo é explícito."""
        questao = {
            "enunciado": "Questão",
            "tipo_questao": "dissertativa",
            "alternativas": []
        }
        
        tipo = service.identificar_tipo_questao(questao)
        assert tipo == TipoQuestao.DISSERTATIVA


class TestEmbaralhamentoVerdadeiroFalso:
    """Testes para questões Verdadeiro/Falso."""
    
    @pytest.fixture
    def service(self):
        return EmbaralhamentoService(seed=42)
    
    def test_vf_nao_embaralha(self, service):
        """Testa que V/F não é embaralhado."""
        alternativas = [
            {"letra": "V", "texto": "Verdadeiro", "correta": True},
            {"letra": "F", "texto": "Falso", "correta": False},
        ]
        
        resultado, mapeamento = service._processar_verdadeiro_falso(
            alternativas, "q1", 1
        )
        
        # V sempre primeiro
        assert resultado[0]["letra"] == "V"
        assert resultado[1]["letra"] == "F"
        assert mapeamento.correta_nova == "V"
    
    def test_vf_resposta_falsa(self, service):
        """Testa V/F quando a resposta é Falso."""
        alternativas = [
            {"letra": "V", "texto": "Verdadeiro", "correta": False},
            {"letra": "F", "texto": "Falso", "correta": True},
        ]
        
        resultado, mapeamento = service._processar_verdadeiro_falso(
            alternativas, "q1", 1
        )
        
        assert mapeamento.correta_nova == "F"
    
    def test_vf_prova_completa(self, service):
        """Testa prova com questões V/F."""
        questoes = [
            {
                "id": "q1",
                "enunciado": "A água ferve a 100°C ao nível do mar.",
                "alternativas": [
                    {"letra": "V", "texto": "Verdadeiro", "correta": True},
                    {"letra": "F", "texto": "Falso", "correta": False},
                ]
            }
        ]
        
        prova = service.gerar_prova_embaralhada(questoes, 1)
        
        # Gabarito deve ser V ou F
        assert prova.gabarito["1"] in ["V", "F"]
        assert prova.gabarito["1"] == "V"


class TestEmbaralhamentoDissertativa:
    """Testes para questões dissertativas."""
    
    @pytest.fixture
    def service(self):
        return EmbaralhamentoService(seed=42)
    
    def test_dissertativa_gabarito_texto(self, service):
        """Testa que dissertativa tem gabarito textual."""
        questoes = [
            {
                "id": "q1",
                "enunciado": "Explique a teoria da relatividade",
                "resposta": "A teoria da relatividade de Einstein...",
                "alternativas": []
            }
        ]
        
        prova = service.gerar_prova_embaralhada(questoes, 1)
        
        # Gabarito é a resposta
        assert "relatividade" in prova.gabarito["1"].lower() or "Einstein" in prova.gabarito["1"]
    
    def test_mista_dissertativa_multipla(self, service):
        """Testa prova mista com dissertativa e múltipla escolha."""
        questoes = [
            {
                "id": "q1",
                "enunciado": "Explique...",
                "resposta": "Resposta dissertativa",
                "alternativas": []
            },
            {
                "id": "q2",
                "enunciado": "Escolha...",
                "alternativas": [
                    {"letra": "A", "texto": "A", "correta": True},
                    {"letra": "B", "texto": "B", "correta": False},
                ]
            }
        ]
        
        prova = service.gerar_prova_embaralhada(questoes, 1)
        
        # Questão 1 ou 2 (dependendo do embaralhamento) tem gabarito diferente
        assert len(prova.gabarito) == 2


class TestEmbaralhamentoNumerica:
    """Testes para questões numéricas."""
    
    @pytest.fixture
    def service(self):
        return EmbaralhamentoService(seed=42)
    
    def test_numerica_gabarito_numero(self, service):
        """Testa que numérica tem gabarito numérico."""
        questoes = [
            {
                "id": "q1",
                "enunciado": "Calcule 2 + 2",
                "resposta": "4",
                "alternativas": []
            }
        ]
        
        prova = service.gerar_prova_embaralhada(questoes, 1)
        
        assert "4" in prova.gabarito["1"]
    
    def test_numerica_com_tolerancia(self, service):
        """Testa numérica com tolerância."""
        questoes = [
            {
                "id": "q1",
                "enunciado": "Calcule pi",
                "resposta": "3.14",
                "tolerancia": 0.01,
                "alternativas": []
            }
        ]
        
        prova = service.gerar_prova_embaralhada(questoes, 1)
        
        assert "3.14" in prova.gabarito["1"]


class TestEmbaralhamentoMultiplaResposta:
    """Testes para questões com múltiplas respostas corretas."""
    
    @pytest.fixture
    def service(self):
        return EmbaralhamentoService(seed=42)
    
    def test_multipla_resposta_identificacao(self, service):
        """Testa identificação de múltipla resposta."""
        questao = {
            "alternativas": [
                {"letra": "A", "texto": "A", "correta": True},
                {"letra": "B", "texto": "B", "correta": True},
                {"letra": "C", "texto": "C", "correta": False},
            ]
        }
        
        tipo = service.identificar_tipo_questao(questao)
        assert tipo == TipoQuestao.MULTIPLA_RESPOSTA
    
    def test_multipla_resposta_gabarito_lista(self, service):
        """Testa que gabarito é lista quando tem múltiplas corretas."""
        questoes = [
            {
                "id": "q1",
                "enunciado": "Marque todas corretas",
                "alternativas": [
                    {"letra": "A", "texto": "A", "correta": True},
                    {"letra": "B", "texto": "B", "correta": False},
                    {"letra": "C", "texto": "C", "correta": True},
                    {"letra": "D", "texto": "D", "correta": False},
                ]
            }
        ]
        
        prova = service.gerar_prova_embaralhada(questoes, 1)
        
        # Gabarito deve ser lista
        gabarito = prova.gabarito["1"]
        assert isinstance(gabarito, list)
        assert len(gabarito) == 2


class TestEmbaralhamentoAssociacao:
    """Testes para questões de associação."""
    
    @pytest.fixture
    def service(self):
        return EmbaralhamentoService(seed=42)
    
    def test_associacao_embaralha_coluna_b(self, service):
        """Testa que coluna B é embaralhada."""
        questao = {
            "coluna_a": ["Item 1", "Item 2", "Item 3"],
            "coluna_b": ["Resposta A", "Resposta B", "Resposta C"],
            "gabarito_associacao": {1: 1, 2: 2, 3: 3}
        }
        
        resultado = service.embaralhar_associacao(questao, 100)
        
        # Coluna B deve ter sido embaralhada
        assert "coluna_b" in resultado
        assert len(resultado["coluna_b"]) == 3
        assert "mapeamento_coluna_b" in resultado
    
    def test_associacao_gabarito_atualizado(self, service):
        """Testa que gabarito de associação é atualizado."""
        questao = {
            "coluna_a": ["A", "B"],
            "coluna_b": ["1", "2"],
            "gabarito_associacao": {1: 1, 2: 2}
        }
        
        resultado = service.embaralhar_associacao(questao, 100)
        
        assert "gabarito_associacao" in resultado


class TestProvaMista:
    """Testes para provas com diferentes tipos de questão."""
    
    @pytest.fixture
    def service(self):
        return EmbaralhamentoService(seed=42)
    
    def test_prova_todos_tipos(self, service):
        """Testa prova com todos os tipos de questão."""
        questoes = [
            # Múltipla escolha
            {
                "id": "q1",
                "enunciado": "Múltipla escolha",
                "alternativas": [
                    {"letra": "A", "texto": "A", "correta": True},
                    {"letra": "B", "texto": "B", "correta": False},
                    {"letra": "C", "texto": "C", "correta": False},
                ]
            },
            # V/F
            {
                "id": "q2",
                "enunciado": "Verdadeiro ou Falso",
                "alternativas": [
                    {"letra": "V", "texto": "Verdadeiro", "correta": False},
                    {"letra": "F", "texto": "Falso", "correta": True},
                ]
            },
            # Dissertativa
            {
                "id": "q3",
                "enunciado": "Dissertativa",
                "resposta": "Resposta aberta",
                "alternativas": []
            },
            # Numérica
            {
                "id": "q4",
                "enunciado": "Numérica",
                "resposta": "42",
                "alternativas": []
            },
        ]
        
        prova = service.gerar_prova_embaralhada(questoes, 1)
        
        # Deve ter 4 questões no gabarito
        assert len(prova.gabarito) == 4
        
        # Cada questão deve ter tipo identificado
        for q in prova.questoes:
            assert "tipo_identificado" in q
    
    def test_embaralhamento_preserva_tipos(self, service):
        """Testa que embaralhamento preserva tipos corretos."""
        questoes = [
            {
                "id": "q1",
                "tipo_questao": "dissertativa",
                "enunciado": "Explique",
                "resposta": "Explicação",
                "alternativas": []
            },
            {
                "id": "q2",
                "tipo_questao": "multipla_escolha",
                "enunciado": "Escolha",
                "alternativas": [
                    {"letra": "A", "texto": "A", "correta": True},
                    {"letra": "B", "texto": "B", "correta": False},
                ]
            },
        ]
        
        # Gerar múltiplas provas
        provas = service.gerar_multiplas_provas(questoes, 5)
        
        for prova in provas:
            # Verificar que cada questão mantém seu tipo
            for q in prova.questoes:
                if q["id"] == "q1":
                    assert q["tipo_identificado"] == "dissertativa"
                elif q["id"] == "q2":
                    assert q["tipo_identificado"] == "multipla_escolha"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

