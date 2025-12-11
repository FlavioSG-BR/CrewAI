"""
Testes unitários para os agentes de geração de questões.

Executa: pytest tests/test_agents.py -v
"""

import pytest
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestAgenteFisica:
    """Testes para o agente de Física."""
    
    def test_importacao(self):
        """Testa se o agente pode ser importado."""
        from backend.agents.fisica import AgenteFisica
        assert AgenteFisica is not None
    
    def test_instanciacao(self):
        """Testa se o agente pode ser instanciado."""
        from backend.agents.fisica import AgenteFisica
        agente = AgenteFisica()
        assert agente is not None
        assert agente.agent is not None
    
    def test_gerar_questao_mru(self):
        """Testa geração de questão MRU."""
        from backend.agents.fisica import AgenteFisica
        agente = AgenteFisica()
        questao = agente.gerar_questao_mru()
        
        assert questao is not None
        assert "enunciado" in questao
        assert "resposta" in questao
        assert "tipo" in questao
        assert len(questao["enunciado"]) > 10
    
    def test_gerar_questao_mruv(self):
        """Testa geração de questão MRUV."""
        from backend.agents.fisica import AgenteFisica
        agente = AgenteFisica()
        questao = agente.gerar_questao_mruv()
        
        assert questao is not None
        assert "enunciado" in questao
        assert "resposta" in questao
    
    def test_gerar_questao_forca(self):
        """Testa geração de questão de forças."""
        from backend.agents.fisica import AgenteFisica
        agente = AgenteFisica()
        questao = agente.gerar_questao_forca()
        
        assert questao is not None
        assert "enunciado" in questao
        assert "dados" in questao
        assert "massa" in questao["dados"]
    
    def test_gerar_questao_por_topico(self):
        """Testa geração por tópico."""
        from backend.agents.fisica import AgenteFisica
        agente = AgenteFisica()
        
        topicos = ["mru", "mruv", "forca", "circuito"]
        for topico in topicos:
            questao = agente.gerar_questao(topico)
            assert questao is not None
            assert "enunciado" in questao


class TestAgenteQuimica:
    """Testes para o agente de Química."""
    
    def test_importacao(self):
        """Testa se o agente pode ser importado."""
        from backend.agents.quimica import AgenteQuimica
        assert AgenteQuimica is not None
    
    def test_instanciacao(self):
        """Testa se o agente pode ser instanciado."""
        from backend.agents.quimica import AgenteQuimica
        agente = AgenteQuimica()
        assert agente is not None
    
    def test_gerar_questao_tabela_periodica(self):
        """Testa geração de questão sobre tabela periódica."""
        from backend.agents.quimica import AgenteQuimica
        agente = AgenteQuimica()
        questao = agente.gerar_questao_tabela_periodica()
        
        assert questao is not None
        assert "enunciado" in questao
        assert "resposta" in questao
        assert "tipo" in questao
    
    def test_gerar_questao_modelo_atomico(self):
        """Testa geração de questão sobre modelo atômico."""
        from backend.agents.quimica import AgenteQuimica
        agente = AgenteQuimica()
        questao = agente.gerar_questao_modelo_atomico()
        
        assert questao is not None
        assert "enunciado" in questao
    
    def test_dados_elementos(self):
        """Testa se os elementos estão definidos."""
        from backend.agents.quimica import ELEMENTOS
        
        assert len(ELEMENTOS) > 0
        assert "O" in ELEMENTOS  # Oxigênio
        assert "C" in ELEMENTOS  # Carbono
        assert ELEMENTOS["O"]["num_atomico"] == 8


class TestAgenteMatematica:
    """Testes para o agente de Matemática."""
    
    def test_importacao(self):
        """Testa se o agente pode ser importado."""
        from backend.agents.matematica import AgenteMatematica
        assert AgenteMatematica is not None
    
    def test_gerar_questao_algebra(self):
        """Testa geração de questão de álgebra."""
        from backend.agents.matematica import AgenteMatematica
        agente = AgenteMatematica()
        questao = agente.gerar_questao_algebra()
        
        assert questao is not None
        assert "enunciado" in questao
        assert "resposta" in questao
        assert "x" in questao["resposta"] or "=" in questao["resposta"]
    
    def test_gerar_questao_geometria(self):
        """Testa geração de questão de geometria."""
        from backend.agents.matematica import AgenteMatematica
        agente = AgenteMatematica()
        questao = agente.gerar_questao_geometria_plana()
        
        assert questao is not None
        assert "enunciado" in questao
        assert "área" in questao["enunciado"].lower() or "calcule" in questao["enunciado"].lower()
    
    def test_gerar_questao_funcoes(self):
        """Testa geração de questão de funções."""
        from backend.agents.matematica import AgenteMatematica
        agente = AgenteMatematica()
        questao = agente.gerar_questao_funcoes()
        
        assert questao is not None
        assert "enunciado" in questao
    
    def test_gerar_questao_probabilidade(self):
        """Testa geração de questão de probabilidade."""
        from backend.agents.matematica import AgenteMatematica
        agente = AgenteMatematica()
        questao = agente.gerar_questao_probabilidade()
        
        assert questao is not None
        assert "enunciado" in questao
        assert "probabilidade" in questao["enunciado"].lower()


class TestAgenteRevisor:
    """Testes para o agente revisor."""
    
    def test_importacao(self):
        """Testa se o agente pode ser importado."""
        from backend.agents.revisor import AgenteRevisor
        assert AgenteRevisor is not None
    
    def test_validar_questao_valida(self):
        """Testa validação de questão válida."""
        from backend.agents.revisor import AgenteRevisor
        revisor = AgenteRevisor()
        
        resultado = revisor.validar_questao(
            "Qual é a velocidade de um carro que percorre 100 km em 2 horas?",
            "50 km/h"
        )
        
        assert resultado is True
    
    def test_validar_questao_invalida(self):
        """Testa validação de questão inválida."""
        from backend.agents.revisor import AgenteRevisor
        revisor = AgenteRevisor()
        
        resultado = revisor.validar_questao("", "")
        assert resultado is False


class TestAgenteClassificador:
    """Testes para o agente classificador."""
    
    def test_importacao(self):
        """Testa se o agente pode ser importado."""
        from backend.agents.classificador import AgenteClassificador
        assert AgenteClassificador is not None
    
    def test_classificar(self):
        """Testa classificação de tópico."""
        from backend.agents.classificador import AgenteClassificador
        classificador = AgenteClassificador()
        
        resultado = classificador.classificar("Movimento Retilíneo Uniforme")
        
        assert resultado is not None
        assert "topico" in resultado
        assert "dificuldade" in resultado


class TestAgenteImagens:
    """Testes para o agente de imagens."""
    
    def test_importacao(self):
        """Testa se o agente pode ser importado."""
        from backend.agents.imagens import AgenteImagens
        assert AgenteImagens is not None
    
    def test_instanciacao(self):
        """Testa se o agente pode ser instanciado."""
        from backend.agents.imagens import AgenteImagens
        agente = AgenteImagens()
        assert agente is not None
        assert os.path.exists(agente.OUTPUT_DIR)
    
    def test_gerar_diagrama_mru(self):
        """Testa geração de diagrama MRU."""
        from backend.agents.imagens import AgenteImagens
        agente = AgenteImagens()
        
        caminho = agente.gerar_diagrama_mru(velocidade=10, tempo=5)
        
        assert caminho is not None
        assert caminho.endswith('.png')
        assert os.path.exists(caminho)
        
        # Limpar arquivo de teste
        os.remove(caminho)
    
    def test_gerar_diagrama_geometria(self):
        """Testa geração de diagrama de geometria."""
        from backend.agents.imagens import AgenteImagens
        agente = AgenteImagens()
        
        caminho = agente.gerar_diagrama_geometrico("circulo", {"raio": 5})
        
        assert caminho is not None
        assert os.path.exists(caminho)
        
        # Limpar arquivo de teste
        os.remove(caminho)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

