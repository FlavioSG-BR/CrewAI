"""
Repositório para operações com questões no banco de dados.
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.repositories.base import BaseRepository


class QuestaoRepository(BaseRepository):
    """
    Repositório para CRUD de questões.
    """
    
    def __init__(self):
        super().__init__(schema="provas")
    
    def criar_questao(
        self,
        materia_id: str,
        enunciado: str,
        tipo: str = "dissertativa",
        dificuldade: str = "medio",
        topico_id: str = None,
        codigo: str = None,
        status: str = "rascunho",
        criado_por: str = None,
        **kwargs
    ) -> str:
        """
        Cria uma nova questão no banco de dados.
        
        Returns:
            ID da questão criada
        """
        questao_id = str(uuid.uuid4())
        
        if codigo is None:
            # Gera código automático baseado na matéria
            codigo = f"Q-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        query = f"""
            INSERT INTO {self.schema}.questoes (
                id, materia_id, topico_id, tipo, dificuldade, 
                codigo, enunciado, status, criado_por,
                enunciado_complementar, pontuacao, tempo_estimado_min,
                fonte, palavras_chave
            ) VALUES (
                :id, :materia_id, :topico_id, :tipo, :dificuldade,
                :codigo, :enunciado, :status, :criado_por,
                :enunciado_complementar, :pontuacao, :tempo_estimado_min,
                :fonte, :palavras_chave
            )
        """
        
        params = {
            "id": questao_id,
            "materia_id": materia_id,
            "topico_id": topico_id,
            "tipo": tipo,
            "dificuldade": dificuldade,
            "codigo": codigo,
            "enunciado": enunciado,
            "status": status,
            "criado_por": criado_por,
            "enunciado_complementar": kwargs.get("enunciado_complementar"),
            "pontuacao": kwargs.get("pontuacao", 1.0),
            "tempo_estimado_min": kwargs.get("tempo_estimado_min"),
            "fonte": kwargs.get("fonte", "Gerador Automático"),
            "palavras_chave": kwargs.get("palavras_chave")
        }
        
        self.execute_insert(query, params)
        return questao_id
    
    def criar_resolucao(
        self,
        questao_id: str,
        resposta_curta: str,
        resposta_completa: str = None,
        passos: List[Dict] = None,
        formulas: List[str] = None,
        **kwargs
    ) -> str:
        """
        Cria uma resolução para uma questão.
        
        Returns:
            ID da resolução criada
        """
        import json
        
        resolucao_id = str(uuid.uuid4())
        
        query = f"""
            INSERT INTO {self.schema}.resolucoes (
                id, questao_id, resposta_curta, resposta_completa,
                passos, formulas, dicas, erros_comuns, metodo_resolucao
            ) VALUES (
                :id, :questao_id, :resposta_curta, :resposta_completa,
                :passos, :formulas, :dicas, :erros_comuns, :metodo_resolucao
            )
        """
        
        params = {
            "id": resolucao_id,
            "questao_id": questao_id,
            "resposta_curta": resposta_curta,
            "resposta_completa": resposta_completa,
            "passos": json.dumps(passos) if passos else None,
            "formulas": formulas,
            "dicas": kwargs.get("dicas"),
            "erros_comuns": kwargs.get("erros_comuns"),
            "metodo_resolucao": kwargs.get("metodo_resolucao")
        }
        
        self.execute_insert(query, params)
        return resolucao_id
    
    def criar_diagrama(
        self,
        questao_id: str,
        nome_arquivo: str,
        caminho: str,
        tipo_diagrama: str = None,
        **kwargs
    ) -> str:
        """
        Registra um diagrama no banco de dados.
        
        Returns:
            ID do diagrama criado
        """
        import json
        import os
        
        diagrama_id = str(uuid.uuid4())
        
        # Obter tamanho do arquivo se existir
        tamanho = 0
        if os.path.exists(caminho):
            tamanho = os.path.getsize(caminho)
        
        query = f"""
            INSERT INTO {self.schema}.diagramas (
                id, questao_id, nome_arquivo, caminho, tipo_arquivo,
                tamanho_bytes, tipo_diagrama, titulo, descricao,
                alt_text, parametros_geracao, posicao
            ) VALUES (
                :id, :questao_id, :nome_arquivo, :caminho, :tipo_arquivo,
                :tamanho_bytes, :tipo_diagrama, :titulo, :descricao,
                :alt_text, :parametros_geracao, :posicao
            )
        """
        
        params = {
            "id": diagrama_id,
            "questao_id": questao_id,
            "nome_arquivo": nome_arquivo,
            "caminho": caminho,
            "tipo_arquivo": kwargs.get("tipo_arquivo", "png"),
            "tamanho_bytes": tamanho,
            "tipo_diagrama": tipo_diagrama,
            "titulo": kwargs.get("titulo"),
            "descricao": kwargs.get("descricao"),
            "alt_text": kwargs.get("alt_text"),
            "parametros_geracao": json.dumps(kwargs.get("parametros")) if kwargs.get("parametros") else None,
            "posicao": kwargs.get("posicao", "apos_enunciado")
        }
        
        self.execute_insert(query, params)
        return diagrama_id
    
    def buscar_questao_por_id(self, questao_id: str) -> Optional[Dict]:
        """
        Busca uma questão pelo ID.
        """
        query = f"""
            SELECT q.*, m.nome as materia_nome, m.codigo as materia_codigo,
                   t.nome as topico_nome, t.codigo as topico_codigo
            FROM {self.schema}.questoes q
            LEFT JOIN {self.schema}.materias m ON q.materia_id = m.id
            LEFT JOIN {self.schema}.topicos t ON q.topico_id = t.id
            WHERE q.id = :id AND q.deleted_at IS NULL
        """
        
        resultados = self.execute_query(query, {"id": questao_id})
        return resultados[0] if resultados else None
    
    def buscar_questoes(
        self,
        materia_id: str = None,
        topico_id: str = None,
        dificuldade: str = None,
        status: str = None,
        limite: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """
        Busca questões com filtros.
        """
        conditions = ["q.deleted_at IS NULL"]
        params = {"limite": limite, "offset": offset}
        
        if materia_id:
            conditions.append("q.materia_id = :materia_id")
            params["materia_id"] = materia_id
        
        if topico_id:
            conditions.append("q.topico_id = :topico_id")
            params["topico_id"] = topico_id
        
        if dificuldade:
            conditions.append("q.dificuldade = :dificuldade")
            params["dificuldade"] = dificuldade
        
        if status:
            conditions.append("q.status = :status")
            params["status"] = status
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT q.*, m.nome as materia_nome, t.nome as topico_nome
            FROM {self.schema}.questoes q
            LEFT JOIN {self.schema}.materias m ON q.materia_id = m.id
            LEFT JOIN {self.schema}.topicos t ON q.topico_id = t.id
            WHERE {where_clause}
            ORDER BY q.created_at DESC
            LIMIT :limite OFFSET :offset
        """
        
        return self.execute_query(query, params)
    
    def obter_materia_id_por_codigo(self, codigo: str) -> Optional[str]:
        """
        Obtém o ID da matéria pelo código (ex: 'FIS', 'MAT', 'QUI').
        """
        query = f"""
            SELECT id FROM {self.schema}.materias 
            WHERE codigo = :codigo AND deleted_at IS NULL
        """
        
        resultados = self.execute_query(query, {"codigo": codigo.upper()})
        return resultados[0]["id"] if resultados else None
    
    def obter_topico_id_por_codigo(self, materia_id: str, codigo: str) -> Optional[str]:
        """
        Obtém o ID do tópico pelo código e matéria.
        """
        query = f"""
            SELECT id FROM {self.schema}.topicos 
            WHERE materia_id = :materia_id AND codigo = :codigo AND deleted_at IS NULL
        """
        
        resultados = self.execute_query(query, {
            "materia_id": materia_id,
            "codigo": codigo.upper()
        })
        return resultados[0]["id"] if resultados else None
    
    def incrementar_uso(self, questao_id: str) -> None:
        """
        Incrementa o contador de uso da questão.
        """
        query = f"""
            UPDATE {self.schema}.questoes 
            SET vezes_usada = COALESCE(vezes_usada, 0) + 1
            WHERE id = :id
        """
        self.execute_update(query, {"id": questao_id})
    
    def contar_questoes(self, materia_id: str = None) -> int:
        """
        Conta o total de questões.
        """
        conditions = ["deleted_at IS NULL"]
        params = {}
        
        if materia_id:
            conditions.append("materia_id = :materia_id")
            params["materia_id"] = materia_id
        
        query = f"""
            SELECT COUNT(*) as total 
            FROM {self.schema}.questoes 
            WHERE {" AND ".join(conditions)}
        """
        
        resultados = self.execute_query(query, params)
        return resultados[0]["total"] if resultados else 0

