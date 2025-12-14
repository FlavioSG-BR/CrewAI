"""
Testes para as Novas Rotas do Fluxo de Negócio.

Executa: pytest tests/test_rotas_novo_fluxo.py -v
"""

import pytest
import sys
import os
import json

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestRotasBancoQuestoes:
    """Testes para rotas do banco de questões."""
    
    @pytest.fixture
    def client(self):
        """Fixture que cria cliente de teste."""
        from app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def limpar_cache(self):
        """Fixture que limpa o cache antes de cada teste."""
        from app import revisao_service
        revisao_service._questoes_cache = {}
        revisao_service._revisoes_cache = {}
        yield
        revisao_service._questoes_cache = {}
        revisao_service._revisoes_cache = {}
    
    def test_banco_questoes_get(self, client, limpar_cache):
        """Testa GET /banco-questoes."""
        response = client.get('/banco-questoes')
        
        assert response.status_code == 200
        assert b'Banco de Quest' in response.data
    
    def test_banco_questoes_tab_pendentes(self, client, limpar_cache):
        """Testa /banco-questoes com tab=pendentes."""
        response = client.get('/banco-questoes?tab=pendentes')
        
        assert response.status_code == 200
    
    def test_banco_questoes_tab_aprovadas(self, client, limpar_cache):
        """Testa /banco-questoes com tab=aprovadas."""
        response = client.get('/banco-questoes?tab=aprovadas')
        
        assert response.status_code == 200
    
    def test_banco_questoes_filtro_materia(self, client, limpar_cache):
        """Testa /banco-questoes com filtro de matéria."""
        response = client.get('/banco-questoes?materia=fisica')
        
        assert response.status_code == 200


class TestRotasRevisao:
    """Testes para rotas de revisão."""
    
    @pytest.fixture
    def client(self):
        from app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def questao_id(self):
        """Fixture que cria uma questão para teste."""
        from app import revisao_service
        revisao_service._questoes_cache = {}
        revisao_service._revisoes_cache = {}
        
        questao = {
            "enunciado": "Questão de teste",
            "resposta": "Resposta",
            "materia": "fisica",
            "dificuldade": "medio"
        }
        
        q_id = revisao_service.adicionar_questao_para_revisao(questao)
        yield q_id
        
        revisao_service._questoes_cache = {}
        revisao_service._revisoes_cache = {}
    
    def test_revisar_questao_get(self, client, questao_id):
        """Testa GET /revisar/<id>."""
        response = client.get(f'/revisar/{questao_id}')
        
        assert response.status_code == 200
        assert b'Revisar Quest' in response.data
    
    def test_revisar_questao_inexistente(self, client):
        """Testa revisão de questão inexistente."""
        from app import revisao_service
        revisao_service._questoes_cache = {}
        
        response = client.get('/revisar/id-inexistente', follow_redirects=True)
        
        # Deve redirecionar para banco de questões
        assert response.status_code == 200
    
    def test_salvar_revisao_aprovar(self, client, questao_id):
        """Testa aprovação via POST."""
        response = client.post(
            f'/revisar/{questao_id}/salvar',
            data={
                'acao': 'aprovar',
                'comentarios': 'Questão aprovada',
                'nota_qualidade': '5'
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
    
    def test_salvar_revisao_rejeitar(self, client, questao_id):
        """Testa rejeição via POST."""
        response = client.post(
            f'/revisar/{questao_id}/salvar',
            data={
                'acao': 'rejeitar',
                'comentarios': 'Questão com problemas',
                'sugestoes': 'Refazer o enunciado'
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
    
    def test_salvar_revisao_corrigir(self, client, questao_id):
        """Testa solicitação de correção via POST."""
        response = client.post(
            f'/revisar/{questao_id}/salvar',
            data={
                'acao': 'corrigir',
                'comentarios': 'Ajustar texto',
                'sugestoes': 'Correções sugeridas'
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200


class TestRotasMontarProva:
    """Testes para rotas de montagem de prova."""
    
    @pytest.fixture
    def client(self):
        from app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def questoes_aprovadas(self):
        """Fixture com questões aprovadas."""
        from app import revisao_service
        revisao_service._questoes_cache = {}
        revisao_service._revisoes_cache = {}
        
        questoes = [
            {
                "enunciado": f"Questão {i}",
                "resposta": f"Resposta {i}",
                "materia": "fisica",
                "dificuldade": "medio",
                "alternativas": [
                    {"letra": "A", "texto": "A", "correta": True},
                    {"letra": "B", "texto": "B", "correta": False},
                    {"letra": "C", "texto": "C", "correta": False},
                    {"letra": "D", "texto": "D", "correta": False},
                    {"letra": "E", "texto": "E", "correta": False},
                ]
            }
            for i in range(1, 4)
        ]
        
        ids = []
        for q in questoes:
            q_id = revisao_service.adicionar_questao_para_revisao(q)
            revisao_service.aprovar_questao(q_id)
            ids.append(q_id)
        
        yield ids
        
        revisao_service._questoes_cache = {}
        revisao_service._revisoes_cache = {}
    
    def test_montar_prova_get(self, client):
        """Testa GET /montar-prova."""
        response = client.get('/montar-prova')
        
        assert response.status_code == 200
        assert b'Montar Prova' in response.data
    
    def test_montar_prova_com_questoes(self, client, questoes_aprovadas):
        """Testa /montar-prova com questões selecionadas."""
        ids_str = ','.join(questoes_aprovadas)
        response = client.get(f'/montar-prova?questoes={ids_str}')
        
        assert response.status_code == 200


class TestAPIsNovoFluxo:
    """Testes para as novas APIs."""
    
    @pytest.fixture
    def client(self):
        from app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def limpar_cache(self):
        from app import revisao_service
        revisao_service._questoes_cache = {}
        revisao_service._revisoes_cache = {}
        yield
        revisao_service._questoes_cache = {}
        revisao_service._revisoes_cache = {}
    
    @pytest.fixture
    def questao_teste(self, limpar_cache):
        """Fixture com questão de teste."""
        from app import revisao_service
        
        questao = {
            "enunciado": "Questão API",
            "resposta": "Resposta",
            "materia": "fisica",
            "dificuldade": "facil"
        }
        
        return revisao_service.adicionar_questao_para_revisao(questao)
    
    def test_api_questoes_pendentes(self, client, limpar_cache):
        """Testa GET /api/questoes/pendentes."""
        response = client.get('/api/questoes/pendentes')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'questoes' in data
        assert 'total' in data
    
    def test_api_questoes_aprovadas(self, client, limpar_cache):
        """Testa GET /api/questoes/aprovadas."""
        response = client.get('/api/questoes/aprovadas')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'questoes' in data
        assert 'total' in data
    
    def test_api_obter_questao(self, client, questao_teste):
        """Testa GET /api/questao/<id>."""
        response = client.get(f'/api/questao/{questao_teste}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'enunciado' in data
    
    def test_api_obter_questao_inexistente(self, client, limpar_cache):
        """Testa GET de questão inexistente."""
        response = client.get('/api/questao/id-invalido')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'erro' in data
    
    def test_api_excluir_questao(self, client, questao_teste):
        """Testa DELETE /api/questao/<id>."""
        response = client.delete(f'/api/questao/{questao_teste}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['sucesso'] is True
    
    def test_api_aprovar_questao(self, client, questao_teste):
        """Testa POST /api/questao/<id>/aprovar."""
        response = client.post(
            f'/api/questao/{questao_teste}/aprovar',
            data=json.dumps({'comentarios': 'Aprovada via API'}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['sucesso'] is True
    
    def test_api_rejeitar_questao(self, client, questao_teste):
        """Testa POST /api/questao/<id>/rejeitar."""
        response = client.post(
            f'/api/questao/{questao_teste}/rejeitar',
            data=json.dumps({'motivo': 'Rejeitada via API'}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['sucesso'] is True
    
    def test_api_rejeitar_sem_motivo(self, client, questao_teste):
        """Testa rejeição sem motivo."""
        response = client.post(
            f'/api/questao/{questao_teste}/rejeitar',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data
    
    def test_api_estatisticas_revisao(self, client, limpar_cache):
        """Testa GET /api/estatisticas/revisao."""
        response = client.get('/api/estatisticas/revisao')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total' in data
        assert 'pendentes' in data
        assert 'aprovadas' in data
    
    def test_api_lotes_provas(self, client):
        """Testa GET /api/lotes-provas."""
        response = client.get('/api/lotes-provas')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'lotes' in data
        assert 'total' in data


class TestAPIProvasIndividuais:
    """Testes para API de provas individuais."""
    
    @pytest.fixture
    def client(self):
        from app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def questoes_ids(self):
        """Fixture com questões aprovadas."""
        from app import revisao_service
        revisao_service._questoes_cache = {}
        revisao_service._revisoes_cache = {}
        
        ids = []
        for i in range(3):
            q = {
                "enunciado": f"Questão API {i}",
                "resposta": f"Resposta {i}",
                "materia": "fisica",
                "alternativas": [
                    {"letra": "A", "texto": "A", "correta": True},
                    {"letra": "B", "texto": "B", "correta": False},
                ]
            }
            q_id = revisao_service.adicionar_questao_para_revisao(q)
            revisao_service.aprovar_questao(q_id)
            ids.append(q_id)
        
        yield ids
        
        revisao_service._questoes_cache = {}
        revisao_service._revisoes_cache = {}
    
    def test_api_provas_individuais_sem_dados(self, client):
        """Testa POST sem dados."""
        response = client.post('/api/provas-individuais')
        
        assert response.status_code == 400
    
    def test_api_provas_individuais_sem_questoes(self, client):
        """Testa POST sem questões."""
        response = client.post(
            '/api/provas-individuais',
            data=json.dumps({'titulo': 'Prova', 'quantidade_alunos': 10}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data
    
    def test_api_provas_individuais_sucesso(self, client, questoes_ids):
        """Testa geração de provas via API (sem PDF)."""
        response = client.post(
            '/api/provas-individuais',
            data=json.dumps({
                'titulo': 'Prova API',
                'questoes_ids': questoes_ids,
                'quantidade_alunos': 5,
                'embaralhar_questoes': True,
                'embaralhar_alternativas': True,
                'gerar_pdf': False,
                'gerar_zip': False
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['status'] == 'concluido'
        assert data['provas_geradas'] == 5
        assert 'gabarito_consolidado' in data
        assert len(data['gabarito_consolidado']) == 5


class TestIntegracaoRotas:
    """Testes de integração das rotas."""
    
    @pytest.fixture
    def client(self):
        from app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def setup(self):
        """Setup e teardown."""
        from app import revisao_service
        revisao_service._questoes_cache = {}
        revisao_service._revisoes_cache = {}
        yield
        revisao_service._questoes_cache = {}
        revisao_service._revisoes_cache = {}
    
    def test_fluxo_completo_web(self, client, setup):
        """Testa fluxo completo via interface web."""
        from app import revisao_service
        
        # 1. Criar questões e adicionar ao banco
        for i in range(3):
            questao = {
                "enunciado": f"Questão fluxo {i}",
                "resposta": f"Resposta {i}",
                "materia": "fisica",
                "dificuldade": "medio",
                "alternativas": [
                    {"letra": "A", "texto": "A", "correta": True},
                    {"letra": "B", "texto": "B", "correta": False},
                    {"letra": "C", "texto": "C", "correta": False},
                    {"letra": "D", "texto": "D", "correta": False},
                    {"letra": "E", "texto": "E", "correta": False},
                ]
            }
            revisao_service.adicionar_questao_para_revisao(questao)
        
        # 2. Verificar banco de questões
        response = client.get('/banco-questoes')
        assert response.status_code == 200
        
        # 3. Aprovar questões via API
        questoes = revisao_service.obter_questoes_pendentes()
        questoes_ids = []
        
        for q in questoes:
            response = client.post(
                f'/api/questao/{q["id"]}/aprovar',
                data=json.dumps({'comentarios': 'Aprovada'}),
                content_type='application/json'
            )
            assert response.status_code == 200
            questoes_ids.append(q["id"])
        
        # 4. Verificar questões aprovadas
        response = client.get('/api/questoes/aprovadas')
        data = json.loads(response.data)
        assert data['total'] == 3
        
        # 5. Acessar página de montar prova
        ids_str = ','.join(questoes_ids)
        response = client.get(f'/montar-prova?questoes={ids_str}')
        assert response.status_code == 200
        
        # 6. Gerar provas via API
        response = client.post(
            '/api/provas-individuais',
            data=json.dumps({
                'titulo': 'Prova Integração',
                'questoes_ids': questoes_ids,
                'quantidade_alunos': 3,
                'gerar_pdf': False,
                'gerar_zip': False
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'concluido'
        assert data['provas_geradas'] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

