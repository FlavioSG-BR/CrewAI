"""
Serviço de Provas - Coordena criação e gerenciamento de provas.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.repositories.prova_repository import ProvaRepository
from backend.repositories.questao_repository import QuestaoRepository
from backend.services.questao_service import QuestaoService
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ProvaService:
    """
    Serviço para criação e gerenciamento de provas.
    """
    
    def __init__(self):
        self.prova_repository = ProvaRepository()
        self.questao_repository = QuestaoRepository()
        self.questao_service = QuestaoService(persistir=True)
    
    def criar_prova(
        self,
        titulo: str,
        materia: str = None,
        descricao: str = None,
        num_questoes: int = 10,
        dificuldade: str = "medio",
        topicos: List[str] = None,
        com_diagramas: bool = False,
        gerar_questoes: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Cria uma prova completa com questões.
        
        Args:
            titulo: Título da prova
            materia: Matéria principal
            descricao: Descrição da prova
            num_questoes: Número de questões a gerar
            dificuldade: Nível de dificuldade
            topicos: Lista de tópicos a cobrir
            com_diagramas: Se True, gera diagramas
            gerar_questoes: Se True, gera questões automaticamente
        
        Returns:
            Dicionário com a prova criada
        """
        logger.info(f"Criando prova: {titulo}")
        
        # Obter materia_id se especificada
        materia_id = None
        if materia:
            codigo = QuestaoService.MATERIA_CODIGOS.get(materia, materia.upper()[:3])
            materia_id = self.questao_repository.obter_materia_id_por_codigo(codigo)
        
        # Criar prova no banco
        prova_id = self.prova_repository.criar_prova(
            titulo=titulo,
            materia_id=materia_id,
            descricao=descricao,
            tempo_limite_min=kwargs.get("tempo_limite_min"),
            **kwargs
        )
        
        questoes_geradas = []
        
        if gerar_questoes:
            # Gerar questões
            topicos_usar = topicos or [None]
            questoes_por_topico = num_questoes // len(topicos_usar)
            
            for i, topico in enumerate(topicos_usar):
                qtd = questoes_por_topico
                if i == len(topicos_usar) - 1:
                    # Último tópico recebe questões restantes
                    qtd = num_questoes - len(questoes_geradas)
                
                novas_questoes = self.questao_service.gerar_multiplas(
                    materia=materia or "matematica",
                    quantidade=qtd,
                    topico=topico,
                    dificuldade=dificuldade,
                    com_diagrama=com_diagramas
                )
                
                questoes_geradas.extend(novas_questoes)
            
            # Adicionar questões à prova
            for numero, questao in enumerate(questoes_geradas, 1):
                if questao.get("id"):
                    self.prova_repository.adicionar_questao_prova(
                        prova_id=prova_id,
                        questao_id=questao["id"],
                        numero=numero,
                        pontuacao=questao.get("pontuacao", 1.0)
                    )
        
        # Calcular pontuação total
        pontuacao_total = self.prova_repository.calcular_pontuacao_total(prova_id)
        
        return {
            "id": prova_id,
            "titulo": titulo,
            "materia": materia,
            "descricao": descricao,
            "num_questoes": len(questoes_geradas),
            "pontuacao_total": pontuacao_total,
            "questoes": questoes_geradas,
            "criada_em": datetime.now().isoformat()
        }
    
    def buscar_prova(self, prova_id: str) -> Optional[Dict]:
        """
        Busca uma prova pelo ID.
        """
        return self.prova_repository.buscar_prova_por_id(prova_id)
    
    def listar_provas(
        self,
        status: str = None,
        materia: str = None,
        limite: int = 50
    ) -> List[Dict]:
        """
        Lista provas com filtros.
        """
        materia_id = None
        if materia:
            codigo = QuestaoService.MATERIA_CODIGOS.get(materia, materia.upper()[:3])
            materia_id = self.questao_repository.obter_materia_id_por_codigo(codigo)
        
        return self.prova_repository.listar_provas(
            status=status,
            materia_id=materia_id,
            limite=limite
        )
    
    def publicar_prova(self, prova_id: str) -> bool:
        """
        Publica uma prova (muda status para 'publicada').
        """
        return self.prova_repository.atualizar_status_prova(prova_id, "publicada")
    
    def encerrar_prova(self, prova_id: str) -> bool:
        """
        Encerra uma prova.
        """
        return self.prova_repository.atualizar_status_prova(prova_id, "encerrada")

