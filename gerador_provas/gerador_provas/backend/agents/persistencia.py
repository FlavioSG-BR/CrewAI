import uuid
from crewai import Agent
from sqlalchemy import create_engine, text

class AgentePersistencia:
    def __init__(self):
        self.agent = Agent(
            role="Persistência em Banco de Dados",
            goal="Armazenar questões e resoluções no PostgreSQL",
            backstory="Especialista em ETL e gestão de dados educacionais.",
            allow_delegation=False
        )
        self.engine = create_engine("postgresql://user:password@db:5432/provas_db")

    def salvar_questao(self, materia: str, topico: str, enunciado: str, dificuldade: str) -> str:
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
    def validar_e_salvar(self, enunciado: str, resposta: str, materia: str):
        from utils.validator import validar_resposta
        if not validar_resposta(resposta, self._calcular_resposta_esperada(enunciado)):
            raise ValueError("Resposta inv�lida!")
        return self.salvar_questao(enunciado, materia)
