import uuid
import re
import os
from crewai import Agent
from sqlalchemy import create_engine, text


class AgentePersistencia:
    """Agente especializado em persistência de dados."""
    
    def __init__(self):
        self.agent = Agent(
            role="Persistência em Banco de Dados",
            goal="Armazenar questões e resoluções no PostgreSQL",
            backstory="Especialista em ETL e gestão de dados educacionais.",
            verbose=False,
            allow_delegation=False
        )
        db_url = os.getenv("DATABASE_URL", "postgresql://provas_user:provas_password_2024@db:5432/provas_db")
        self.engine = create_engine(db_url)

    def salvar_questao(self, materia: str, topico: str, enunciado: str, dificuldade: str) -> str:
        """Salva uma questão no banco de dados"""
        questao_id = str(uuid.uuid4())
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO questoes (id, materia, topico, enunciado, dificuldade)
                VALUES (:id, :materia, :topico, :enunciado, :dificuldade)
            """), {
                "id": questao_id,
                "materia": materia,
                "topico": topico,
                "enunciado": enunciado,
                "dificuldade": dificuldade
            })
            conn.commit()
        return questao_id

    def salvar_resolucao(self, questao_id: str, solucao: str, explicacao: str):
        """Salva a resolução de uma questão"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO resolucoes (questao_id, solucao, explicacao)
                VALUES (:questao_id, :solucao, :explicacao)
            """), {
                "questao_id": questao_id,
                "solucao": solucao,
                "explicacao": explicacao
            })
            conn.commit()

    def _calcular_resposta_esperada(self, enunciado: str) -> str:
        """
        Calcula a resposta esperada baseada no enunciado.
        Usa heurísticas simples para extrair valores numéricos.
        """
        # Extrai números do enunciado para cálculos básicos
        numeros = re.findall(r'\d+\.?\d*', enunciado)
        
        if len(numeros) >= 2:
            # Exemplo: soma dos dois primeiros números encontrados
            resultado = float(numeros[0]) + float(numeros[1])
            return str(resultado)
        elif len(numeros) == 1:
            return numeros[0]
        
        return "Resposta não calculável automaticamente"

    def validar_e_salvar(self, enunciado: str, resposta: str, materia: str, topico: str = "Geral", dificuldade: str = "Médio") -> str:
        """Valida a resposta e salva a questão se for válida"""
        from backend.utils.validator import validar_resposta
        
        resposta_esperada = self._calcular_resposta_esperada(enunciado)
        
        if not validar_resposta(resposta, resposta_esperada):
            raise ValueError("Resposta inválida!")
        
        return self.salvar_questao(materia, topico, enunciado, dificuldade)
