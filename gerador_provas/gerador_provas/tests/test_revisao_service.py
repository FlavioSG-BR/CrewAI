"""
Testes para o Serviço de Revisão de Questões.

Executa: pytest tests/test_revisao_service.py -v
"""

import pytest
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.services.revisao_service import (
    RevisaoService, 
    RevisaoQuestao, 
    FonteBibliografica
)


class TestFonteBibliografica:
    """Testes para a classe FonteBibliografica."""
    
    def test_criar_fonte_livro(self):
        """Testa criação de fonte tipo livro."""
        fonte = FonteBibliografica(
            tipo="livro",
            autor="Guyton, A.C.",
            titulo="Tratado de Fisiologia Médica",
            ano=2017,
            edicao="13ª",
            paginas="123-145"
        )
        
        assert fonte.tipo == "livro"
        assert fonte.autor == "Guyton, A.C."
        assert fonte.titulo == "Tratado de Fisiologia Médica"
        assert fonte.ano == 2017
    
    def test_criar_fonte_artigo(self):
        """Testa criação de fonte tipo artigo."""
        fonte = FonteBibliografica(
            tipo="artigo",
            autor="Silva, J.A.",
            titulo="Estudo sobre metabolismo",
            revista="Nature",
            doi="10.1038/xxx"
        )
        
        assert fonte.tipo == "artigo"
        assert fonte.revista == "Nature"
        assert fonte.doi == "10.1038/xxx"
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        fonte = FonteBibliografica(
            tipo="livro",
            autor="Autor Teste",
            titulo="Título Teste",
            ano=2024
        )
        
        resultado = fonte.to_dict()
        
        assert isinstance(resultado, dict)
        assert resultado["tipo"] == "livro"
        assert resultado["autor"] == "Autor Teste"
        assert resultado["titulo"] == "Título Teste"
        assert resultado["ano"] == 2024
        # Campos None não devem estar no dict
        assert "revista" not in resultado
        assert "doi" not in resultado


class TestRevisaoService:
    """Testes para o serviço de revisão."""
    
    @pytest.fixture
    def service(self):
        """Fixture que cria uma instância limpa do serviço."""
        service = RevisaoService()
        # Limpar cache para cada teste
        service._questoes_cache = {}
        service._revisoes_cache = {}
        return service
    
    @pytest.fixture
    def questao_exemplo(self):
        """Fixture com uma questão de exemplo."""
        return {
            "enunciado": "Qual é a velocidade de um corpo em MRU que percorre 100m em 10s?",
            "resposta": "10 m/s",
            "materia": "fisica",
            "topico": "mru",
            "dificuldade": "medio",
            "alternativas": [
                {"letra": "A", "texto": "10 m/s", "correta": True},
                {"letra": "B", "texto": "20 m/s", "correta": False},
                {"letra": "C", "texto": "5 m/s", "correta": False},
                {"letra": "D", "texto": "15 m/s", "correta": False},
                {"letra": "E", "texto": "25 m/s", "correta": False},
            ]
        }
    
    def test_instanciacao(self, service):
        """Testa se o serviço pode ser instanciado."""
        assert service is not None
        assert isinstance(service._questoes_cache, dict)
        assert isinstance(service._revisoes_cache, dict)
    
    def test_adicionar_questao_para_revisao(self, service, questao_exemplo):
        """Testa adição de questão ao fluxo de revisão."""
        questao_id = service.adicionar_questao_para_revisao(questao_exemplo)
        
        assert questao_id is not None
        assert questao_id in service._questoes_cache
        
        questao = service._questoes_cache[questao_id]
        assert questao["status"] == "pendente"
        assert questao["enunciado"] == questao_exemplo["enunciado"]
    
    def test_obter_questao(self, service, questao_exemplo):
        """Testa obtenção de questão pelo ID."""
        questao_id = service.adicionar_questao_para_revisao(questao_exemplo)
        
        questao = service.obter_questao(questao_id)
        
        assert questao is not None
        assert questao["id"] == questao_id
        assert questao["enunciado"] == questao_exemplo["enunciado"]
    
    def test_obter_questao_inexistente(self, service):
        """Testa obtenção de questão que não existe."""
        questao = service.obter_questao("id-inexistente")
        assert questao is None
    
    def test_obter_questoes_pendentes(self, service, questao_exemplo):
        """Testa listagem de questões pendentes."""
        # Adicionar algumas questões
        for i in range(3):
            q = questao_exemplo.copy()
            q["enunciado"] = f"Questão {i+1}"
            service.adicionar_questao_para_revisao(q)
        
        pendentes = service.obter_questoes_pendentes()
        
        assert len(pendentes) == 3
        for q in pendentes:
            assert q["status"] in ["pendente", "rascunho"]
    
    def test_aprovar_questao(self, service, questao_exemplo):
        """Testa aprovação de questão."""
        questao_id = service.adicionar_questao_para_revisao(questao_exemplo)
        
        resultado = service.aprovar_questao(
            questao_id=questao_id,
            comentarios="Questão bem elaborada"
        )
        
        assert resultado["sucesso"] is True
        assert resultado["status"] == "aprovada"
        
        questao = service.obter_questao(questao_id)
        assert questao["status"] == "aprovada"
        assert questao["aprovada_em"] is not None
    
    def test_aprovar_questao_com_fontes(self, service, questao_exemplo):
        """Testa aprovação com fontes bibliográficas."""
        questao_id = service.adicionar_questao_para_revisao(questao_exemplo)
        
        fontes = [
            {"tipo": "livro", "autor": "Halliday", "titulo": "Física"},
            {"tipo": "artigo", "autor": "Silva", "titulo": "Estudo"}
        ]
        
        resultado = service.aprovar_questao(
            questao_id=questao_id,
            fontes=fontes
        )
        
        assert resultado["sucesso"] is True
        
        questao = service.obter_questao(questao_id)
        assert "fontes_bibliograficas" in questao
        assert len(questao["fontes_bibliograficas"]) == 2
    
    def test_rejeitar_questao(self, service, questao_exemplo):
        """Testa rejeição de questão."""
        questao_id = service.adicionar_questao_para_revisao(questao_exemplo)
        
        resultado = service.rejeitar_questao(
            questao_id=questao_id,
            motivo="Enunciado confuso",
            sugestoes="Reformular o texto"
        )
        
        assert resultado["sucesso"] is True
        assert resultado["status"] == "rejeitada"
        
        questao = service.obter_questao(questao_id)
        assert questao["status"] == "rejeitada"
    
    def test_solicitar_correcoes(self, service, questao_exemplo):
        """Testa solicitação de correções."""
        questao_id = service.adicionar_questao_para_revisao(questao_exemplo)
        
        resultado = service.solicitar_correcoes(
            questao_id=questao_id,
            correcoes="Corrigir a unidade de medida",
            comentarios="A resposta está correta mas a unidade precisa ser ajustada"
        )
        
        assert resultado["sucesso"] is True
        assert resultado["status"] == "correcao_pendente"
        
        questao = service.obter_questao(questao_id)
        assert questao["status"] == "correcao_pendente"
    
    def test_obter_questoes_aprovadas(self, service, questao_exemplo):
        """Testa listagem de questões aprovadas."""
        # Adicionar e aprovar questões
        for i in range(3):
            q = questao_exemplo.copy()
            q["enunciado"] = f"Questão aprovada {i+1}"
            questao_id = service.adicionar_questao_para_revisao(q)
            service.aprovar_questao(questao_id)
        
        # Adicionar uma não aprovada
        questao_id = service.adicionar_questao_para_revisao(questao_exemplo)
        
        aprovadas = service.obter_questoes_aprovadas()
        
        assert len(aprovadas) == 3
        for q in aprovadas:
            assert q["status"] == "aprovada"
    
    def test_historico_revisoes(self, service, questao_exemplo):
        """Testa histórico de revisões."""
        questao_id = service.adicionar_questao_para_revisao(questao_exemplo)
        
        # Primeira revisão: correção
        service.solicitar_correcoes(questao_id, "Correção 1")
        
        # Segunda revisão: aprovação
        service.aprovar_questao(questao_id)
        
        revisoes = service.obter_revisoes(questao_id)
        
        assert len(revisoes) == 2
        assert revisoes[0]["status"] == "correcao_pendente"
        assert revisoes[1]["status"] == "aprovada"
    
    def test_aplicar_correcoes(self, service, questao_exemplo):
        """Testa aplicação de correções."""
        questao_id = service.adicionar_questao_para_revisao(questao_exemplo)
        
        novo_enunciado = "Enunciado corrigido"
        resultado = service.aplicar_correcoes(
            questao_id=questao_id,
            novo_enunciado=novo_enunciado
        )
        
        assert resultado["sucesso"] is True
        assert resultado["versao"] == 2
        
        questao = service.obter_questao(questao_id)
        assert questao["enunciado"] == novo_enunciado
        assert questao["versao"] == 2
        assert questao["status"] == "pendente"
    
    def test_adicionar_fonte_bibliografica(self, service, questao_exemplo):
        """Testa adição de fonte bibliográfica."""
        questao_id = service.adicionar_questao_para_revisao(questao_exemplo)
        
        resultado = service.adicionar_fonte_bibliografica(
            questao_id=questao_id,
            fonte={"tipo": "livro", "autor": "Autor", "titulo": "Título"}
        )
        
        assert resultado["sucesso"] is True
        assert resultado["total_fontes"] == 1
        
        # Adicionar mais uma
        resultado = service.adicionar_fonte_bibliografica(
            questao_id=questao_id,
            fonte={"tipo": "artigo", "autor": "Outro", "titulo": "Outro Título"}
        )
        
        assert resultado["total_fontes"] == 2
    
    def test_obter_estatisticas(self, service, questao_exemplo):
        """Testa obtenção de estatísticas."""
        # Adicionar questões com diferentes status
        for i in range(2):
            q = questao_exemplo.copy()
            questao_id = service.adicionar_questao_para_revisao(q)
            service.aprovar_questao(questao_id)
        
        for i in range(3):
            q = questao_exemplo.copy()
            service.adicionar_questao_para_revisao(q)
        
        stats = service.obter_estatisticas()
        
        assert stats["total"] == 5
        assert stats["aprovadas"] == 2
        assert stats["pendentes"] == 3
    
    def test_filtrar_por_materia(self, service):
        """Testa filtro por matéria."""
        # Adicionar questões de diferentes matérias
        materias = ["fisica", "quimica", "matematica"]
        
        for materia in materias:
            questao = {
                "enunciado": f"Questão de {materia}",
                "resposta": "Resposta",
                "materia": materia,
                "dificuldade": "medio"
            }
            service.adicionar_questao_para_revisao(questao)
        
        # Filtrar por física
        questoes_fisica = service.obter_questoes_pendentes(materia="fisica")
        
        assert len(questoes_fisica) == 1
        assert questoes_fisica[0]["materia"] == "fisica"


class TestRevisaoQuestao:
    """Testes para a classe RevisaoQuestao."""
    
    def test_criar_revisao_basica(self):
        """Testa criação de revisão básica."""
        revisao = RevisaoQuestao(
            questao_id="123",
            status="pendente"
        )
        
        assert revisao.questao_id == "123"
        assert revisao.status == "pendente"
        assert revisao.versao == 1
    
    def test_criar_revisao_completa(self):
        """Testa criação de revisão com todos os campos."""
        fonte = FonteBibliografica(
            tipo="livro",
            autor="Autor",
            titulo="Título"
        )
        
        revisao = RevisaoQuestao(
            questao_id="123",
            status="aprovada",
            comentarios="Ótima questão",
            sugestoes_melhoria="Nenhuma",
            fontes_bibliograficas=[fonte],
            nota_qualidade=5,
            precisao_cientifica=True,
            clareza_enunciado=True,
            adequacao_nivel=True,
            versao=2
        )
        
        assert revisao.status == "aprovada"
        assert revisao.nota_qualidade == 5
        assert len(revisao.fontes_bibliograficas) == 1
        assert revisao.precisao_cientifica is True


class TestIntegracaoRevisao:
    """Testes de integração do fluxo de revisão."""
    
    def test_fluxo_completo_aprovacao(self):
        """Testa fluxo completo até aprovação."""
        service = RevisaoService()
        service._questoes_cache = {}
        service._revisoes_cache = {}
        
        # 1. Gerar questão
        questao = {
            "enunciado": "Qual é a fórmula da velocidade?",
            "resposta": "v = d/t",
            "materia": "fisica",
            "topico": "mru",
            "dificuldade": "facil"
        }
        
        # 2. Adicionar para revisão
        questao_id = service.adicionar_questao_para_revisao(questao)
        assert service.obter_questao(questao_id)["status"] == "pendente"
        
        # 3. Solicitar correção
        service.solicitar_correcoes(questao_id, "Adicionar unidades")
        assert service.obter_questao(questao_id)["status"] == "correcao_pendente"
        
        # 4. Aplicar correção
        service.aplicar_correcoes(questao_id, novo_enunciado="Qual é a fórmula da velocidade em m/s?")
        assert service.obter_questao(questao_id)["status"] == "pendente"
        assert service.obter_questao(questao_id)["versao"] == 2
        
        # 5. Aprovar com fontes
        fontes = [{"tipo": "livro", "autor": "Halliday", "titulo": "Física Vol 1"}]
        service.aprovar_questao(questao_id, fontes=fontes)
        
        # Verificar estado final
        questao_final = service.obter_questao(questao_id)
        assert questao_final["status"] == "aprovada"
        assert len(service.obter_revisoes(questao_id)) == 3
    
    def test_fluxo_rejeicao(self):
        """Testa fluxo de rejeição."""
        service = RevisaoService()
        service._questoes_cache = {}
        service._revisoes_cache = {}
        
        questao = {
            "enunciado": "Questão com problema",
            "resposta": "Resposta incorreta",
            "materia": "fisica",
            "dificuldade": "medio"
        }
        
        questao_id = service.adicionar_questao_para_revisao(questao)
        
        # Rejeitar
        service.rejeitar_questao(
            questao_id,
            motivo="A resposta está cientificamente incorreta",
            sugestoes="Consultar referências atualizadas"
        )
        
        questao_final = service.obter_questao(questao_id)
        assert questao_final["status"] == "rejeitada"
        
        # Questão rejeitada não deve aparecer em aprovadas
        aprovadas = service.obter_questoes_aprovadas()
        assert len(aprovadas) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

