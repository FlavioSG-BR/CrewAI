"""
Testes para o Serviço de Provas Individuais.

Executa: pytest tests/test_prova_individual_service.py -v
"""

import pytest
import sys
import os
import tempfile
import shutil

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.services.prova_individual_service import (
    ProvaIndividualService,
    ConfiguracaoProvaIndividual,
    ResultadoLoteProvas,
    ProvaProfessor
)
from backend.services.revisao_service import RevisaoService


class TestConfiguracaoProvaIndividual:
    """Testes para a configuração de prova individual."""
    
    def test_criar_configuracao_basica(self):
        """Testa criação de configuração básica."""
        config = ConfiguracaoProvaIndividual(
            titulo="Prova de Física",
            questoes_ids=["q1", "q2", "q3"],
            quantidade_alunos=30
        )
        
        assert config.titulo == "Prova de Física"
        assert config.quantidade_alunos == 30
        assert len(config.questoes_ids) == 3
        assert config.embaralhar_questoes is True
        assert config.embaralhar_alternativas is True
    
    def test_criar_configuracao_completa(self):
        """Testa criação de configuração com todos os parâmetros."""
        config = ConfiguracaoProvaIndividual(
            titulo="Prova Final",
            questoes_ids=["q1", "q2"],
            quantidade_alunos=50,
            embaralhar_questoes=False,
            embaralhar_alternativas=True,
            instituicao="Escola XYZ",
            instrucoes=["Leia com atenção", "Use caneta azul"],
            tempo_limite_min=120,
            incluir_campo_nome=True,
            incluir_campo_matricula=True,
            gerar_pdf=True,
            gerar_zip=True
        )
        
        assert config.titulo == "Prova Final"
        assert config.quantidade_alunos == 50
        assert config.embaralhar_questoes is False
        assert config.instituicao == "Escola XYZ"
        assert len(config.instrucoes) == 2
        assert config.tempo_limite_min == 120


class TestResultadoLoteProvas:
    """Testes para o resultado de lote de provas."""
    
    def test_criar_resultado_sucesso(self):
        """Testa criação de resultado de sucesso."""
        resultado = ResultadoLoteProvas(
            lote_id="abc123",
            titulo="Prova Teste",
            quantidade_alunos=30,
            provas_geradas=30,
            provas=[{"id": "1"}, {"id": "2"}],
            gabarito_consolidado={"A01": {"1": "A"}},
            caminho_zip="/path/to/file.zip",
            tempo_geracao_seg=5.5,
            status="concluido"
        )
        
        assert resultado.lote_id == "abc123"
        assert resultado.provas_geradas == 30
        assert resultado.status == "concluido"
        assert resultado.erro is None
    
    def test_criar_resultado_erro(self):
        """Testa criação de resultado de erro."""
        resultado = ResultadoLoteProvas(
            lote_id="abc123",
            titulo="Prova Teste",
            quantidade_alunos=30,
            provas_geradas=0,
            provas=[],
            gabarito_consolidado={},
            status="erro",
            erro="Nenhuma questão encontrada"
        )
        
        assert resultado.status == "erro"
        assert resultado.erro == "Nenhuma questão encontrada"
        assert resultado.provas_geradas == 0


class TestProvaIndividualService:
    """Testes para o serviço de provas individuais."""
    
    @pytest.fixture
    def service(self):
        """Fixture que cria o serviço."""
        return ProvaIndividualService()
    
    @pytest.fixture
    def questoes_no_banco(self, service):
        """Fixture que adiciona questões ao banco de revisão."""
        questoes_ids = []
        
        questoes = [
            {
                "enunciado": "Qual é a velocidade de um corpo em MRU que percorre 100m em 10s?",
                "resposta": "10 m/s",
                "materia": "fisica",
                "topico": "mru",
                "dificuldade": "facil",
                "alternativas": [
                    {"letra": "A", "texto": "10 m/s", "correta": True},
                    {"letra": "B", "texto": "20 m/s", "correta": False},
                    {"letra": "C", "texto": "5 m/s", "correta": False},
                    {"letra": "D", "texto": "15 m/s", "correta": False},
                    {"letra": "E", "texto": "25 m/s", "correta": False},
                ]
            },
            {
                "enunciado": "Um móvel com velocidade inicial 0 acelera a 2 m/s². Qual sua velocidade após 5s?",
                "resposta": "10 m/s",
                "materia": "fisica",
                "topico": "mruv",
                "dificuldade": "medio",
                "alternativas": [
                    {"letra": "A", "texto": "5 m/s", "correta": False},
                    {"letra": "B", "texto": "10 m/s", "correta": True},
                    {"letra": "C", "texto": "15 m/s", "correta": False},
                    {"letra": "D", "texto": "20 m/s", "correta": False},
                    {"letra": "E", "texto": "25 m/s", "correta": False},
                ]
            },
            {
                "enunciado": "Qual a aceleração da gravidade aproximada na Terra?",
                "resposta": "10 m/s²",
                "materia": "fisica",
                "topico": "queda_livre",
                "dificuldade": "facil",
                "alternativas": [
                    {"letra": "A", "texto": "5 m/s²", "correta": False},
                    {"letra": "B", "texto": "8 m/s²", "correta": False},
                    {"letra": "C", "texto": "10 m/s²", "correta": True},
                    {"letra": "D", "texto": "12 m/s²", "correta": False},
                    {"letra": "E", "texto": "15 m/s²", "correta": False},
                ]
            }
        ]
        
        for q in questoes:
            q_id = service.revisao_service.adicionar_questao_para_revisao(q)
            service.revisao_service.aprovar_questao(q_id)
            questoes_ids.append(q_id)
        
        return questoes_ids
    
    def test_instanciacao(self, service):
        """Testa instanciação do serviço."""
        assert service is not None
        assert service.embaralhamento is not None
        assert service.revisao_service is not None
    
    def test_obter_questoes_por_ids(self, service, questoes_no_banco):
        """Testa obtenção de questões pelos IDs."""
        questoes = service.obter_questoes_por_ids(questoes_no_banco)
        
        assert len(questoes) == 3
        for q in questoes:
            assert "enunciado" in q
            assert "alternativas" in q
    
    def test_obter_questoes_ids_inexistentes(self, service):
        """Testa obtenção com IDs inexistentes."""
        questoes = service.obter_questoes_por_ids(["id_invalido_1", "id_invalido_2"])
        
        assert len(questoes) == 0
    
    def test_gerar_provas_sem_questoes(self, service):
        """Testa geração sem questões válidas."""
        config = ConfiguracaoProvaIndividual(
            titulo="Prova Teste",
            questoes_ids=["id_invalido"],
            quantidade_alunos=10,
            gerar_pdf=False,
            gerar_zip=False
        )
        
        resultado = service.gerar_provas_individuais(config)
        
        assert resultado.status == "erro"
        assert "Nenhuma questão encontrada" in resultado.erro
    
    def test_gerar_provas_individuais_basico(self, service, questoes_no_banco):
        """Testa geração básica de provas individuais (sem PDF)."""
        config = ConfiguracaoProvaIndividual(
            titulo="Prova de Física",
            questoes_ids=questoes_no_banco,
            quantidade_alunos=5,
            embaralhar_questoes=True,
            embaralhar_alternativas=True,
            gerar_pdf=False,  # Não gerar PDF para teste rápido
            gerar_zip=False
        )
        
        resultado = service.gerar_provas_individuais(config)
        
        assert resultado.status == "concluido"
        assert resultado.provas_geradas == 5
        assert len(resultado.provas) == 5
        assert len(resultado.gabarito_consolidado) == 5
    
    def test_provas_diferentes(self, service, questoes_no_banco):
        """Testa que as provas geradas são diferentes."""
        config = ConfiguracaoProvaIndividual(
            titulo="Prova Teste",
            questoes_ids=questoes_no_banco,
            quantidade_alunos=10,
            embaralhar_questoes=True,
            embaralhar_alternativas=True,
            gerar_pdf=False,
            gerar_zip=False
        )
        
        resultado = service.gerar_provas_individuais(config)
        
        # Verificar que os códigos são únicos
        codigos = [p["codigo_prova"] for p in resultado.provas]
        assert len(codigos) == len(set(codigos))
        
        # Verificar que os gabaritos variam
        gabaritos = [tuple(g["gabarito"].items()) for g in resultado.gabarito_consolidado.values()]
        # Nem todos devem ser iguais
        assert len(set(gabaritos)) > 1
    
    def test_gabarito_consolidado_estrutura(self, service, questoes_no_banco):
        """Testa estrutura do gabarito consolidado."""
        config = ConfiguracaoProvaIndividual(
            titulo="Prova Teste",
            questoes_ids=questoes_no_banco,
            quantidade_alunos=3,
            gerar_pdf=False,
            gerar_zip=False
        )
        
        resultado = service.gerar_provas_individuais(config)
        
        for codigo, dados in resultado.gabarito_consolidado.items():
            assert "numero_aluno" in dados
            assert "gabarito" in dados
            assert "hash" in dados
            
            # Gabarito deve ter respostas para todas as questões
            assert len(dados["gabarito"]) == 3
    
    def test_sem_embaralhamento(self, service, questoes_no_banco):
        """Testa geração sem embaralhamento."""
        config = ConfiguracaoProvaIndividual(
            titulo="Prova Sem Embaralhamento",
            questoes_ids=questoes_no_banco,
            quantidade_alunos=3,
            embaralhar_questoes=False,
            embaralhar_alternativas=False,
            gerar_pdf=False,
            gerar_zip=False
        )
        
        resultado = service.gerar_provas_individuais(config)
        
        # Todos os gabaritos devem ser iguais
        gabaritos = [tuple(sorted(g["gabarito"].items())) 
                     for g in resultado.gabarito_consolidado.values()]
        assert len(set(gabaritos)) == 1
    
    def test_tempo_geracao(self, service, questoes_no_banco):
        """Testa que o tempo de geração é registrado."""
        config = ConfiguracaoProvaIndividual(
            titulo="Prova Teste",
            questoes_ids=questoes_no_banco,
            quantidade_alunos=5,
            gerar_pdf=False,
            gerar_zip=False
        )
        
        resultado = service.gerar_provas_individuais(config)
        
        assert resultado.tempo_geracao_seg > 0


class TestGeracaoProvaRapida:
    """Testes para o método de geração rápida."""
    
    @pytest.fixture
    def service(self):
        return ProvaIndividualService()
    
    @pytest.fixture
    def questoes_ids(self, service):
        questoes = [
            {
                "enunciado": f"Questão {i}",
                "resposta": f"Resposta {i}",
                "materia": "fisica",
                "alternativas": [
                    {"letra": "A", "texto": "A", "correta": True},
                    {"letra": "B", "texto": "B", "correta": False},
                ]
            }
            for i in range(1, 4)
        ]
        
        ids = []
        for q in questoes:
            q_id = service.revisao_service.adicionar_questao_para_revisao(q)
            service.revisao_service.aprovar_questao(q_id)
            ids.append(q_id)
        
        return ids
    
    def test_gerar_prova_rapida(self, service, questoes_ids):
        """Testa método de geração rápida."""
        # Mock para não gerar PDF
        original_gerar = service.gerar_provas_individuais
        
        def mock_gerar(config):
            config.gerar_pdf = False
            config.gerar_zip = False
            return original_gerar(config)
        
        service.gerar_provas_individuais = mock_gerar
        
        resultado = service.gerar_prova_rapida(
            titulo="Prova Rápida",
            questoes_ids=questoes_ids,
            quantidade_alunos=5,
            instituicao="Teste"
        )
        
        assert resultado.status == "concluido"
        assert resultado.provas_geradas == 5


class TestIntegracaoCompleta:
    """Testes de integração do fluxo completo."""
    
    def test_fluxo_completo_geracao_provas(self):
        """Testa o fluxo completo de geração de provas individuais."""
        # 1. Criar serviço
        service = ProvaIndividualService()
        
        # 2. Adicionar questões ao banco
        questoes = [
            {
                "enunciado": "Qual é a fórmula da velocidade média?",
                "resposta": "v = Δs/Δt",
                "materia": "fisica",
                "topico": "cinematica",
                "dificuldade": "facil",
                "alternativas": [
                    {"letra": "A", "texto": "v = Δs/Δt", "correta": True},
                    {"letra": "B", "texto": "v = s.t", "correta": False},
                    {"letra": "C", "texto": "v = s/t²", "correta": False},
                    {"letra": "D", "texto": "v = s + t", "correta": False},
                    {"letra": "E", "texto": "v = s - t", "correta": False},
                ]
            },
            {
                "enunciado": "Qual a segunda lei de Newton?",
                "resposta": "F = m.a",
                "materia": "fisica",
                "topico": "dinamica",
                "dificuldade": "medio",
                "alternativas": [
                    {"letra": "A", "texto": "F = m/a", "correta": False},
                    {"letra": "B", "texto": "F = m.a", "correta": True},
                    {"letra": "C", "texto": "F = m + a", "correta": False},
                    {"letra": "D", "texto": "F = m - a", "correta": False},
                    {"letra": "E", "texto": "F = m²a", "correta": False},
                ]
            }
        ]
        
        questoes_ids = []
        for q in questoes:
            q_id = service.revisao_service.adicionar_questao_para_revisao(q)
            # 3. Aprovar questões
            service.revisao_service.aprovar_questao(q_id, comentarios="Aprovada")
            questoes_ids.append(q_id)
        
        # 4. Configurar prova
        config = ConfiguracaoProvaIndividual(
            titulo="Prova de Física - 1º Bimestre",
            questoes_ids=questoes_ids,
            quantidade_alunos=10,
            embaralhar_questoes=True,
            embaralhar_alternativas=True,
            instituicao="Escola Teste",
            instrucoes=["Leia com atenção", "Use caneta preta ou azul"],
            tempo_limite_min=60,
            gerar_pdf=False,  # Não gerar PDF no teste
            gerar_zip=False
        )
        
        # 5. Gerar provas
        resultado = service.gerar_provas_individuais(config)
        
        # 6. Verificar resultado
        assert resultado.status == "concluido"
        assert resultado.titulo == "Prova de Física - 1º Bimestre"
        assert resultado.provas_geradas == 10
        assert len(resultado.provas) == 10
        assert len(resultado.gabarito_consolidado) == 10
        
        # 7. Verificar que cada prova tem estrutura correta
        for prova in resultado.provas:
            assert "codigo_prova" in prova
            assert "numero_aluno" in prova
            assert "questoes" in prova
            assert "gabarito" in prova
            assert len(prova["questoes"]) == 2
        
        # 8. Verificar gabarito consolidado
        for codigo, dados in resultado.gabarito_consolidado.items():
            assert "numero_aluno" in dados
            assert "gabarito" in dados
            # Cada gabarito deve ter 2 respostas
            assert len(dados["gabarito"]) == 2


class TestProvaProfessor:
    """Testes para a geração da prova do professor (mestre comentada)."""
    
    def test_dataclass_prova_professor(self):
        """Testa criação do dataclass ProvaProfessor."""
        prova_prof = ProvaProfessor(
            titulo="Prova de Teste - PROFESSOR",
            questoes=[{"id": "q1", "enunciado": "Teste"}],
            gabarito_completo={"1": "A"},
            comentarios={"1": "Explicação da questão"},
            fontes_bibliograficas=[{"autor": "Autor", "titulo": "Livro"}],
            total_questoes=1
        )
        
        assert prova_prof.titulo == "Prova de Teste - PROFESSOR"
        assert len(prova_prof.questoes) == 1
        assert prova_prof.gabarito_completo["1"] == "A"
        assert "1" in prova_prof.comentarios
    
    def test_configuracao_com_prova_professor(self):
        """Testa que a configuração padrão inclui geração de prova do professor."""
        config = ConfiguracaoProvaIndividual(
            titulo="Prova",
            questoes_ids=["q1"],
            quantidade_alunos=10
        )
        
        # Deve gerar prova do professor por padrão
        assert config.gerar_prova_professor is True
    
    def test_configuracao_sem_prova_professor(self):
        """Testa que é possível desabilitar geração de prova do professor."""
        config = ConfiguracaoProvaIndividual(
            titulo="Prova",
            questoes_ids=["q1"],
            quantidade_alunos=10,
            gerar_prova_professor=False
        )
        
        assert config.gerar_prova_professor is False


class TestResultadoLoteProvasComProfessor:
    """Testes para o resultado do lote incluindo prova do professor."""
    
    def test_resultado_com_prova_professor(self):
        """Testa resultado do lote com prova do professor."""
        resultado = ResultadoLoteProvas(
            lote_id="abc123",
            titulo="Prova",
            quantidade_alunos=30,
            provas_geradas=31,  # 30 alunos + 1 professor
            provas_alunos=[{"codigo_prova": f"P{i}"} for i in range(30)],
            prova_professor={
                "codigo_prova": "PROFESSOR",
                "e_prova_professor": True,
                "gabarito_completo": {"1": "A", "2": "B"}
            }
        )
        
        assert resultado.provas_geradas == 31
        assert len(resultado.provas_alunos) == 30
        assert resultado.prova_professor is not None
        assert resultado.prova_professor["codigo_prova"] == "PROFESSOR"
    
    def test_propriedade_provas_inclui_professor(self):
        """Testa que a propriedade provas inclui professor no início."""
        resultado = ResultadoLoteProvas(
            lote_id="abc123",
            titulo="Prova",
            quantidade_alunos=5,
            provas_geradas=6,
            provas_alunos=[{"codigo_prova": f"P{i}"} for i in range(5)],
            prova_professor={"codigo_prova": "PROFESSOR"}
        )
        
        # Propriedade 'provas' deve incluir todas
        todas_provas = resultado.provas
        assert len(todas_provas) == 6
        
        # Professor deve ser o primeiro
        assert todas_provas[0]["codigo_prova"] == "PROFESSOR"
    
    def test_resultado_sem_prova_professor(self):
        """Testa resultado do lote sem prova do professor."""
        resultado = ResultadoLoteProvas(
            lote_id="abc123",
            titulo="Prova",
            quantidade_alunos=10,
            provas_geradas=10,
            provas_alunos=[{"codigo_prova": f"P{i}"} for i in range(10)],
            prova_professor=None
        )
        
        assert resultado.prova_professor is None
        assert len(resultado.provas) == 10  # Apenas alunos
    
    def test_gabarito_consolidado_inclui_professor(self):
        """Testa que gabarito consolidado pode incluir dados do professor."""
        gabarito = {
            "PROFESSOR": {
                "numero_aluno": 0,
                "gabarito": {"1": "A", "2": "B"},
                "hash": "master",
                "comentada": True
            },
            "P001": {
                "numero_aluno": 1,
                "gabarito": {"1": "C", "2": "A"},
                "hash": "abc123"
            }
        }
        
        resultado = ResultadoLoteProvas(
            lote_id="xyz",
            titulo="Prova",
            quantidade_alunos=1,
            provas_geradas=2,
            provas_alunos=[],
            prova_professor={},
            gabarito_consolidado=gabarito
        )
        
        assert "PROFESSOR" in resultado.gabarito_consolidado
        assert resultado.gabarito_consolidado["PROFESSOR"]["comentada"] is True


class TestGeracaoProvaProfessor:
    """Testes de integração para geração da prova do professor."""
    
    @pytest.fixture
    def questoes_mock(self):
        """Questões de teste para gerar prova do professor."""
        return [
            {
                "id": "q1",
                "enunciado": "Qual a capital do Brasil?",
                "tipo_questao": "multipla_escolha",
                "alternativas": [
                    {"letra": "A", "texto": "São Paulo", "correta": False},
                    {"letra": "B", "texto": "Rio de Janeiro", "correta": False},
                    {"letra": "C", "texto": "Brasília", "correta": True},
                    {"letra": "D", "texto": "Salvador", "correta": False},
                ],
                "explicacao": "Brasília foi construída para ser a capital federal.",
                "fontes_bibliograficas": [
                    {"autor": "IBGE", "titulo": "Atlas do Brasil", "ano": "2023"}
                ]
            },
            {
                "id": "q2",
                "enunciado": "A Terra é plana.",
                "tipo_questao": "verdadeiro_falso",
                "alternativas": [
                    {"letra": "V", "texto": "Verdadeiro", "correta": False},
                    {"letra": "F", "texto": "Falso", "correta": True},
                ],
                "explicacao": "A Terra tem formato geoide, aproximadamente esférico."
            },
            {
                "id": "q3",
                "enunciado": "Explique a fotossíntese.",
                "tipo_questao": "dissertativa",
                "resposta": "A fotossíntese é o processo pelo qual plantas convertem luz solar em energia.",
                "alternativas": []
            }
        ]
    
    def test_prova_professor_contem_gabarito_completo(self, questoes_mock):
        """Testa que a prova do professor contém gabarito de todas as questões."""
        from copy import deepcopy
        
        service = ProvaIndividualService()
        
        # Gerar prova do professor diretamente
        prova_prof = service._gerar_prova_professor(
            questoes=deepcopy(questoes_mock),
            config=ConfiguracaoProvaIndividual(
                titulo="Prova Teste",
                questoes_ids=["q1", "q2", "q3"],
                quantidade_alunos=5,
                gerar_pdf=False
            ),
            output_dir=tempfile.mkdtemp()
        )
        
        # Verificar gabarito completo
        assert "gabarito_completo" in prova_prof
        gabarito = prova_prof["gabarito_completo"]
        
        assert "1" in gabarito  # Questão 1
        assert "2" in gabarito  # Questão 2
        assert "3" in gabarito  # Questão 3
    
    def test_prova_professor_contem_comentarios(self, questoes_mock):
        """Testa que a prova do professor contém comentários/explicações."""
        from copy import deepcopy
        
        service = ProvaIndividualService()
        
        prova_prof = service._gerar_prova_professor(
            questoes=deepcopy(questoes_mock),
            config=ConfiguracaoProvaIndividual(
                titulo="Prova",
                questoes_ids=["q1", "q2", "q3"],
                quantidade_alunos=5,
                gerar_pdf=False
            ),
            output_dir=tempfile.mkdtemp()
        )
        
        # Verificar comentários
        assert "comentarios" in prova_prof
        assert len(prova_prof["comentarios"]) > 0
    
    def test_prova_professor_contem_fontes(self, questoes_mock):
        """Testa que a prova do professor contém fontes bibliográficas."""
        from copy import deepcopy
        
        service = ProvaIndividualService()
        
        prova_prof = service._gerar_prova_professor(
            questoes=deepcopy(questoes_mock),
            config=ConfiguracaoProvaIndividual(
                titulo="Prova",
                questoes_ids=["q1", "q2", "q3"],
                quantidade_alunos=5,
                gerar_pdf=False
            ),
            output_dir=tempfile.mkdtemp()
        )
        
        # Verificar fontes
        assert "fontes_bibliograficas" in prova_prof
    
    def test_prova_professor_questoes_nao_embaralhadas(self, questoes_mock):
        """Testa que a prova do professor mantém ordem original das questões."""
        from copy import deepcopy
        
        service = ProvaIndividualService()
        
        prova_prof = service._gerar_prova_professor(
            questoes=deepcopy(questoes_mock),
            config=ConfiguracaoProvaIndividual(
                titulo="Prova",
                questoes_ids=["q1", "q2", "q3"],
                quantidade_alunos=5,
                gerar_pdf=False
            ),
            output_dir=tempfile.mkdtemp()
        )
        
        # Verificar ordem original
        questoes = prova_prof["questoes"]
        assert questoes[0]["id"] == "q1"
        assert questoes[1]["id"] == "q2"
        assert questoes[2]["id"] == "q3"
    
    def test_prova_professor_resumo_por_tipo(self, questoes_mock):
        """Testa que a prova do professor tem resumo por tipo de questão."""
        from copy import deepcopy
        
        service = ProvaIndividualService()
        
        prova_prof = service._gerar_prova_professor(
            questoes=deepcopy(questoes_mock),
            config=ConfiguracaoProvaIndividual(
                titulo="Prova",
                questoes_ids=["q1", "q2", "q3"],
                quantidade_alunos=5,
                gerar_pdf=False
            ),
            output_dir=tempfile.mkdtemp()
        )
        
        # Verificar resumo por tipo
        assert "resumo_por_tipo" in prova_prof
        resumo = prova_prof["resumo_por_tipo"]
        
        # Deve ter os tipos das questões
        assert sum(resumo.values()) == 3  # 3 questões no total


class TestNumeroTotalProvas:
    """Testes para verificar que são geradas N+1 provas (alunos + professor)."""
    
    def test_30_alunos_gera_31_provas(self):
        """Testa que para 30 alunos são geradas 31 provas."""
        # Simular resultado
        resultado = ResultadoLoteProvas(
            lote_id="test",
            titulo="Prova",
            quantidade_alunos=30,
            provas_geradas=31,
            provas_alunos=[{"numero": i} for i in range(1, 31)],
            prova_professor={"numero": 0, "codigo_prova": "PROFESSOR"}
        )
        
        assert resultado.quantidade_alunos == 30
        assert resultado.provas_geradas == 31
        assert len(resultado.provas_alunos) == 30
        assert resultado.prova_professor is not None
    
    def test_propriedade_total_provas(self):
        """Testa propriedade que retorna todas as provas."""
        resultado = ResultadoLoteProvas(
            lote_id="test",
            titulo="Prova",
            quantidade_alunos=5,
            provas_geradas=6,
            provas_alunos=[{"numero": i} for i in range(1, 6)],
            prova_professor={"numero": 0}
        )
        
        # Todas as provas = professor + alunos
        assert len(resultado.provas) == 6


class TestExplicacoesDetalhadas:
    """Testes para explicações detalhadas de cada alternativa."""
    
    @pytest.fixture
    def questao_com_explicacoes(self):
        """Questão com explicações completas de cada alternativa."""
        return {
            "id": "q1",
            "enunciado": "Qual é a unidade de força no SI?",
            "tipo_questao": "multipla_escolha",
            "alternativas": [
                {
                    "letra": "A",
                    "texto": "Joule",
                    "correta": False,
                    "explicacao": "Joule é a unidade de energia, não de força."
                },
                {
                    "letra": "B",
                    "texto": "Watt",
                    "correta": False,
                    "explicacao": "Watt é a unidade de potência (energia por tempo)."
                },
                {
                    "letra": "C",
                    "texto": "Newton",
                    "correta": True,
                    "explicacao": "Newton (N) é a unidade de força, definida como kg·m/s²."
                },
                {
                    "letra": "D",
                    "texto": "Pascal",
                    "correta": False,
                    "explicacao": "Pascal é a unidade de pressão (força por área)."
                },
                {
                    "letra": "E",
                    "texto": "Hertz",
                    "correta": False,
                    "explicacao": "Hertz é a unidade de frequência (ciclos por segundo)."
                },
            ],
            "explicacao": "A força é uma grandeza vetorial medida em Newtons no SI."
        }
    
    def test_alternativas_incorretas_tem_explicacao(self, questao_com_explicacoes):
        """Testa que alternativas incorretas têm explicação do erro."""
        from copy import deepcopy
        
        service = ProvaIndividualService()
        
        prova_prof = service._gerar_prova_professor(
            questoes=[deepcopy(questao_com_explicacoes)],
            config=ConfiguracaoProvaIndividual(
                titulo="Prova",
                questoes_ids=["q1"],
                quantidade_alunos=5,
                gerar_pdf=False
            ),
            output_dir=tempfile.mkdtemp()
        )
        
        questao = prova_prof["questoes"][0]
        alternativas = questao["alternativas"]
        
        # Verificar que cada alternativa tem status e explicação
        for alt in alternativas:
            assert "status" in alt
            assert "explicacao" in alt
            
            if alt["correta"]:
                assert alt["status"] == "CORRETA"
            else:
                assert alt["status"] == "INCORRETA"
                # Explicação não deve estar vazia
                assert len(alt["explicacao"]) > 0
    
    def test_alternativa_correta_destaque(self, questao_com_explicacoes):
        """Testa que alternativa correta está marcada para destaque."""
        from copy import deepcopy
        
        service = ProvaIndividualService()
        
        prova_prof = service._gerar_prova_professor(
            questoes=[deepcopy(questao_com_explicacoes)],
            config=ConfiguracaoProvaIndividual(
                titulo="Prova",
                questoes_ids=["q1"],
                quantidade_alunos=5,
                gerar_pdf=False
            ),
            output_dir=tempfile.mkdtemp()
        )
        
        questao = prova_prof["questoes"][0]
        
        # Encontrar alternativa correta
        correta = None
        for alt in questao["alternativas"]:
            if alt["correta"]:
                correta = alt
                break
        
        assert correta is not None
        assert correta["destaque"] is True
        assert correta["status"] == "CORRETA"
    
    def test_explicacao_erro_padrao_gerada(self):
        """Testa geração de explicação padrão para alternativas sem explicação."""
        from copy import deepcopy
        
        questao_sem_explicacao = {
            "id": "q1",
            "enunciado": "Teste",
            "alternativas": [
                {"letra": "A", "texto": "Sempre acontece assim", "correta": False},
                {"letra": "B", "texto": "Nunca ocorre", "correta": False},
                {"letra": "C", "texto": "Resposta correta", "correta": True},
            ]
        }
        
        service = ProvaIndividualService()
        
        prova_prof = service._gerar_prova_professor(
            questoes=[deepcopy(questao_sem_explicacao)],
            config=ConfiguracaoProvaIndividual(
                titulo="Prova",
                questoes_ids=["q1"],
                quantidade_alunos=5,
                gerar_pdf=False
            ),
            output_dir=tempfile.mkdtemp()
        )
        
        questao = prova_prof["questoes"][0]
        
        # Alternativas incorretas devem ter explicação gerada
        for alt in questao["alternativas"]:
            if not alt["correta"]:
                assert "explicacao" in alt
                assert len(alt["explicacao"]) > 0


class TestProvaProfessorDissertativa:
    """Testes para questões dissertativas na prova do professor."""
    
    def test_dissertativa_tem_criterios_correcao(self):
        """Testa que dissertativa tem critérios de correção."""
        from copy import deepcopy
        
        questao_dissertativa = {
            "id": "q1",
            "enunciado": "Explique a teoria da relatividade.",
            "tipo_questao": "dissertativa",
            "resposta": "A teoria da relatividade...",
            "alternativas": [],
            "criterios_correcao": [
                "Mencionar Einstein",
                "Explicar E=mc²",
                "Relacionar espaço e tempo"
            ]
        }
        
        service = ProvaIndividualService()
        
        prova_prof = service._gerar_prova_professor(
            questoes=[deepcopy(questao_dissertativa)],
            config=ConfiguracaoProvaIndividual(
                titulo="Prova",
                questoes_ids=["q1"],
                quantidade_alunos=5,
                gerar_pdf=False
            ),
            output_dir=tempfile.mkdtemp()
        )
        
        questao = prova_prof["questoes"][0]
        
        assert "criterios_correcao" in questao
        assert len(questao["criterios_correcao"]) > 0
    
    def test_dissertativa_criterios_padrao(self):
        """Testa que dissertativa sem critérios recebe critérios padrão."""
        from copy import deepcopy
        
        questao_sem_criterios = {
            "id": "q1",
            "enunciado": "Explique algo.",
            "tipo_questao": "dissertativa",
            "resposta": "Resposta",
            "alternativas": []
        }
        
        service = ProvaIndividualService()
        
        prova_prof = service._gerar_prova_professor(
            questoes=[deepcopy(questao_sem_criterios)],
            config=ConfiguracaoProvaIndividual(
                titulo="Prova",
                questoes_ids=["q1"],
                quantidade_alunos=5,
                gerar_pdf=False
            ),
            output_dir=tempfile.mkdtemp()
        )
        
        questao = prova_prof["questoes"][0]
        
        # Deve ter critérios padrão
        assert "criterios_correcao" in questao


class TestGerarExplicacaoErroPadrao:
    """Testes para o método _gerar_explicacao_erro_padrao."""
    
    def test_explicacao_para_negacao(self):
        """Testa explicação para alternativas com negação."""
        service = ProvaIndividualService()
        
        alternativa = {"texto": "Isso nunca acontece"}
        explicacao = service._gerar_explicacao_erro_padrao(alternativa, "A")
        
        assert "negação" in explicacao.lower()
    
    def test_explicacao_para_generalizacao(self):
        """Testa explicação para alternativas com generalização."""
        service = ProvaIndividualService()
        
        alternativa = {"texto": "Sempre ocorre dessa forma"}
        explicacao = service._gerar_explicacao_erro_padrao(alternativa, "B")
        
        assert "generalização" in explicacao.lower()
    
    def test_explicacao_para_restricao(self):
        """Testa explicação para alternativas restritivas."""
        service = ProvaIndividualService()
        
        alternativa = {"texto": "Somente este caso é válido"}
        explicacao = service._gerar_explicacao_erro_padrao(alternativa, "C")
        
        assert "restritiva" in explicacao.lower()
    
    def test_explicacao_generica(self):
        """Testa explicação genérica para outros casos."""
        service = ProvaIndividualService()
        
        alternativa = {"texto": "Uma resposta qualquer"}
        explicacao = service._gerar_explicacao_erro_padrao(alternativa, "D")
        
        assert "incorreta" in explicacao.lower()
        assert "(D)" in explicacao


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

