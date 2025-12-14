"""
Serviço de Revisão de Questões - Gerencia o fluxo de revisão pelo professor.

Este serviço coordena:
- Submissão de questões para revisão
- Adição de comentários e sugestões
- Aprovação/rejeição de questões
- Gestão de fontes bibliográficas
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
import uuid

from backend.repositories.questao_repository import QuestaoRepository
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FonteBibliografica:
    """Representa uma fonte bibliográfica."""
    tipo: str  # livro, artigo, site, outros
    autor: str
    titulo: str
    ano: Optional[int] = None
    edicao: Optional[str] = None
    paginas: Optional[str] = None
    revista: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class RevisaoQuestao:
    """Dados de uma revisão de questão."""
    questao_id: str
    status: str = "pendente"
    comentarios: Optional[str] = None
    sugestoes_melhoria: Optional[str] = None
    correcoes_texto: Optional[str] = None
    fontes_bibliograficas: List[FonteBibliografica] = field(default_factory=list)
    nota_qualidade: Optional[int] = None
    precisao_cientifica: Optional[bool] = None
    clareza_enunciado: Optional[bool] = None
    adequacao_nivel: Optional[bool] = None
    versao: int = 1
    professor_id: Optional[str] = None


class RevisaoService:
    """
    Serviço para gerenciamento de revisões de questões.
    
    Fluxo:
    1. Questão é gerada com status 'rascunho'
    2. Professor visualiza e adiciona feedback
    3. Professor pode aprovar, rejeitar ou solicitar correções
    4. Questões aprovadas ficam disponíveis para uso em provas
    """
    
    STATUS_REVISAO = {
        'pendente': 'Aguardando revisão',
        'em_revisao': 'Em análise pelo professor',
        'aprovada': 'Aprovada para uso',
        'rejeitada': 'Rejeitada - necessita nova geração',
        'correcao_pendente': 'Correções solicitadas'
    }
    
    def __init__(self):
        self.questao_repository = QuestaoRepository()
        # Cache de revisões em memória (para versão piloto sem banco)
        self._revisoes_cache: Dict[str, List[Dict]] = {}
        self._questoes_cache: Dict[str, Dict] = {}
    
    def obter_questoes_pendentes(
        self,
        professor_id: Optional[str] = None,
        materia: Optional[str] = None,
        limite: int = 50
    ) -> List[Dict]:
        """
        Retorna questões pendentes de revisão.
        
        Args:
            professor_id: Filtrar por professor (opcional)
            materia: Filtrar por matéria (opcional)
            limite: Número máximo de resultados
        
        Returns:
            Lista de questões pendentes
        """
        questoes = []
        
        for questao_id, questao in self._questoes_cache.items():
            if questao.get('status') in ['rascunho', 'revisao', 'pendente']:
                if materia and questao.get('materia') != materia:
                    continue
                if professor_id and questao.get('professor_id') != professor_id:
                    continue
                    
                # Adicionar info de revisão
                revisoes = self._revisoes_cache.get(questao_id, [])
                ultima_revisao = revisoes[-1] if revisoes else None
                
                questao_info = {
                    **questao,
                    'id': questao_id,
                    'ultima_revisao': ultima_revisao,
                    'total_revisoes': len(revisoes)
                }
                questoes.append(questao_info)
        
        return questoes[:limite]
    
    def obter_questoes_aprovadas(
        self,
        professor_id: Optional[str] = None,
        materia: Optional[str] = None,
        limite: int = 100
    ) -> List[Dict]:
        """
        Retorna questões aprovadas pelo professor.
        
        Args:
            professor_id: Filtrar por professor (opcional)
            materia: Filtrar por matéria (opcional)
            limite: Número máximo de resultados
        
        Returns:
            Lista de questões aprovadas
        """
        questoes = []
        
        for questao_id, questao in self._questoes_cache.items():
            if questao.get('status') == 'aprovada':
                if materia and questao.get('materia') != materia:
                    continue
                if professor_id and questao.get('professor_id') != professor_id:
                    continue
                
                questao_info = {
                    **questao,
                    'id': questao_id
                }
                questoes.append(questao_info)
        
        # Ordenar por data de aprovação (mais recentes primeiro)
        questoes.sort(key=lambda x: x.get('aprovada_em', ''), reverse=True)
        
        return questoes[:limite]
    
    def adicionar_questao_para_revisao(self, questao: Dict) -> str:
        """
        Adiciona uma questão ao fluxo de revisão.
        
        Args:
            questao: Dados da questão gerada
        
        Returns:
            ID da questão
        """
        questao_id = questao.get('id') or str(uuid.uuid4())
        
        # Garantir campos obrigatórios
        questao_data = {
            **questao,
            'id': questao_id,
            'status': 'pendente',
            'created_at': datetime.now().isoformat(),
            'versao': 1
        }
        
        self._questoes_cache[questao_id] = questao_data
        self._revisoes_cache[questao_id] = []
        
        logger.info(f"Questão {questao_id} adicionada para revisão")
        return questao_id
    
    def obter_questao(self, questao_id: str) -> Optional[Dict]:
        """Obtém uma questão pelo ID."""
        return self._questoes_cache.get(questao_id)
    
    def obter_revisoes(self, questao_id: str) -> List[Dict]:
        """Obtém histórico de revisões de uma questão."""
        return self._revisoes_cache.get(questao_id, [])
    
    def salvar_revisao(self, revisao: RevisaoQuestao) -> Dict:
        """
        Salva uma revisão para uma questão.
        
        Args:
            revisao: Dados da revisão
        
        Returns:
            Dicionário com resultado da operação
        """
        questao_id = revisao.questao_id
        
        if questao_id not in self._questoes_cache:
            return {"erro": "Questão não encontrada", "sucesso": False}
        
        # Criar registro de revisão
        revisao_data = {
            'id': str(uuid.uuid4()),
            'questao_id': questao_id,
            'status': revisao.status,
            'comentarios': revisao.comentarios,
            'sugestoes_melhoria': revisao.sugestoes_melhoria,
            'correcoes_texto': revisao.correcoes_texto,
            'fontes_bibliograficas': [f.to_dict() for f in revisao.fontes_bibliograficas],
            'nota_qualidade': revisao.nota_qualidade,
            'precisao_cientifica': revisao.precisao_cientifica,
            'clareza_enunciado': revisao.clareza_enunciado,
            'adequacao_nivel': revisao.adequacao_nivel,
            'versao': revisao.versao,
            'professor_id': revisao.professor_id,
            'created_at': datetime.now().isoformat()
        }
        
        # Adicionar ao histórico
        if questao_id not in self._revisoes_cache:
            self._revisoes_cache[questao_id] = []
        self._revisoes_cache[questao_id].append(revisao_data)
        
        # Atualizar status da questão
        self._questoes_cache[questao_id]['status'] = revisao.status
        self._questoes_cache[questao_id]['ultima_revisao'] = revisao_data
        
        if revisao.status == 'aprovada':
            self._questoes_cache[questao_id]['aprovada_em'] = datetime.now().isoformat()
            self._questoes_cache[questao_id]['fontes_bibliograficas'] = revisao_data['fontes_bibliograficas']
        
        logger.info(f"Revisão salva para questão {questao_id}: status={revisao.status}")
        
        return {
            "sucesso": True,
            "revisao_id": revisao_data['id'],
            "status": revisao.status
        }
    
    def aprovar_questao(
        self,
        questao_id: str,
        comentarios: Optional[str] = None,
        fontes: Optional[List[Dict]] = None,
        professor_id: Optional[str] = None
    ) -> Dict:
        """
        Aprova uma questão para uso em provas.
        
        Args:
            questao_id: ID da questão
            comentarios: Comentários finais do professor
            fontes: Lista de fontes bibliográficas
            professor_id: ID do professor
        
        Returns:
            Resultado da operação
        """
        fontes_obj = []
        if fontes:
            for f in fontes:
                fontes_obj.append(FonteBibliografica(**f))
        
        revisao = RevisaoQuestao(
            questao_id=questao_id,
            status='aprovada',
            comentarios=comentarios,
            fontes_bibliograficas=fontes_obj,
            professor_id=professor_id,
            precisao_cientifica=True,
            clareza_enunciado=True,
            adequacao_nivel=True
        )
        
        return self.salvar_revisao(revisao)
    
    def rejeitar_questao(
        self,
        questao_id: str,
        motivo: str,
        sugestoes: Optional[str] = None,
        professor_id: Optional[str] = None
    ) -> Dict:
        """
        Rejeita uma questão (necessita nova geração).
        
        Args:
            questao_id: ID da questão
            motivo: Motivo da rejeição
            sugestoes: Sugestões para melhoria
            professor_id: ID do professor
        
        Returns:
            Resultado da operação
        """
        revisao = RevisaoQuestao(
            questao_id=questao_id,
            status='rejeitada',
            comentarios=motivo,
            sugestoes_melhoria=sugestoes,
            professor_id=professor_id
        )
        
        return self.salvar_revisao(revisao)
    
    def solicitar_correcoes(
        self,
        questao_id: str,
        correcoes: str,
        comentarios: Optional[str] = None,
        professor_id: Optional[str] = None
    ) -> Dict:
        """
        Solicita correções em uma questão.
        
        Args:
            questao_id: ID da questão
            correcoes: Correções a serem feitas
            comentarios: Comentários adicionais
            professor_id: ID do professor
        
        Returns:
            Resultado da operação
        """
        revisao = RevisaoQuestao(
            questao_id=questao_id,
            status='correcao_pendente',
            comentarios=comentarios,
            correcoes_texto=correcoes,
            professor_id=professor_id
        )
        
        return self.salvar_revisao(revisao)
    
    def aplicar_correcoes(
        self,
        questao_id: str,
        novo_enunciado: Optional[str] = None,
        novas_alternativas: Optional[List[Dict]] = None,
        nova_resposta: Optional[str] = None
    ) -> Dict:
        """
        Aplica correções a uma questão.
        
        Args:
            questao_id: ID da questão
            novo_enunciado: Novo texto do enunciado
            novas_alternativas: Novas alternativas
            nova_resposta: Nova resposta correta
        
        Returns:
            Resultado da operação
        """
        if questao_id not in self._questoes_cache:
            return {"erro": "Questão não encontrada", "sucesso": False}
        
        questao = self._questoes_cache[questao_id]
        
        if novo_enunciado:
            questao['enunciado'] = novo_enunciado
        
        if novas_alternativas:
            questao['alternativas'] = novas_alternativas
        
        if nova_resposta:
            questao['resposta'] = nova_resposta
        
        # Incrementar versão
        questao['versao'] = questao.get('versao', 1) + 1
        questao['status'] = 'pendente'  # Volta para revisão
        questao['updated_at'] = datetime.now().isoformat()
        
        logger.info(f"Correções aplicadas na questão {questao_id}, versão {questao['versao']}")
        
        return {
            "sucesso": True,
            "versao": questao['versao'],
            "status": questao['status']
        }
    
    def adicionar_fonte_bibliografica(
        self,
        questao_id: str,
        fonte: Dict
    ) -> Dict:
        """
        Adiciona uma fonte bibliográfica a uma questão.
        
        Args:
            questao_id: ID da questão
            fonte: Dados da fonte
        
        Returns:
            Resultado da operação
        """
        if questao_id not in self._questoes_cache:
            return {"erro": "Questão não encontrada", "sucesso": False}
        
        questao = self._questoes_cache[questao_id]
        
        if 'fontes_bibliograficas' not in questao:
            questao['fontes_bibliograficas'] = []
        
        fonte_obj = FonteBibliografica(**fonte)
        questao['fontes_bibliograficas'].append(fonte_obj.to_dict())
        
        return {
            "sucesso": True,
            "total_fontes": len(questao['fontes_bibliograficas'])
        }
    
    def obter_estatisticas(self, professor_id: Optional[str] = None) -> Dict:
        """
        Retorna estatísticas do fluxo de revisão.
        
        Args:
            professor_id: Filtrar por professor (opcional)
        
        Returns:
            Dicionário com estatísticas
        """
        stats = {
            'total': 0,
            'pendentes': 0,
            'aprovadas': 0,
            'rejeitadas': 0,
            'correcao_pendente': 0,
            'por_materia': {}
        }
        
        for questao in self._questoes_cache.values():
            if professor_id and questao.get('professor_id') != professor_id:
                continue
            
            stats['total'] += 1
            status = questao.get('status', 'pendente')
            
            if status in ['pendente', 'rascunho']:
                stats['pendentes'] += 1
            elif status == 'aprovada':
                stats['aprovadas'] += 1
            elif status == 'rejeitada':
                stats['rejeitadas'] += 1
            elif status == 'correcao_pendente':
                stats['correcao_pendente'] += 1
            
            # Por matéria
            materia = questao.get('materia', 'outros')
            if materia not in stats['por_materia']:
                stats['por_materia'][materia] = {'total': 0, 'aprovadas': 0}
            stats['por_materia'][materia]['total'] += 1
            if status == 'aprovada':
                stats['por_materia'][materia]['aprovadas'] += 1
        
        return stats


# Instância global do serviço
revisao_service = RevisaoService()

