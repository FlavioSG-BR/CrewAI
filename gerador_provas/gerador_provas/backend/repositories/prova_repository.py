"""
Repositório para operações com provas no banco de dados.
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.repositories.base import BaseRepository


class ProvaRepository(BaseRepository):
    """
    Repositório para CRUD de provas.
    """
    
    def __init__(self):
        super().__init__(schema="provas")
    
    def criar_prova(
        self,
        titulo: str,
        materia_id: str = None,
        descricao: str = None,
        tempo_limite_min: int = None,
        criado_por: str = None,
        **kwargs
    ) -> str:
        """
        Cria uma nova prova.
        
        Returns:
            ID da prova criada
        """
        prova_id = str(uuid.uuid4())
        codigo = f"PROVA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        query = f"""
            INSERT INTO {self.schema}.provas (
                id, codigo, titulo, descricao, materia_id,
                tempo_limite_min, criado_por, nivel_escolar, serie,
                instrucoes, embaralhar_questoes, embaralhar_alternativas
            ) VALUES (
                :id, :codigo, :titulo, :descricao, :materia_id,
                :tempo_limite_min, :criado_por, :nivel_escolar, :serie,
                :instrucoes, :embaralhar_questoes, :embaralhar_alternativas
            )
        """
        
        params = {
            "id": prova_id,
            "codigo": codigo,
            "titulo": titulo,
            "descricao": descricao,
            "materia_id": materia_id,
            "tempo_limite_min": tempo_limite_min,
            "criado_por": criado_por,
            "nivel_escolar": kwargs.get("nivel_escolar"),
            "serie": kwargs.get("serie"),
            "instrucoes": kwargs.get("instrucoes"),
            "embaralhar_questoes": kwargs.get("embaralhar_questoes", False),
            "embaralhar_alternativas": kwargs.get("embaralhar_alternativas", False)
        }
        
        self.execute_insert(query, params)
        return prova_id
    
    def adicionar_questao_prova(
        self,
        prova_id: str,
        questao_id: str,
        numero: int,
        pontuacao: float = 1.0
    ) -> str:
        """
        Adiciona uma questão a uma prova.
        
        Returns:
            ID do relacionamento criado
        """
        relacao_id = str(uuid.uuid4())
        
        query = f"""
            INSERT INTO {self.schema}.prova_questoes (
                id, prova_id, questao_id, numero, pontuacao
            ) VALUES (
                :id, :prova_id, :questao_id, :numero, :pontuacao
            )
        """
        
        params = {
            "id": relacao_id,
            "prova_id": prova_id,
            "questao_id": questao_id,
            "numero": numero,
            "pontuacao": pontuacao
        }
        
        self.execute_insert(query, params)
        return relacao_id
    
    def buscar_prova_por_id(self, prova_id: str) -> Optional[Dict]:
        """
        Busca uma prova pelo ID com suas questões.
        """
        query = f"""
            SELECT p.*, m.nome as materia_nome
            FROM {self.schema}.provas p
            LEFT JOIN {self.schema}.materias m ON p.materia_id = m.id
            WHERE p.id = :id AND p.deleted_at IS NULL
        """
        
        resultados = self.execute_query(query, {"id": prova_id})
        if not resultados:
            return None
        
        prova = resultados[0]
        
        # Buscar questões da prova
        query_questoes = f"""
            SELECT pq.numero, pq.pontuacao, q.*
            FROM {self.schema}.prova_questoes pq
            JOIN {self.schema}.questoes q ON pq.questao_id = q.id
            WHERE pq.prova_id = :prova_id
            ORDER BY pq.numero
        """
        
        prova["questoes"] = self.execute_query(query_questoes, {"prova_id": prova_id})
        
        return prova
    
    def listar_provas(
        self,
        status: str = None,
        materia_id: str = None,
        limite: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """
        Lista provas com filtros.
        """
        conditions = ["p.deleted_at IS NULL"]
        params = {"limite": limite, "offset": offset}
        
        if status:
            conditions.append("p.status = :status")
            params["status"] = status
        
        if materia_id:
            conditions.append("p.materia_id = :materia_id")
            params["materia_id"] = materia_id
        
        query = f"""
            SELECT p.*, m.nome as materia_nome,
                   (SELECT COUNT(*) FROM {self.schema}.prova_questoes WHERE prova_id = p.id) as total_questoes
            FROM {self.schema}.provas p
            LEFT JOIN {self.schema}.materias m ON p.materia_id = m.id
            WHERE {" AND ".join(conditions)}
            ORDER BY p.created_at DESC
            LIMIT :limite OFFSET :offset
        """
        
        return self.execute_query(query, params)
    
    def atualizar_status_prova(self, prova_id: str, status: str) -> bool:
        """
        Atualiza o status de uma prova.
        """
        query = f"""
            UPDATE {self.schema}.provas 
            SET status = :status, updated_at = CURRENT_TIMESTAMP
            WHERE id = :id
        """
        
        rows = self.execute_update(query, {"id": prova_id, "status": status})
        return rows > 0
    
    def calcular_pontuacao_total(self, prova_id: str) -> float:
        """
        Calcula a pontuação total de uma prova.
        """
        query = f"""
            SELECT COALESCE(SUM(pontuacao), 0) as total
            FROM {self.schema}.prova_questoes
            WHERE prova_id = :prova_id
        """
        
        resultados = self.execute_query(query, {"prova_id": prova_id})
        return float(resultados[0]["total"]) if resultados else 0.0

