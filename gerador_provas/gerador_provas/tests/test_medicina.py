# -*- coding: utf-8 -*-
"""
Testes unitários para os agentes de Medicina.

Executa: pytest tests/test_medicina.py -v
"""

import pytest
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestAgenteFarmacologia:
    """Testes para o agente de Farmacologia."""
    
    def test_importacao(self):
        """Testa se o agente pode ser importado."""
        from backend.agents.medicina.farmacologia import AgenteFarmacologia
        assert AgenteFarmacologia is not None
    
    def test_instanciacao(self):
        """Testa se o agente pode ser instanciado."""
        from backend.agents.medicina.farmacologia import AgenteFarmacologia
        agente = AgenteFarmacologia()
        assert agente is not None
        assert agente.agent is not None
    
    def test_gerar_questao_farmacocinetica(self):
        """Testa geração de questão de farmacocinética."""
        from backend.agents.medicina.farmacologia import AgenteFarmacologia
        agente = AgenteFarmacologia()
        
        for dificuldade in ["facil", "medio", "dificil"]:
            questao = agente.gerar_questao_farmacocinetica(dificuldade)
            assert questao is not None
            assert "enunciado" in questao
            assert "resposta" in questao
    
    def test_gerar_questao_antibioticos(self):
        """Testa geração de questão sobre antibióticos."""
        from backend.agents.medicina.farmacologia import AgenteFarmacologia
        agente = AgenteFarmacologia()
        questao = agente.gerar_questao_antibioticos("medio")
        
        assert questao is not None
        assert "enunciado" in questao
        assert "resposta" in questao
    
    def test_gerar_questao_geral(self):
        """Testa o método geral de geração."""
        from backend.agents.medicina.farmacologia import AgenteFarmacologia
        agente = AgenteFarmacologia()
        
        questao = agente.gerar_questao("antibioticos", "dificil")
        assert questao is not None
        assert "enunciado" in questao
    
    def test_gerar_questao_cardiovascular(self):
        """Testa geração de questão cardiovascular."""
        from backend.agents.medicina.farmacologia import AgenteFarmacologia
        agente = AgenteFarmacologia()
        questao = agente.gerar_questao_cardiovascular("medio")
        assert questao is not None
        assert "enunciado" in questao
    
    def test_gerar_questao_snc(self):
        """Testa geração de questão sobre SNC."""
        from backend.agents.medicina.farmacologia import AgenteFarmacologia
        agente = AgenteFarmacologia()
        questao = agente.gerar_questao_snc("dificil")
        assert questao is not None


class TestAgenteHistologia:
    """Testes para o agente de Histologia."""
    
    def test_importacao(self):
        """Testa se o agente pode ser importado."""
        from backend.agents.medicina.histologia import AgenteHistologia
        assert AgenteHistologia is not None
    
    def test_instanciacao(self):
        """Testa se o agente pode ser instanciado."""
        from backend.agents.medicina.histologia import AgenteHistologia
        agente = AgenteHistologia()
        assert agente is not None
    
    def test_gerar_questao_tecidos(self):
        """Testa geração de questão sobre tecidos."""
        from backend.agents.medicina.histologia import AgenteHistologia
        agente = AgenteHistologia()
        
        questao = agente.gerar_questao_tecidos("medio")
        assert questao is not None
        assert "enunciado" in questao
        assert "resposta" in questao
    
    def test_gerar_questao_coloracoes(self):
        """Testa geração de questão sobre colorações."""
        from backend.agents.medicina.histologia import AgenteHistologia
        agente = AgenteHistologia()
        
        questao = agente.gerar_questao_coloracoes("facil")
        assert "enunciado" in questao
    
    def test_gerar_questao_sistema_digestorio(self):
        """Testa geração de questão sobre sistema digestório."""
        from backend.agents.medicina.histologia import AgenteHistologia
        agente = AgenteHistologia()
        
        questao = agente.gerar_questao_sistema_digestorio("dificil")
        assert "enunciado" in questao


class TestAgenteAnatomia:
    """Testes para o agente de Anatomia."""
    
    def test_importacao(self):
        """Testa se o agente pode ser importado."""
        from backend.agents.medicina.anatomia import AgenteAnatomia
        assert AgenteAnatomia is not None
    
    def test_gerar_questao_osteologia(self):
        """Testa geração de questão de osteologia."""
        from backend.agents.medicina.anatomia import AgenteAnatomia
        agente = AgenteAnatomia()
        
        questao = agente.gerar_questao_osteologia("medio")
        assert questao is not None
        assert "enunciado" in questao
    
    def test_gerar_questao_cardiovascular(self):
        """Testa geração de questão cardiovascular."""
        from backend.agents.medicina.anatomia import AgenteAnatomia
        agente = AgenteAnatomia()
        
        questao = agente.gerar_questao_sistema_cardiovascular("dificil")
        assert "enunciado" in questao
        assert "resposta" in questao
    
    def test_gerar_questao_sistema_nervoso(self):
        """Testa geração de questão sobre sistema nervoso."""
        from backend.agents.medicina.anatomia import AgenteAnatomia
        agente = AgenteAnatomia()
        
        questao = agente.gerar_questao_sistema_nervoso("medio")
        assert "enunciado" in questao


class TestAgenteFisiologia:
    """Testes para o agente de Fisiologia."""
    
    def test_importacao(self):
        """Testa se o agente pode ser importado."""
        from backend.agents.medicina.fisiologia import AgenteFisiologia
        assert AgenteFisiologia is not None
    
    def test_gerar_questao_cardiovascular(self):
        """Testa geração de questão cardiovascular."""
        from backend.agents.medicina.fisiologia import AgenteFisiologia
        agente = AgenteFisiologia()
        
        questao = agente.gerar_questao_cardiovascular("medio")
        assert questao is not None
        assert "enunciado" in questao
    
    def test_gerar_questao_renal(self):
        """Testa geração de questão renal."""
        from backend.agents.medicina.fisiologia import AgenteFisiologia
        agente = AgenteFisiologia()
        
        questao = agente.gerar_questao_renal("facil")
        assert "enunciado" in questao
    
    def test_gerar_questao_endocrina(self):
        """Testa geração de questão endócrina."""
        from backend.agents.medicina.fisiologia import AgenteFisiologia
        agente = AgenteFisiologia()
        
        questao = agente.gerar_questao_endocrina("dificil")
        assert "enunciado" in questao


class TestAgentePatologia:
    """Testes para o agente de Patologia."""
    
    def test_importacao(self):
        """Testa se o agente pode ser importado."""
        from backend.agents.medicina.patologia import AgentePatologia
        assert AgentePatologia is not None
    
    def test_gerar_questao_geral(self):
        """Testa geração de questão de patologia geral."""
        from backend.agents.medicina.patologia import AgentePatologia
        agente = AgentePatologia()
        
        questao = agente.gerar_questao_patologia_geral("medio")
        assert questao is not None
        assert "enunciado" in questao
    
    def test_gerar_questao_neoplasias(self):
        """Testa geração de questão sobre neoplasias."""
        from backend.agents.medicina.patologia import AgentePatologia
        agente = AgentePatologia()
        
        questao = agente.gerar_questao_neoplasias("dificil")
        assert "enunciado" in questao


class TestAgenteBioquimica:
    """Testes para o agente de Bioquímica."""
    
    def test_importacao(self):
        """Testa se o agente pode ser importado."""
        from backend.agents.medicina.bioquimica import AgenteBioquimica
        assert AgenteBioquimica is not None
    
    def test_gerar_questao_metabolismo(self):
        """Testa geração de questão sobre metabolismo."""
        from backend.agents.medicina.bioquimica import AgenteBioquimica
        agente = AgenteBioquimica()
        
        questao = agente.gerar_questao_metabolismo("medio")
        assert questao is not None
        assert "enunciado" in questao
    
    def test_gerar_questao_enzimas(self):
        """Testa geração de questão sobre enzimas."""
        from backend.agents.medicina.bioquimica import AgenteBioquimica
        agente = AgenteBioquimica()
        
        questao = agente.gerar_questao_enzimas("facil")
        assert questao is not None


class TestAgenteMicrobiologia:
    """Testes para o agente de Microbiologia."""
    
    def test_importacao(self):
        """Testa se o agente pode ser importado."""
        from backend.agents.medicina.microbiologia import AgenteMicrobiologia
        assert AgenteMicrobiologia is not None
    
    def test_gerar_questao_bacteriologia(self):
        """Testa geração de questão de bacteriologia."""
        from backend.agents.medicina.microbiologia import AgenteMicrobiologia
        agente = AgenteMicrobiologia()
        
        questao = agente.gerar_questao_bacteriologia("medio")
        assert questao is not None
        assert "enunciado" in questao
    
    def test_gerar_questao_imunologia(self):
        """Testa geração de questão de imunologia."""
        from backend.agents.medicina.microbiologia import AgenteMicrobiologia
        agente = AgenteMicrobiologia()
        
        questao = agente.gerar_questao_imunologia("dificil")
        assert "enunciado" in questao


class TestAgenteCasosClinico:
    """Testes para o agente de Casos Clínicos."""
    
    def test_importacao(self):
        """Testa se o agente pode ser importado."""
        from backend.agents.medicina.casos_clinicos import AgenteCasosClinico
        assert AgenteCasosClinico is not None
    
    def test_gerar_questao(self):
        """Testa geração de caso clínico via método geral."""
        from backend.agents.medicina.casos_clinicos import AgenteCasosClinico
        agente = AgenteCasosClinico()
        
        for dificuldade in ["facil", "medio", "dificil"]:
            questao = agente.gerar_questao(dificuldade=dificuldade)
            assert questao is not None
            assert "enunciado" in questao
            assert "resposta" in questao


class TestIntegracaoAgentes:
    """Testes de integração entre agentes médicos."""
    
    def test_todos_agentes_importaveis(self):
        """Testa se todos os agentes podem ser importados do módulo."""
        from backend.agents.medicina import (
            AgenteFarmacologia,
            AgenteHistologia,
            AgenteAnatomia,
            AgenteFisiologia,
            AgentePatologia,
            AgenteBioquimica,
            AgenteMicrobiologia,
            AgenteCasosClinico
        )
        
        agentes = [
            AgenteFarmacologia,
            AgenteHistologia,
            AgenteAnatomia,
            AgenteFisiologia,
            AgentePatologia,
            AgenteBioquimica,
            AgenteMicrobiologia,
            AgenteCasosClinico
        ]
        
        for AgenteClass in agentes:
            agente = AgenteClass()
            assert agente is not None
    
    def test_metodo_gerar_questao_padrao(self):
        """Testa se todos os agentes têm o método gerar_questao."""
        from backend.agents.medicina import (
            AgenteFarmacologia,
            AgenteHistologia,
            AgenteAnatomia,
            AgenteFisiologia,
            AgentePatologia,
            AgenteBioquimica,
            AgenteMicrobiologia,
            AgenteCasosClinico
        )
        
        agentes = [
            AgenteFarmacologia(),
            AgenteHistologia(),
            AgenteAnatomia(),
            AgenteFisiologia(),
            AgentePatologia(),
            AgenteBioquimica(),
            AgenteMicrobiologia(),
            AgenteCasosClinico()
        ]
        
        for agente in agentes:
            assert hasattr(agente, 'gerar_questao')
            questao = agente.gerar_questao()
            assert "enunciado" in questao
            assert "resposta" in questao
    
    def test_dificuldades_diferentes(self):
        """Testa se todos os agentes geram questões em todas as dificuldades."""
        from backend.agents.medicina import AgenteFarmacologia
        
        agente = AgenteFarmacologia()
        
        for dificuldade in ["facil", "medio", "dificil"]:
            questao = agente.gerar_questao(dificuldade=dificuldade)
            assert questao is not None
            assert len(questao["enunciado"]) > 10

