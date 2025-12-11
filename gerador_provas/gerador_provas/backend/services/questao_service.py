"""
Serviço de Questões - Coordena geração e persistência.

Este serviço integra:
- Agentes de geração (Física, Química, Matemática)
- Agente de revisão
- Agente de classificação
- Agente de imagens
- Repositório de questões
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.agents.fisica import AgenteFisica
from backend.agents.quimica import AgenteQuimica
from backend.agents.matematica import AgenteMatematica
from backend.agents.revisor import AgenteRevisor
from backend.agents.classificador import AgenteClassificador
from backend.agents.imagens import AgenteImagens
from backend.repositories.questao_repository import QuestaoRepository
from backend.utils.logger import log_questao_gerada, get_logger

logger = get_logger(__name__)


class QuestaoService:
    """
    Serviço para geração e gerenciamento de questões.
    
    Integra o fluxo completo:
    1. Geração da questão (agente específico)
    2. Revisão (agente revisor)
    3. Classificação (agente classificador)
    4. Geração de diagrama (agente imagens - opcional)
    5. Persistência (repositório)
    """
    
    # Mapeamento de matérias para códigos
    MATERIA_CODIGOS = {
        "fisica": "FIS",
        "quimica": "QUI",
        "matematica": "MAT",
        "biologia": "BIO",
        "geografia": "GEO",
        "historia": "HIS",
        "portugues": "POR"
    }
    
    def __init__(self, persistir: bool = True):
        """
        Args:
            persistir: Se True, salva as questões no banco de dados
        """
        self.persistir = persistir
        self.repository = QuestaoRepository() if persistir else None
        
        # Agentes (lazy loading)
        self._agentes = {}
        self._revisor = None
        self._classificador = None
        self._gerador_imagens = None
    
    def _get_agente(self, materia: str):
        """Obtém o agente para a matéria (lazy loading)."""
        if materia not in self._agentes:
            agentes_map = {
                "fisica": AgenteFisica,
                "quimica": AgenteQuimica,
                "matematica": AgenteMatematica
            }
            if materia in agentes_map:
                self._agentes[materia] = agentes_map[materia]()
        return self._agentes.get(materia)
    
    def _get_revisor(self):
        """Obtém o agente revisor (lazy loading)."""
        if self._revisor is None:
            self._revisor = AgenteRevisor()
        return self._revisor
    
    def _get_classificador(self):
        """Obtém o agente classificador (lazy loading)."""
        if self._classificador is None:
            self._classificador = AgenteClassificador()
        return self._classificador
    
    def _get_gerador_imagens(self):
        """Obtém o agente de imagens (lazy loading)."""
        if self._gerador_imagens is None:
            self._gerador_imagens = AgenteImagens()
        return self._gerador_imagens
    
    def gerar_questao(
        self,
        materia: str,
        topico: str = None,
        dificuldade: str = "medio",
        com_diagrama: bool = False,
        salvar: bool = None
    ) -> Dict[str, Any]:
        """
        Gera uma questão completa.
        
        Args:
            materia: Nome da matéria (fisica, quimica, matematica)
            topico: Tópico específico (opcional)
            dificuldade: Nível de dificuldade
            com_diagrama: Se True, gera diagrama
            salvar: Se True, salva no banco (default: self.persistir)
        
        Returns:
            Dicionário com a questão gerada e metadados
        """
        if salvar is None:
            salvar = self.persistir
        
        logger.info(f"Gerando questão: materia={materia}, topico={topico}")
        
        # 1. Obter agente e gerar questão
        agente = self._get_agente(materia)
        if not agente:
            raise ValueError(f"Matéria '{materia}' não suportada")
        
        questao = agente.gerar_questao(topico or "geral", com_diagrama)
        
        # 2. Classificar
        classificador = self._get_classificador()
        tags = classificador.classificar(topico or questao.get("tipo", "geral"))
        
        # 3. Revisar
        revisor = self._get_revisor()
        enunciado = questao.get("enunciado", "")
        resposta = questao.get("resposta", "")
        
        questao["revisao_aprovada"] = revisor.validar_questao(enunciado, resposta)
        
        if not questao["revisao_aprovada"]:
            logger.warning("Questão reprovada na revisão, tentando novamente...")
            # Tenta gerar novamente
            questao = agente.gerar_questao(topico or "geral", com_diagrama)
            questao["revisao_aprovada"] = True  # Segunda tentativa é aceita
        
        # 4. Adicionar metadados
        questao["materia"] = materia
        questao["topico"] = topico
        questao["dificuldade"] = dificuldade
        questao["tags"] = tags
        questao["gerado_em"] = datetime.now().isoformat()
        
        # 5. Salvar no banco de dados
        if salvar and self.repository:
            try:
                questao_id = self._salvar_questao(questao, materia, topico, dificuldade)
                questao["id"] = questao_id
                questao["salva"] = True
                logger.info(f"Questão salva com ID: {questao_id}")
            except Exception as e:
                logger.error(f"Erro ao salvar questão: {e}")
                questao["salva"] = False
                questao["erro_persistencia"] = str(e)
        else:
            questao["salva"] = False
        
        # 6. Log
        log_questao_gerada(materia)
        
        return questao
    
    def _salvar_questao(
        self,
        questao: Dict,
        materia: str,
        topico: str,
        dificuldade: str
    ) -> str:
        """Salva a questão no banco de dados."""
        # Obter IDs de matéria e tópico
        codigo_materia = self.MATERIA_CODIGOS.get(materia, materia.upper()[:3])
        materia_id = self.repository.obter_materia_id_por_codigo(codigo_materia)
        
        if not materia_id:
            logger.warning(f"Matéria {codigo_materia} não encontrada no banco")
            # Usar ID genérico ou criar
            materia_id = None
        
        topico_id = None
        if topico and materia_id:
            topico_id = self.repository.obter_topico_id_por_codigo(
                materia_id, 
                topico.upper().replace(" ", "_")
            )
        
        # Criar questão
        questao_id = self.repository.criar_questao(
            materia_id=materia_id,
            topico_id=topico_id,
            enunciado=questao.get("enunciado", ""),
            tipo=questao.get("tipo_questao", "dissertativa"),
            dificuldade=dificuldade,
            status="aprovada" if questao.get("revisao_aprovada") else "rascunho",
            fonte="Gerador Automático CrewAI",
            palavras_chave=questao.get("tags", {}).get("topico")
        )
        
        # Criar resolução
        self.repository.criar_resolucao(
            questao_id=questao_id,
            resposta_curta=questao.get("resposta", ""),
            resposta_completa=questao.get("explicacao"),
            formulas=questao.get("formulas"),
            metodo_resolucao=questao.get("metodo")
        )
        
        # Registrar diagrama se existir
        if questao.get("diagrama"):
            caminho = questao["diagrama"]
            nome_arquivo = os.path.basename(caminho)
            
            self.repository.criar_diagrama(
                questao_id=questao_id,
                nome_arquivo=nome_arquivo,
                caminho=caminho,
                tipo_diagrama=questao.get("tipo"),
                parametros=questao.get("dados")
            )
        
        return questao_id
    
    def gerar_multiplas(
        self,
        materia: str,
        quantidade: int,
        topico: str = None,
        dificuldade: str = "medio",
        com_diagrama: bool = False
    ) -> List[Dict]:
        """
        Gera múltiplas questões.
        
        Args:
            materia: Nome da matéria
            quantidade: Número de questões
            topico: Tópico (opcional)
            dificuldade: Nível de dificuldade
            com_diagrama: Se True, gera diagramas
        
        Returns:
            Lista de questões geradas
        """
        questoes = []
        
        for i in range(quantidade):
            try:
                questao = self.gerar_questao(
                    materia=materia,
                    topico=topico,
                    dificuldade=dificuldade,
                    com_diagrama=com_diagrama
                )
                questao["numero"] = i + 1
                questoes.append(questao)
            except Exception as e:
                logger.error(f"Erro ao gerar questão {i + 1}: {e}")
        
        return questoes
    
    def buscar_questoes(
        self,
        materia: str = None,
        topico: str = None,
        dificuldade: str = None,
        limite: int = 50
    ) -> List[Dict]:
        """
        Busca questões no banco de dados.
        """
        if not self.repository:
            return []
        
        materia_id = None
        if materia:
            codigo = self.MATERIA_CODIGOS.get(materia, materia.upper()[:3])
            materia_id = self.repository.obter_materia_id_por_codigo(codigo)
        
        return self.repository.buscar_questoes(
            materia_id=materia_id,
            dificuldade=dificuldade,
            limite=limite
        )
    
    def obter_estatisticas(self) -> Dict:
        """
        Retorna estatísticas das questões.
        """
        if not self.repository:
            return {"total": 0}
        
        return {
            "total": self.repository.contar_questoes(),
            "por_materia": {
                "fisica": self.repository.contar_questoes(
                    self.repository.obter_materia_id_por_codigo("FIS")
                ),
                "quimica": self.repository.contar_questoes(
                    self.repository.obter_materia_id_por_codigo("QUI")
                ),
                "matematica": self.repository.contar_questoes(
                    self.repository.obter_materia_id_por_codigo("MAT")
                )
            }
        }

