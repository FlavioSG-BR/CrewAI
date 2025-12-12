"""
Testes para os utilitários.

Executa: pytest tests/test_utils.py -v
"""

import pytest
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestLogger:
    """Testes para o sistema de logging."""
    
    def test_importacao(self):
        """Testa se o logger pode ser importado."""
        from backend.utils.logger import get_logger, log_questao_gerada
        assert get_logger is not None
        assert log_questao_gerada is not None
    
    def test_get_logger(self):
        """Testa obtenção de logger."""
        from backend.utils.logger import get_logger
        
        logger = get_logger("teste")
        assert logger is not None
        assert logger.name == "teste"
    
    def test_log_questao_gerada(self):
        """Testa log de questão gerada."""
        from backend.utils.logger import log_questao_gerada
        
        # Não deve lançar exceção
        log_questao_gerada("fisica")
        log_questao_gerada("quimica", "tabela_periodica")
        log_questao_gerada("matematica", "algebra", sucesso=False)


class TestValidator:
    """Testes para o validador de respostas."""
    
    def test_importacao(self):
        """Testa se o validador pode ser importado."""
        from backend.utils.validator import validar_resposta
        assert validar_resposta is not None
    
    def test_validar_resposta_igual(self):
        """Testa validação de respostas iguais."""
        from backend.utils.validator import validar_resposta
        
        resultado = validar_resposta("5", "5")
        assert resultado == True
    
    def test_validar_resposta_equivalente(self):
        """Testa validação de respostas matematicamente equivalentes."""
        from backend.utils.validator import validar_resposta
        
        resultado = validar_resposta("x**2", "x^2")
        assert resultado == True
    
    def test_validar_resposta_diferente(self):
        """Testa validação de respostas diferentes."""
        from backend.utils.validator import validar_resposta
        
        resultado = validar_resposta("5", "10")
        assert resultado == False
    
    def test_validar_resposta_invalida(self):
        """Testa validação com entrada inválida."""
        from backend.utils.validator import validar_resposta
        
        resultado = validar_resposta("abc", "123")
        assert resultado == False


class TestConfig:
    """Testes para as configurações."""
    
    def test_importacao(self):
        """Testa se as configurações podem ser importadas."""
        from config import settings
        assert settings is not None
    
    def test_configuracoes_padrao(self):
        """Testa valores padrão das configurações."""
        from config import settings
        
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 5000
        assert "postgresql" in settings.DATABASE_URL or "sqlite" in settings.DATABASE_URL
    
    def test_diretorios(self):
        """Testa configurações de diretórios."""
        from config import settings
        
        assert settings.LOG_DIR is not None
        assert settings.OUTPUT_DIR is not None
        assert settings.DIAGRAMAS_DIR is not None


class TestLatexGenerator:
    """Testes para o gerador de LaTeX."""
    
    def test_importacao(self):
        """Testa se o gerador pode ser importado."""
        from backend.utils.latex_generator import gerar_pdf, gerar_latex
        assert gerar_pdf is not None
        assert gerar_latex is not None
    
    def test_exportar_questao_latex(self):
        """Testa exportação de questão para LaTeX."""
        from backend.utils.latex_generator import exportar_questao_latex
        
        questao = {
            "enunciado": "Qual é 2 + 2?",
            "resposta": "4",
            "tipo": "Matemática"
        }
        
        latex = exportar_questao_latex(questao)
        
        assert latex is not None
        assert "2 + 2" in latex
        assert "4" in latex


class TestDashboard:
    """Testes para o dashboard."""
    
    def test_importacao(self):
        """Testa se o dashboard pode ser importado."""
        from backend.utils.dashboard import gerar_grafico_acertos
        assert gerar_grafico_acertos is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

