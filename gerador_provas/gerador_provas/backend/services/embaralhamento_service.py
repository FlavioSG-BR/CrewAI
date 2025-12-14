"""
Serviço de Embaralhamento - Gera provas únicas com questões e alternativas embaralhadas.

Este serviço é responsável por:
- Embaralhar a ordem das questões em uma prova
- Embaralhar a ordem das alternativas em cada questão
- Manter o mapeamento para geração de gabaritos individuais
- Garantir que cada prova seja única

Tipos de questão suportados:
- multipla_escolha: 2-5 alternativas (A-E), apenas uma correta
- verdadeiro_falso: 2 alternativas (V/F), apenas uma correta
- dissertativa: Sem alternativas, resposta aberta
- numerica: Resposta é um número (com tolerância opcional)
- associacao: Colunas para associar (embaralha colunas)
- multipla_resposta: Múltipla escolha com mais de uma correta
"""

import random
import hashlib
import json
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from copy import deepcopy
from enum import Enum

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class TipoQuestao(Enum):
    """Tipos de questão suportados."""
    MULTIPLA_ESCOLHA = "multipla_escolha"
    VERDADEIRO_FALSO = "verdadeiro_falso"
    DISSERTATIVA = "dissertativa"
    NUMERICA = "numerica"
    ASSOCIACAO = "associacao"
    MULTIPLA_RESPOSTA = "multipla_resposta"  # Múltiplas corretas


@dataclass
class MapeamentoQuestao:
    """Mapeamento de embaralhamento de uma questão."""
    questao_id: str
    posicao_original: int
    nova_posicao: int


@dataclass
class MapeamentoAlternativas:
    """Mapeamento de embaralhamento das alternativas de uma questão."""
    questao_id: str
    numero_questao: int
    mapeamento: Dict[str, str]  # {"A": "C", "B": "E", ...} original -> nova
    correta_original: Union[str, List[str]]  # Uma ou múltiplas respostas
    correta_nova: Union[str, List[str]]
    tipo_questao: str = "multipla_escolha"


@dataclass
class ProvaEmbaralhada:
    """Representa uma prova com questões e alternativas embaralhadas."""
    numero_aluno: int
    codigo_prova: str
    questoes: List[Dict]
    ordem_questoes: List[MapeamentoQuestao]
    ordem_alternativas: Dict[str, MapeamentoAlternativas]
    gabarito: Dict[str, Union[str, List[str]]]  # {"1": "C", "2": ["A", "C"], "3": "V", ...}
    hash_verificacao: str


class EmbaralhamentoService:
    """
    Serviço para embaralhamento de provas.
    
    Garante que cada aluno receba uma versão única da prova com:
    - Ordem diferente das questões
    - Ordem diferente das alternativas em cada questão (quando aplicável)
    - Gabarito específico para sua versão
    
    Suporta diferentes tipos de questão:
    - Múltipla escolha (2-5 alternativas)
    - Verdadeiro/Falso
    - Dissertativa (sem embaralhamento de alternativas)
    - Numérica
    - Associação de colunas
    - Múltipla resposta (mais de uma correta)
    """
    
    # Letras possíveis para alternativas (máximo 10)
    LETRAS_ALTERNATIVAS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    
    # Opções para V/F
    OPCOES_VF = ['V', 'F']
    OPCOES_VF_EXTENSO = ['Verdadeiro', 'Falso']
    
    def __init__(self, seed: Optional[int] = None):
        """
        Args:
            seed: Seed para reprodutibilidade (opcional)
        """
        self.seed = seed
        if seed:
            random.seed(seed)
    
    def identificar_tipo_questao(self, questao: Dict) -> TipoQuestao:
        """
        Identifica o tipo de questão baseado em sua estrutura.
        
        Args:
            questao: Dicionário com dados da questão
        
        Returns:
            TipoQuestao enum
        """
        # Se tem tipo explícito, usar
        tipo_explicito = questao.get('tipo_questao', questao.get('tipo', ''))
        
        if tipo_explicito:
            tipo_lower = tipo_explicito.lower().replace(' ', '_')
            for tipo in TipoQuestao:
                if tipo.value == tipo_lower:
                    return tipo
        
        # Inferir pelo conteúdo
        alternativas = questao.get('alternativas', [])
        
        # Sem alternativas = dissertativa ou numérica
        if not alternativas or len(alternativas) == 0:
            resposta = str(questao.get('resposta', ''))
            # Se resposta parece número, é numérica
            try:
                float(resposta.replace(',', '.').strip())
                return TipoQuestao.NUMERICA
            except:
                return TipoQuestao.DISSERTATIVA
        
        # Verificar V/F
        if len(alternativas) == 2:
            textos = [str(a.get('texto', '')).strip().upper() for a in alternativas]
            if set(textos) <= {'V', 'F', 'VERDADEIRO', 'FALSO', 'TRUE', 'FALSE', 'SIM', 'NÃO', 'NAO'}:
                return TipoQuestao.VERDADEIRO_FALSO
        
        # Verificar múltipla resposta
        corretas = sum(1 for a in alternativas if a.get('correta', False))
        if corretas > 1:
            return TipoQuestao.MULTIPLA_RESPOSTA
        
        # Verificar associação (tem colunas)
        if questao.get('coluna_a') or questao.get('coluna_b') or questao.get('associacoes'):
            return TipoQuestao.ASSOCIACAO
        
        # Default: múltipla escolha
        return TipoQuestao.MULTIPLA_ESCOLHA
    
    def pode_embaralhar_alternativas(self, tipo: TipoQuestao) -> bool:
        """
        Verifica se o tipo de questão permite embaralhamento de alternativas.
        
        Args:
            tipo: Tipo da questão
        
        Returns:
            True se pode embaralhar alternativas
        """
        tipos_embaralhaveis = {
            TipoQuestao.MULTIPLA_ESCOLHA,
            TipoQuestao.MULTIPLA_RESPOSTA,
            TipoQuestao.ASSOCIACAO,  # Embaralha as colunas
        }
        return tipo in tipos_embaralhaveis
    
    def embaralhar_lista(self, lista: List, seed_adicional: int = 0) -> Tuple[List, List[int]]:
        """
        Embaralha uma lista e retorna o mapeamento de índices.
        
        Args:
            lista: Lista a ser embaralhada
            seed_adicional: Seed adicional para variar o embaralhamento
        
        Returns:
            Tupla (lista_embaralhada, mapeamento_indices)
        """
        if self.seed:
            random.seed(self.seed + seed_adicional)
        
        indices = list(range(len(lista)))
        random.shuffle(indices)
        
        lista_embaralhada = [lista[i] for i in indices]
        
        return lista_embaralhada, indices
    
    def embaralhar_alternativas(
        self,
        alternativas: List[Dict],
        questao_id: str,
        numero_questao: int,
        seed_adicional: int = 0,
        tipo_questao: TipoQuestao = None
    ) -> Tuple[List[Dict], MapeamentoAlternativas]:
        """
        Embaralha as alternativas de uma questão.
        
        Suporta diferentes tipos:
        - multipla_escolha: Embaralha normalmente, atualiza letras
        - multipla_resposta: Igual, mas rastreia múltiplas corretas
        - verdadeiro_falso: NÃO embaralha (V sempre primeiro, F segundo)
        - associacao: Embaralha os itens das colunas
        
        Args:
            alternativas: Lista de alternativas
            questao_id: ID da questão
            numero_questao: Número da questão na prova
            seed_adicional: Seed para variar embaralhamento
            tipo_questao: Tipo da questão (para tratamento especial)
        
        Returns:
            Tupla (alternativas_embaralhadas, mapeamento)
        """
        if not alternativas or len(alternativas) == 0:
            return alternativas, None
        
        # Verdadeiro/Falso: não embaralhar alternativas
        if tipo_questao == TipoQuestao.VERDADEIRO_FALSO:
            return self._processar_verdadeiro_falso(alternativas, questao_id, numero_questao)
        
        # Encontrar alternativas corretas (pode ser mais de uma)
        corretas_originais = []
        for alt in alternativas:
            if alt.get('correta', False):
                corretas_originais.append(alt.get('letra', 'A'))
        
        if not corretas_originais:
            corretas_originais = ['A']  # Default
        
        # Determinar letras baseado no número de alternativas
        num_alternativas = len(alternativas)
        letras_disponiveis = self.LETRAS_ALTERNATIVAS[:num_alternativas]
        
        # Embaralhar
        alternativas_copy = deepcopy(alternativas)
        if self.seed:
            random.seed(self.seed + seed_adicional + hash(questao_id) % 1000)
        random.shuffle(alternativas_copy)
        
        # Criar mapeamento e atualizar letras
        mapeamento = {}
        corretas_novas = []
        
        for i, alt in enumerate(alternativas_copy):
            letra_original = alt.get('letra', letras_disponiveis[i] if i < len(letras_disponiveis) else f'X{i}')
            letra_nova = letras_disponiveis[i] if i < len(letras_disponiveis) else f'X{i}'
            
            mapeamento[letra_original] = letra_nova
            alt['letra'] = letra_nova
            
            if alt.get('correta', False):
                corretas_novas.append(letra_nova)
        
        # Para múltipla resposta, manter lista; para única, pegar primeira
        if tipo_questao == TipoQuestao.MULTIPLA_RESPOSTA:
            correta_original = corretas_originais
            correta_nova = corretas_novas
        else:
            correta_original = corretas_originais[0] if corretas_originais else 'A'
            correta_nova = corretas_novas[0] if corretas_novas else mapeamento.get(correta_original, 'A')
        
        mapeamento_obj = MapeamentoAlternativas(
            questao_id=questao_id,
            numero_questao=numero_questao,
            mapeamento=mapeamento,
            correta_original=correta_original,
            correta_nova=correta_nova,
            tipo_questao=tipo_questao.value if tipo_questao else "multipla_escolha"
        )
        
        return alternativas_copy, mapeamento_obj
    
    def _processar_verdadeiro_falso(
        self,
        alternativas: List[Dict],
        questao_id: str,
        numero_questao: int
    ) -> Tuple[List[Dict], MapeamentoAlternativas]:
        """
        Processa questões de Verdadeiro/Falso (não embaralha, apenas padroniza).
        
        Args:
            alternativas: Lista de alternativas V/F
            questao_id: ID da questão
            numero_questao: Número da questão
        
        Returns:
            Tupla (alternativas_padronizadas, mapeamento)
        """
        alternativas_copy = deepcopy(alternativas)
        
        # Encontrar qual é a correta
        correta = 'V'  # Default
        for alt in alternativas_copy:
            if alt.get('correta', False):
                texto = str(alt.get('texto', '')).strip().upper()
                if texto in ['V', 'VERDADEIRO', 'TRUE', 'SIM']:
                    correta = 'V'
                else:
                    correta = 'F'
                break
        
        # Padronizar formato
        padronizadas = [
            {"letra": "V", "texto": "Verdadeiro", "correta": correta == 'V'},
            {"letra": "F", "texto": "Falso", "correta": correta == 'F'}
        ]
        
        mapeamento_obj = MapeamentoAlternativas(
            questao_id=questao_id,
            numero_questao=numero_questao,
            mapeamento={"V": "V", "F": "F"},
            correta_original=correta,
            correta_nova=correta,
            tipo_questao="verdadeiro_falso"
        )
        
        return padronizadas, mapeamento_obj
    
    def embaralhar_associacao(
        self,
        questao: Dict,
        seed_adicional: int = 0
    ) -> Dict:
        """
        Embaralha questões de associação (colunas para relacionar).
        
        Args:
            questao: Questão com coluna_a, coluna_b e gabarito de associação
            seed_adicional: Seed adicional
        
        Returns:
            Questão com colunas embaralhadas e gabarito atualizado
        """
        questao_copy = deepcopy(questao)
        
        coluna_a = questao_copy.get('coluna_a', [])
        coluna_b = questao_copy.get('coluna_b', [])
        gabarito_original = questao_copy.get('gabarito_associacao', {})
        
        if not coluna_b:
            return questao_copy
        
        # Embaralhar apenas coluna B
        if self.seed:
            random.seed(self.seed + seed_adicional)
        
        indices_b = list(range(len(coluna_b)))
        random.shuffle(indices_b)
        
        # Nova coluna B
        nova_coluna_b = [coluna_b[i] for i in indices_b]
        
        # Atualizar números/letras
        mapeamento_b = {}  # original -> novo
        for novo_idx, original_idx in enumerate(indices_b):
            mapeamento_b[original_idx + 1] = novo_idx + 1
        
        # Atualizar gabarito
        novo_gabarito = {}
        for item_a, item_b in gabarito_original.items():
            if isinstance(item_b, int):
                novo_gabarito[item_a] = mapeamento_b.get(item_b, item_b)
            else:
                novo_gabarito[item_a] = item_b
        
        questao_copy['coluna_b'] = nova_coluna_b
        questao_copy['gabarito_associacao'] = novo_gabarito
        questao_copy['mapeamento_coluna_b'] = mapeamento_b
        
        return questao_copy
    
    def embaralhar_questoes(
        self,
        questoes: List[Dict],
        seed_adicional: int = 0
    ) -> Tuple[List[Dict], List[MapeamentoQuestao]]:
        """
        Embaralha a ordem das questões.
        
        Args:
            questoes: Lista de questões
            seed_adicional: Seed para variar embaralhamento
        
        Returns:
            Tupla (questoes_embaralhadas, mapeamento)
        """
        questoes_copy = deepcopy(questoes)
        
        if self.seed:
            random.seed(self.seed + seed_adicional)
        
        # Criar lista de índices e embaralhar
        indices = list(range(len(questoes_copy)))
        random.shuffle(indices)
        
        # Reorganizar questões e criar mapeamento
        questoes_embaralhadas = []
        mapeamento = []
        
        for nova_pos, indice_original in enumerate(indices):
            questao = questoes_copy[indice_original]
            questao_id = questao.get('id', str(indice_original))
            
            # Atualizar número da questão
            questao['numero'] = nova_pos + 1
            questao['numero_original'] = indice_original + 1
            
            questoes_embaralhadas.append(questao)
            
            mapeamento.append(MapeamentoQuestao(
                questao_id=questao_id,
                posicao_original=indice_original + 1,
                nova_posicao=nova_pos + 1
            ))
        
        return questoes_embaralhadas, mapeamento
    
    def gerar_prova_embaralhada(
        self,
        questoes: List[Dict],
        numero_aluno: int,
        embaralhar_questoes: bool = True,
        embaralhar_alternativas: bool = True
    ) -> ProvaEmbaralhada:
        """
        Gera uma versão embaralhada completa da prova para um aluno.
        
        Suporta diferentes tipos de questão:
        - multipla_escolha: Embaralha alternativas normalmente
        - verdadeiro_falso: NÃO embaralha alternativas (mantém V/F)
        - dissertativa: Não tem alternativas, gabarito é a resposta
        - numerica: Gabarito é o número
        - multipla_resposta: Embaralha, gabarito tem múltiplas letras
        - associacao: Embaralha coluna B
        
        Args:
            questoes: Lista de questões originais
            numero_aluno: Número do aluno (1, 2, 3...)
            embaralhar_questoes: Se deve embaralhar ordem das questões
            embaralhar_alternativas: Se deve embaralhar alternativas
        
        Returns:
            ProvaEmbaralhada com todos os mapeamentos
        """
        # Usar número do aluno como seed adicional para garantir unicidade
        seed_aluno = numero_aluno * 1000
        
        # Embaralhar questões (se configurado)
        if embaralhar_questoes:
            questoes_processadas, mapeamento_questoes = self.embaralhar_questoes(
                questoes, seed_aluno
            )
        else:
            questoes_processadas = deepcopy(questoes)
            mapeamento_questoes = [
                MapeamentoQuestao(
                    questao_id=q.get('id', str(i)),
                    posicao_original=i + 1,
                    nova_posicao=i + 1
                )
                for i, q in enumerate(questoes)
            ]
        
        # Processar cada questão conforme seu tipo
        mapeamento_alternativas = {}
        gabarito = {}
        
        for i, questao in enumerate(questoes_processadas):
            questao_id = questao.get('id', str(i))
            numero_questao = i + 1
            numero_str = str(numero_questao)
            
            # Identificar tipo da questão
            tipo_questao = self.identificar_tipo_questao(questao)
            questao['tipo_identificado'] = tipo_questao.value
            
            alternativas = questao.get('alternativas', [])
            
            # Processar conforme o tipo
            if tipo_questao == TipoQuestao.DISSERTATIVA:
                # Dissertativa: gabarito é a resposta textual
                resposta = questao.get('resposta', '')
                gabarito[numero_str] = resposta[:200] if resposta else 'Resposta aberta'
            
            elif tipo_questao == TipoQuestao.NUMERICA:
                # Numérica: gabarito é o número
                resposta = questao.get('resposta', '0')
                tolerancia = questao.get('tolerancia', 0)
                if tolerancia:
                    gabarito[numero_str] = f"{resposta} (±{tolerancia})"
                else:
                    gabarito[numero_str] = str(resposta)
            
            elif tipo_questao == TipoQuestao.ASSOCIACAO:
                # Associação: embaralhar coluna B
                if embaralhar_alternativas:
                    questao_emb = self.embaralhar_associacao(questao, seed_aluno + i)
                    questao.update(questao_emb)
                gabarito[numero_str] = questao.get('gabarito_associacao', {})
            
            elif tipo_questao == TipoQuestao.VERDADEIRO_FALSO:
                # V/F: não embaralha, apenas padroniza
                alt_processadas, mapeamento_alt = self._processar_verdadeiro_falso(
                    alternativas, questao_id, numero_questao
                )
                questao['alternativas'] = alt_processadas
                if mapeamento_alt:
                    mapeamento_alternativas[numero_str] = mapeamento_alt
                    gabarito[numero_str] = mapeamento_alt.correta_nova
            
            elif alternativas and embaralhar_alternativas:
                # Múltipla escolha ou múltipla resposta: embaralhar
                alt_embaralhadas, mapeamento_alt = self.embaralhar_alternativas(
                    alternativas,
                    questao_id,
                    numero_questao,
                    seed_aluno + i,
                    tipo_questao
                )
                
                questao['alternativas'] = alt_embaralhadas
                
                if mapeamento_alt:
                    mapeamento_alternativas[numero_str] = mapeamento_alt
                    gabarito[numero_str] = mapeamento_alt.correta_nova
            
            else:
                # Sem embaralhamento: manter original
                if alternativas:
                    if tipo_questao == TipoQuestao.MULTIPLA_RESPOSTA:
                        # Múltiplas corretas
                        corretas = [a.get('letra', 'A') for a in alternativas if a.get('correta')]
                        gabarito[numero_str] = corretas if corretas else ['A']
                    else:
                        # Uma correta
                        for alt in alternativas:
                            if alt.get('correta', False):
                                gabarito[numero_str] = alt.get('letra', 'A')
                                break
                else:
                    resposta = questao.get('resposta', '')
                    gabarito[numero_str] = resposta[:100] if resposta else ''
        
        # Gerar código único da prova
        codigo_prova = self._gerar_codigo_prova(numero_aluno)
        
        # Gerar hash de verificação
        hash_verificacao = self._gerar_hash_verificacao(
            questoes_processadas,
            mapeamento_alternativas,
            gabarito
        )
        
        return ProvaEmbaralhada(
            numero_aluno=numero_aluno,
            codigo_prova=codigo_prova,
            questoes=questoes_processadas,
            ordem_questoes=mapeamento_questoes,
            ordem_alternativas=mapeamento_alternativas,
            gabarito=gabarito,
            hash_verificacao=hash_verificacao
        )
    
    def gerar_multiplas_provas(
        self,
        questoes: List[Dict],
        quantidade_alunos: int,
        embaralhar_questoes: bool = True,
        embaralhar_alternativas: bool = True
    ) -> List[ProvaEmbaralhada]:
        """
        Gera múltiplas versões embaralhadas da prova.
        
        Args:
            questoes: Lista de questões originais
            quantidade_alunos: Número de provas a gerar
            embaralhar_questoes: Se deve embaralhar ordem das questões
            embaralhar_alternativas: Se deve embaralhar alternativas
        
        Returns:
            Lista de ProvaEmbaralhada
        """
        logger.info(f"Gerando {quantidade_alunos} provas embaralhadas")
        
        provas = []
        codigos_usados = set()
        
        for i in range(1, quantidade_alunos + 1):
            prova = self.gerar_prova_embaralhada(
                questoes=questoes,
                numero_aluno=i,
                embaralhar_questoes=embaralhar_questoes,
                embaralhar_alternativas=embaralhar_alternativas
            )
            
            # Garantir código único
            while prova.codigo_prova in codigos_usados:
                prova = ProvaEmbaralhada(
                    numero_aluno=prova.numero_aluno,
                    codigo_prova=self._gerar_codigo_prova(i, extra=random.randint(1, 999)),
                    questoes=prova.questoes,
                    ordem_questoes=prova.ordem_questoes,
                    ordem_alternativas=prova.ordem_alternativas,
                    gabarito=prova.gabarito,
                    hash_verificacao=prova.hash_verificacao
                )
            
            codigos_usados.add(prova.codigo_prova)
            provas.append(prova)
        
        logger.info(f"Geradas {len(provas)} provas únicas")
        
        return provas
    
    def _gerar_codigo_prova(self, numero_aluno: int, extra: int = 0) -> str:
        """Gera um código único para a prova."""
        # Formato: LETRA + NÚMERO (ex: A01, B02, C03...)
        letra_index = (numero_aluno - 1 + extra) % 26
        letra = chr(65 + letra_index)  # A-Z
        numero = ((numero_aluno - 1) // 26) + 1
        
        return f"{letra}{numero:02d}"
    
    def _gerar_hash_verificacao(
        self,
        questoes: List[Dict],
        mapeamento_alternativas: Dict,
        gabarito: Dict
    ) -> str:
        """Gera hash para verificação de integridade."""
        dados = {
            'questoes_ids': [q.get('id', '') for q in questoes],
            'mapeamento': {k: v.mapeamento if hasattr(v, 'mapeamento') else v 
                          for k, v in mapeamento_alternativas.items()},
            'gabarito': gabarito
        }
        
        dados_str = json.dumps(dados, sort_keys=True)
        return hashlib.sha256(dados_str.encode()).hexdigest()[:16]
    
    def verificar_integridade(
        self,
        prova: ProvaEmbaralhada,
        hash_original: str
    ) -> bool:
        """Verifica se uma prova não foi alterada."""
        hash_atual = self._gerar_hash_verificacao(
            prova.questoes,
            prova.ordem_alternativas,
            prova.gabarito
        )
        return hash_atual == hash_original
    
    def converter_para_dict(self, prova: ProvaEmbaralhada) -> Dict:
        """Converte ProvaEmbaralhada para dicionário serializável."""
        return {
            'numero_aluno': prova.numero_aluno,
            'codigo_prova': prova.codigo_prova,
            'questoes': prova.questoes,
            'ordem_questoes': [
                {
                    'questao_id': m.questao_id,
                    'posicao_original': m.posicao_original,
                    'nova_posicao': m.nova_posicao
                }
                for m in prova.ordem_questoes
            ],
            'ordem_alternativas': {
                k: {
                    'questao_id': v.questao_id,
                    'numero_questao': v.numero_questao,
                    'mapeamento': v.mapeamento,
                    'correta_original': v.correta_original,
                    'correta_nova': v.correta_nova
                }
                for k, v in prova.ordem_alternativas.items()
            },
            'gabarito': prova.gabarito,
            'hash_verificacao': prova.hash_verificacao
        }
    
    def gerar_gabarito_consolidado(
        self,
        provas: List[ProvaEmbaralhada]
    ) -> Dict[str, Dict]:
        """
        Gera um gabarito consolidado de todas as provas.
        
        Args:
            provas: Lista de provas embaralhadas
        
        Returns:
            Dicionário com gabarito de cada versão
        """
        return {
            prova.codigo_prova: {
                'numero_aluno': prova.numero_aluno,
                'gabarito': prova.gabarito,
                'hash': prova.hash_verificacao
            }
            for prova in provas
        }


# Instância global do serviço
embaralhamento_service = EmbaralhamentoService()

