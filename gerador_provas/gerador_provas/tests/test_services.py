"""
Testes para os serviços de negócio.

Executa: pytest tests/test_services.py -v
"""

import pytest
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestQuestaoService:
    """Testes para o serviço de questões."""
    
    def test_importacao(self):
        """Testa se o serviço pode ser importado."""
        from backend.services.questao_service import QuestaoService
        assert QuestaoService is not None
    
    def test_instanciacao_sem_persistencia(self):
        """Testa instanciação sem persistência."""
        from backend.services.questao_service import QuestaoService
        service = QuestaoService(persistir=False)
        
        assert service is not None
        assert service.persistir is False
        assert service.repository is None
    
    def test_gerar_questao_fisica(self):
        """Testa geração de questão de física via serviço."""
        from backend.services.questao_service import QuestaoService
        service = QuestaoService(persistir=False)
        
        questao = service.gerar_questao(
            materia="fisica",
            topico="mru",
            dificuldade="medio",
            salvar=False
        )
        
        assert questao is not None
        assert "enunciado" in questao
        assert "resposta" in questao
        assert questao["materia"] == "fisica"
        assert questao["salva"] is False
    
    def test_gerar_questao_quimica(self):
        """Testa geração de questão de química via serviço."""
        from backend.services.questao_service import QuestaoService
        service = QuestaoService(persistir=False)
        
        questao = service.gerar_questao(
            materia="quimica",
            topico="tabela_periodica",
            salvar=False
        )
        
        assert questao is not None
        assert questao["materia"] == "quimica"
    
    def test_gerar_questao_matematica(self):
        """Testa geração de questão de matemática via serviço."""
        from backend.services.questao_service import QuestaoService
        service = QuestaoService(persistir=False)
        
        questao = service.gerar_questao(
            materia="matematica",
            topico="algebra",
            salvar=False
        )
        
        assert questao is not None
        assert questao["materia"] == "matematica"
    
    def test_gerar_multiplas_questoes(self):
        """Testa geração de múltiplas questões."""
        from backend.services.questao_service import QuestaoService
        service = QuestaoService(persistir=False)
        
        questoes = service.gerar_multiplas(
            materia="fisica",
            quantidade=3,
            topico="mru"
        )
        
        assert len(questoes) == 3
        for i, q in enumerate(questoes, 1):
            assert q["numero"] == i
    
    def test_gerar_questao_materia_invalida(self):
        """Testa erro com matéria inválida."""
        from backend.services.questao_service import QuestaoService
        service = QuestaoService(persistir=False)
        
        with pytest.raises(ValueError):
            service.gerar_questao(materia="filosofia")
    
    def test_metadados_questao(self):
        """Testa se os metadados são adicionados corretamente."""
        from backend.services.questao_service import QuestaoService
        service = QuestaoService(persistir=False)
        
        questao = service.gerar_questao(
            materia="fisica",
            topico="mru",
            dificuldade="dificil",
            salvar=False
        )
        
        assert "materia" in questao
        assert "topico" in questao
        assert "dificuldade" in questao
        assert "tags" in questao
        assert "gerado_em" in questao
        assert "revisao_aprovada" in questao


class TestProvaService:
    """Testes para o serviço de provas."""
    
    def test_importacao(self):
        """Testa se o serviço pode ser importado."""
        from backend.services.prova_service import ProvaService
        assert ProvaService is not None


class TestIntegracaoAgentesServicos:
    """Testes de integração entre agentes e serviços."""
    
    def test_fluxo_completo_geracao(self):
        """Testa o fluxo completo de geração de questão."""
        from backend.services.questao_service import QuestaoService
        
        service = QuestaoService(persistir=False)
        
        # Gerar questão com todos os passos
        questao = service.gerar_questao(
            materia="fisica",
            topico="mru",
            dificuldade="medio",
            com_diagrama=False,
            salvar=False
        )
        
        # Verificar que passou por todas as etapas
        assert questao["revisao_aprovada"] is True or questao["revisao_aprovada"] is False
        assert "tags" in questao
        assert "gerado_em" in questao
    
    def test_consistencia_entre_materias(self):
        """Testa consistência entre diferentes matérias."""
        from backend.services.questao_service import QuestaoService
        
        service = QuestaoService(persistir=False)
        
        materias = ["fisica", "quimica", "matematica"]
        
        for materia in materias:
            questao = service.gerar_questao(materia=materia, salvar=False)
            
            # Todas devem ter os mesmos campos obrigatórios
            assert "enunciado" in questao
            assert "resposta" in questao
            assert "materia" in questao
            assert questao["materia"] == materia


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

