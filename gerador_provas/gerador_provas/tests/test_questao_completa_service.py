"""
Testes para o Serviço de Questão Completa.

Executa: pytest tests/test_questao_completa_service.py -v
"""

import pytest
import sys
import os
import json

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.services.questao_completa_service import (
    QuestaoCompletaService,
    QuestaoCompleta,
    AlternativaComentada,
    ErroComum,
    FonteBibliografica,
    CriterioCorrecao
)


class TestAlternativaComentada:
    """Testes para o dataclass AlternativaComentada."""
    
    def test_criar_alternativa_correta(self):
        """Testa criação de alternativa correta."""
        alt = AlternativaComentada(
            letra="C",
            texto="Newton",
            correta=True,
            explicacao="Newton é a unidade de força no SI, definida como kg·m/s²."
        )
        
        assert alt.letra == "C"
        assert alt.correta is True
        assert "Newton" in alt.texto
        assert "força" in alt.explicacao
    
    def test_criar_alternativa_incorreta(self):
        """Testa criação de alternativa incorreta com erro conceitual."""
        alt = AlternativaComentada(
            letra="A",
            texto="Joule",
            correta=False,
            explicacao="Joule é unidade de energia, não de força.",
            erro_conceitual="Confusão entre grandezas físicas",
            dica_professor="Aluno confunde força com energia"
        )
        
        assert alt.correta is False
        assert alt.erro_conceitual is not None
        assert alt.dica_professor is not None


class TestQuestaoCompleta:
    """Testes para o dataclass QuestaoCompleta."""
    
    def test_criar_questao_multipla_escolha(self):
        """Testa criação de questão de múltipla escolha."""
        alternativas = [
            AlternativaComentada("A", "Joule", False, "Unidade de energia"),
            AlternativaComentada("B", "Watt", False, "Unidade de potência"),
            AlternativaComentada("C", "Newton", True, "Unidade de força no SI"),
        ]
        
        questao = QuestaoCompleta(
            id="q1",
            tipo="multipla_escolha",
            enunciado="Qual é a unidade de força no SI?",
            alternativas=alternativas,
            explicacao_geral="A força é medida em Newtons no Sistema Internacional."
        )
        
        assert questao.tipo == "multipla_escolha"
        assert len(questao.alternativas) == 3
        assert any(alt.correta for alt in questao.alternativas)
    
    def test_criar_questao_dissertativa(self):
        """Testa criação de questão dissertativa."""
        criterios = [
            CriterioCorrecao("Definir o conceito", 3.0, True),
            CriterioCorrecao("Dar exemplo", 2.0, False),
        ]
        
        questao = QuestaoCompleta(
            id="q2",
            tipo="dissertativa",
            enunciado="Explique a teoria da relatividade.",
            resposta="A teoria da relatividade de Einstein...",
            criterios_correcao=criterios,
            explicacao_geral="Conceito fundamental da física moderna."
        )
        
        assert questao.tipo == "dissertativa"
        assert questao.resposta is not None
        assert len(questao.criterios_correcao) == 2


class TestQuestaoCompletaService:
    """Testes para o serviço QuestaoCompletaService."""
    
    @pytest.fixture
    def service(self):
        return QuestaoCompletaService()
    
    @pytest.fixture
    def questao_multipla_escolha(self, service):
        """Questão de múltipla escolha completa para testes."""
        return service.criar_questao_completa(
            tipo="multipla_escolha",
            enunciado="Qual é a unidade de força no Sistema Internacional (SI)?",
            alternativas=[
                {
                    "letra": "A",
                    "texto": "Joule",
                    "correta": False,
                    "explicacao": "Joule (J) é a unidade de ENERGIA, não de força. É definido como 1 J = 1 N·m.",
                    "erro_conceitual": "Confusão entre força e energia"
                },
                {
                    "letra": "B",
                    "texto": "Watt",
                    "correta": False,
                    "explicacao": "Watt (W) é a unidade de POTÊNCIA, que mede energia por tempo. 1 W = 1 J/s.",
                    "erro_conceitual": "Confusão entre força e potência"
                },
                {
                    "letra": "C",
                    "texto": "Newton",
                    "correta": True,
                    "explicacao": "Newton (N) é a unidade de FORÇA no SI, definida como a força necessária para acelerar 1 kg a 1 m/s². Fórmula: 1 N = 1 kg·m/s².",
                    "conceitos_envolvidos": ["Segunda lei de Newton", "F = m·a"]
                },
                {
                    "letra": "D",
                    "texto": "Pascal",
                    "correta": False,
                    "explicacao": "Pascal (Pa) é a unidade de PRESSÃO, que é força por área. 1 Pa = 1 N/m².",
                    "erro_conceitual": "Confusão entre força e pressão"
                },
                {
                    "letra": "E",
                    "texto": "Hertz",
                    "correta": False,
                    "explicacao": "Hertz (Hz) é a unidade de FREQUÊNCIA, medindo ciclos por segundo. 1 Hz = 1/s.",
                    "erro_conceitual": "Grandeza completamente diferente"
                }
            ],
            explicacao_geral="A força é uma grandeza vetorial que representa a interação entre corpos. No SI, é medida em Newtons (N). A segunda lei de Newton estabelece F = m·a.",
            fontes=[
                {
                    "tipo": "livro",
                    "autor": "Halliday, Resnick, Walker",
                    "titulo": "Fundamentos de Física",
                    "edicao": "10ª",
                    "ano": 2016,
                    "relevancia": "Definição formal de força e unidades"
                }
            ],
            erros_comuns=[
                {
                    "erro": "Confundir força com energia",
                    "frequencia": "alta",
                    "como_identificar": "Aluno marca Joule como resposta",
                    "como_corrigir": "Revisar conceito de grandezas físicas e suas unidades"
                },
                {
                    "erro": "Esquecer a fórmula F = m·a",
                    "frequencia": "media",
                    "como_identificar": "Aluno não consegue derivar a unidade",
                    "como_corrigir": "Praticar análise dimensional"
                }
            ],
            dificuldade="facil",
            nivel_cognitivo="lembrar",
            tempo_estimado_min=2,
            palavras_chave=["força", "Newton", "SI", "unidade"]
        )
    
    def test_criar_questao_completa(self, service):
        """Testa criação de questão completa."""
        questao = service.criar_questao_completa(
            tipo="multipla_escolha",
            enunciado="Teste",
            alternativas=[
                {"letra": "A", "texto": "Opção A", "correta": False, "explicacao": "Errada"},
                {"letra": "B", "texto": "Opção B", "correta": True, "explicacao": "Correta"},
            ]
        )
        
        assert questao is not None
        assert questao.tipo == "multipla_escolha"
        assert len(questao.alternativas) == 2
    
    def test_validar_completude_questao_completa(self, service, questao_multipla_escolha):
        """Testa validação de questão completa."""
        resultado = service.validar_completude(questao_multipla_escolha)
        
        assert resultado['completa'] is True
        assert resultado['porcentagem'] >= 80
        assert len(resultado['itens_faltando']) == 0
    
    def test_validar_completude_questao_incompleta(self, service):
        """Testa validação de questão incompleta."""
        questao = service.criar_questao_completa(
            tipo="multipla_escolha",
            enunciado="Teste",
            alternativas=[
                {"letra": "A", "texto": "A", "correta": True, "explicacao": ""},
                {"letra": "B", "texto": "B", "correta": False, "explicacao": ""},
            ]
        )
        
        resultado = service.validar_completude(questao)
        
        assert resultado['completa'] is False
        assert len(resultado['itens_faltando']) > 0
    
    def test_para_prova_aluno(self, service, questao_multipla_escolha):
        """Testa conversão para prova do aluno (sem explicações)."""
        prova_aluno = service.para_prova_aluno(questao_multipla_escolha)
        
        # Deve ter enunciado
        assert 'enunciado' in prova_aluno
        
        # Deve ter alternativas
        assert 'alternativas' in prova_aluno
        assert len(prova_aluno['alternativas']) == 5
        
        # Alternativas NÃO devem ter explicações
        for alt in prova_aluno['alternativas']:
            assert 'explicacao' not in alt
            assert 'correta' not in alt
            assert 'erro_conceitual' not in alt
    
    def test_para_prova_professor(self, service, questao_multipla_escolha):
        """Testa conversão para prova do professor (com tudo)."""
        prova_prof = service.para_prova_professor(questao_multipla_escolha)
        
        # Deve ter enunciado
        assert 'enunciado' in prova_prof
        
        # Deve ter alternativas com explicações
        assert 'alternativas' in prova_prof
        for alt in prova_prof['alternativas']:
            assert 'letra' in alt
            assert 'texto' in alt
            assert 'correta' in alt
            assert 'status' in alt
            assert 'explicacao' in alt
        
        # Deve ter explicação geral
        assert 'explicacao_geral' in prova_prof
        assert prova_prof['explicacao_geral'] is not None
        
        # Deve ter erros comuns
        assert 'erros_comuns' in prova_prof
        assert len(prova_prof['erros_comuns']) > 0
        
        # Deve ter fontes
        assert 'fontes_bibliograficas' in prova_prof
        assert len(prova_prof['fontes_bibliograficas']) > 0
    
    def test_para_banco_dados(self, service, questao_multipla_escolha):
        """Testa conversão para formato do banco de dados."""
        db_data = service.para_banco_dados(questao_multipla_escolha)
        
        assert 'id' in db_data
        assert 'tipo' in db_data
        assert 'enunciado' in db_data
        assert 'alternativas_comentadas' in db_data
        assert 'explicacao_geral' in db_data
        assert 'erros_comuns' in db_data
        assert 'fontes_bibliograficas' in db_data
        
        # Deve ser JSON válido
        alt_json = json.loads(db_data['alternativas_comentadas'])
        assert 'alternativas' in alt_json
    
    def test_do_banco_dados(self, service, questao_multipla_escolha):
        """Testa conversão de volta do banco de dados."""
        # Primeiro converter para DB
        db_data = service.para_banco_dados(questao_multipla_escolha)
        
        # Simular dados do banco (strings JSON)
        db_row = {
            'id': db_data['id'],
            'tipo': db_data['tipo'],
            'enunciado': db_data['enunciado'],
            'alternativas_comentadas': db_data['alternativas_comentadas'],
            'explicacao_geral': db_data['explicacao_geral'],
            'erros_comuns': db_data['erros_comuns'],
            'fontes_bibliograficas': db_data['fontes_bibliograficas'],
            'dificuldade': 'facil',
            'status': 'rascunho'
        }
        
        # Converter de volta
        questao_recuperada = service.do_banco_dados(db_row)
        
        assert questao_recuperada.id == questao_multipla_escolha.id
        assert questao_recuperada.tipo == questao_multipla_escolha.tipo
        assert len(questao_recuperada.alternativas) == 5
        assert len(questao_recuperada.erros_comuns) > 0


class TestValidacaoCompletude:
    """Testes específicos para validação de completude."""
    
    @pytest.fixture
    def service(self):
        return QuestaoCompletaService()
    
    def test_dissertativa_precisa_resposta(self, service):
        """Testa que dissertativa precisa de resposta."""
        questao = service.criar_questao_completa(
            tipo="dissertativa",
            enunciado="Explique algo.",
            resposta=None,  # Sem resposta
            explicacao_geral="Explicação"
        )
        
        resultado = service.validar_completude(questao)
        
        assert 'Resposta esperada' in resultado['itens_faltando']
    
    def test_dissertativa_recomenda_criterios(self, service):
        """Testa que dissertativa recomenda critérios de correção."""
        questao = service.criar_questao_completa(
            tipo="dissertativa",
            enunciado="Explique algo.",
            resposta="Resposta modelo.",
            explicacao_geral="Explicação"
        )
        
        resultado = service.validar_completude(questao)
        
        # Critérios são recomendados (aviso), não obrigatórios
        assert any("critérios" in aviso.lower() for aviso in resultado['avisos'])
    
    def test_multipla_escolha_precisa_correta(self, service):
        """Testa que múltipla escolha precisa de alternativa correta."""
        questao = service.criar_questao_completa(
            tipo="multipla_escolha",
            enunciado="Teste",
            alternativas=[
                {"letra": "A", "texto": "A", "correta": False, "explicacao": "Errada"},
                {"letra": "B", "texto": "B", "correta": False, "explicacao": "Errada"},
            ],
            explicacao_geral="Explicação"
        )
        
        resultado = service.validar_completude(questao)
        
        assert 'Alternativa correta não marcada' in resultado['itens_faltando']


class TestConversaoFormatos:
    """Testes para conversão entre formatos."""
    
    @pytest.fixture
    def service(self):
        return QuestaoCompletaService()
    
    def test_prova_aluno_nao_expoe_resposta(self, service):
        """Testa que prova do aluno não expõe respostas."""
        questao = service.criar_questao_completa(
            tipo="multipla_escolha",
            enunciado="Teste",
            alternativas=[
                {"letra": "A", "texto": "Errada", "correta": False, "explicacao": "Motivo"},
                {"letra": "B", "texto": "Certa", "correta": True, "explicacao": "Motivo"},
            ]
        )
        
        prova_aluno = service.para_prova_aluno(questao)
        
        # Nenhuma alternativa deve indicar se é correta
        for alt in prova_aluno['alternativas']:
            assert 'correta' not in alt
    
    def test_prova_professor_expoe_tudo(self, service):
        """Testa que prova do professor expõe todas as informações."""
        questao = service.criar_questao_completa(
            tipo="multipla_escolha",
            enunciado="Teste",
            alternativas=[
                {"letra": "A", "texto": "Errada", "correta": False, 
                 "explicacao": "Por que está errada", "erro_conceitual": "Tipo de erro"},
                {"letra": "B", "texto": "Certa", "correta": True, 
                 "explicacao": "Por que está certa"},
            ],
            explicacao_geral="Explicação geral",
            erros_comuns=[
                {"erro": "Erro comum", "frequencia": "alta", 
                 "como_identificar": "Como", "como_corrigir": "Correção"}
            ]
        )
        
        prova_prof = service.para_prova_professor(questao)
        
        # Alternativas devem ter tudo
        for alt in prova_prof['alternativas']:
            assert 'correta' in alt
            assert 'explicacao' in alt
            assert 'status' in alt
        
        # Erros comuns devem estar presentes
        assert len(prova_prof['erros_comuns']) > 0


class TestGeracaoPrompt:
    """Testes para geração de prompts para IA."""
    
    @pytest.fixture
    def service(self):
        return QuestaoCompletaService()
    
    def test_prompt_multipla_escolha(self, service):
        """Testa geração de prompt para múltipla escolha."""
        prompt = service.gerar_prompt_ia(
            tipo="multipla_escolha",
            topico="Leis de Newton",
            dificuldade="medio"
        )
        
        assert "multipla escolha" in prompt.lower() or "múltipla escolha" in prompt.lower()
        assert "Leis de Newton" in prompt
        assert "alternativas" in prompt.lower()
        assert "explicação" in prompt.lower()
    
    def test_prompt_dissertativa(self, service):
        """Testa geração de prompt para dissertativa."""
        prompt = service.gerar_prompt_ia(
            tipo="dissertativa",
            topico="Fotossíntese",
            dificuldade="dificil"
        )
        
        assert "dissertativa" in prompt.lower()
        assert "Fotossíntese" in prompt
        assert "critérios" in prompt.lower()
    
    def test_prompt_verdadeiro_falso(self, service):
        """Testa geração de prompt para V/F."""
        prompt = service.gerar_prompt_ia(
            tipo="verdadeiro_falso",
            topico="Teoria da Evolução"
        )
        
        assert "verdadeiro" in prompt.lower() or "falso" in prompt.lower()
        assert "Teoria da Evolução" in prompt


class TestQuestaoNumerica:
    """Testes para questões numéricas."""
    
    @pytest.fixture
    def service(self):
        return QuestaoCompletaService()
    
    def test_criar_questao_numerica(self, service):
        """Testa criação de questão numérica."""
        questao = service.criar_questao_completa(
            tipo="numerica",
            enunciado="Calcule a área de um círculo com raio 5cm.",
            resposta="78.54",
            tolerancia=0.1,
            explicacao_geral="Área = π × r²",
            resolucao_passo_a_passo="1. A = π × r²\n2. A = 3.14159 × 5²\n3. A = 78.54 cm²"
        )
        
        assert questao.tipo == "numerica"
        assert questao.resposta == "78.54"
        assert questao.tolerancia == 0.1
        assert questao.resolucao_passo_a_passo is not None
    
    def test_numerica_prova_aluno_mostra_tolerancia(self, service):
        """Testa que prova do aluno mostra tolerância para numéricas."""
        questao = service.criar_questao_completa(
            tipo="numerica",
            enunciado="Calcule...",
            resposta="42",
            tolerancia=0.5
        )
        
        prova_aluno = service.para_prova_aluno(questao)
        
        # Aluno precisa saber a precisão esperada
        assert prova_aluno.get('tolerancia') == 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

