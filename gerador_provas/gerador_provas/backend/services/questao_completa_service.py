"""
Serviço de Questão Completa - Gera e gerencia questões com explicações detalhadas.

As questões já nascem completas com:
- Enunciado
- Alternativas com explicação individual (corretas e incorretas)
- Explicação geral
- Fontes bibliográficas
- Erros comuns dos alunos
- Critérios de correção (para dissertativas)

O professor pode revisar e editar todas essas informações antes de aprovar.
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from copy import deepcopy
import uuid

from backend.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AlternativaComentada:
    """Uma alternativa com explicação completa."""
    letra: str
    texto: str
    correta: bool
    explicacao: str  # Por que está certa ou errada
    erro_conceitual: Optional[str] = None  # Tipo de erro (para incorretas)
    dica_professor: Optional[str] = None  # Dica para o professor
    conceitos_envolvidos: List[str] = field(default_factory=list)


@dataclass
class ErroComum:
    """Erro comum cometido por alunos."""
    erro: str
    frequencia: str  # alta, media, baixa
    como_identificar: str
    como_corrigir: str


@dataclass
class FonteBibliografica:
    """Referência bibliográfica."""
    tipo: str  # livro, artigo, site
    autor: str
    titulo: str
    ano: Optional[int] = None
    editora: Optional[str] = None
    edicao: Optional[str] = None
    paginas: Optional[str] = None
    revista: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    relevancia: Optional[str] = None  # Por que esta fonte é relevante


@dataclass
class CriterioCorrecao:
    """Critério de correção para questões dissertativas."""
    descricao: str
    peso: float
    obrigatorio: bool = False


@dataclass
class QuestaoCompleta:
    """
    Questão completa com todas as informações para o professor.
    
    Esta estrutura contém tudo que o professor precisa para:
    - Revisar a qualidade da questão
    - Corrigir provas
    - Dar feedback aos alunos
    """
    id: str
    tipo: str  # multipla_escolha, verdadeiro_falso, dissertativa, numerica
    enunciado: str
    
    # Alternativas comentadas (para objetivas)
    alternativas: List[AlternativaComentada] = field(default_factory=list)
    
    # Resposta (para dissertativas e numéricas)
    resposta: Optional[str] = None
    tolerancia: Optional[float] = None  # Para numéricas
    
    # Explicações
    explicacao_geral: Optional[str] = None
    resolucao_passo_a_passo: Optional[str] = None
    
    # Metadados pedagógicos
    erros_comuns: List[ErroComum] = field(default_factory=list)
    pontos_chave: List[str] = field(default_factory=list)
    dicas_correcao: List[str] = field(default_factory=list)
    
    # Critérios (para dissertativas)
    criterios_correcao: List[CriterioCorrecao] = field(default_factory=list)
    
    # Fontes
    fontes_bibliograficas: List[FonteBibliografica] = field(default_factory=list)
    
    # Classificação
    nivel_cognitivo: Optional[str] = None  # Taxonomia de Bloom
    dificuldade: str = "medio"
    tempo_estimado_min: int = 3
    palavras_chave: List[str] = field(default_factory=list)
    
    # Controle
    status: str = "rascunho"
    versao: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class QuestaoCompletaService:
    """
    Serviço para gerenciar questões completas com explicações.
    
    Responsabilidades:
    - Criar estrutura de questão completa
    - Validar completude das informações
    - Converter para/de formato do banco de dados
    - Preparar questão para prova do aluno (sem explicações)
    - Preparar questão para prova do professor (com tudo)
    """
    
    NIVEIS_COGNITIVOS = [
        "lembrar",    # Recordar fatos
        "entender",   # Compreender significados
        "aplicar",    # Usar em situações novas
        "analisar",   # Identificar partes e relações
        "avaliar",    # Fazer julgamentos
        "criar"       # Produzir algo novo
    ]
    
    TIPOS_QUESTAO = [
        "multipla_escolha",
        "verdadeiro_falso", 
        "dissertativa",
        "numerica",
        "associacao",
        "multipla_resposta"
    ]
    
    def __init__(self):
        self.questoes_cache = {}
    
    def criar_questao_completa(
        self,
        tipo: str,
        enunciado: str,
        alternativas: List[Dict] = None,
        resposta: str = None,
        explicacao_geral: str = None,
        fontes: List[Dict] = None,
        erros_comuns: List[Dict] = None,
        **kwargs
    ) -> QuestaoCompleta:
        """
        Cria uma questão completa com todas as informações.
        
        Args:
            tipo: Tipo da questão
            enunciado: Texto do enunciado
            alternativas: Lista de alternativas com explicações
            resposta: Resposta (para dissertativas/numéricas)
            explicacao_geral: Explicação geral
            fontes: Fontes bibliográficas
            erros_comuns: Erros comuns dos alunos
            **kwargs: Outros campos opcionais
        
        Returns:
            QuestaoCompleta
        """
        questao_id = kwargs.get('id', str(uuid.uuid4()))
        
        # Processar alternativas
        alts_comentadas = []
        if alternativas:
            for alt in alternativas:
                alts_comentadas.append(AlternativaComentada(
                    letra=alt.get('letra', '?'),
                    texto=alt.get('texto', ''),
                    correta=alt.get('correta', False),
                    explicacao=alt.get('explicacao', ''),
                    erro_conceitual=alt.get('erro_conceitual'),
                    dica_professor=alt.get('dica_professor'),
                    conceitos_envolvidos=alt.get('conceitos_envolvidos', [])
                ))
        
        # Processar erros comuns
        erros = []
        if erros_comuns:
            for erro in erros_comuns:
                erros.append(ErroComum(
                    erro=erro.get('erro', ''),
                    frequencia=erro.get('frequencia', 'media'),
                    como_identificar=erro.get('como_identificar', ''),
                    como_corrigir=erro.get('como_corrigir', '')
                ))
        
        # Processar fontes
        fontes_obj = []
        if fontes:
            for fonte in fontes:
                fontes_obj.append(FonteBibliografica(
                    tipo=fonte.get('tipo', 'livro'),
                    autor=fonte.get('autor', ''),
                    titulo=fonte.get('titulo', ''),
                    ano=fonte.get('ano'),
                    editora=fonte.get('editora'),
                    edicao=fonte.get('edicao'),
                    paginas=fonte.get('paginas'),
                    revista=fonte.get('revista'),
                    doi=fonte.get('doi'),
                    url=fonte.get('url'),
                    relevancia=fonte.get('relevancia')
                ))
        
        # Processar critérios de correção
        criterios = []
        if kwargs.get('criterios_correcao'):
            for crit in kwargs['criterios_correcao']:
                criterios.append(CriterioCorrecao(
                    descricao=crit.get('descricao', ''),
                    peso=crit.get('peso', 1.0),
                    obrigatorio=crit.get('obrigatorio', False)
                ))
        
        questao = QuestaoCompleta(
            id=questao_id,
            tipo=tipo,
            enunciado=enunciado,
            alternativas=alts_comentadas,
            resposta=resposta,
            tolerancia=kwargs.get('tolerancia'),
            explicacao_geral=explicacao_geral,
            resolucao_passo_a_passo=kwargs.get('resolucao_passo_a_passo'),
            erros_comuns=erros,
            pontos_chave=kwargs.get('pontos_chave', []),
            dicas_correcao=kwargs.get('dicas_correcao', []),
            criterios_correcao=criterios,
            fontes_bibliograficas=fontes_obj,
            nivel_cognitivo=kwargs.get('nivel_cognitivo'),
            dificuldade=kwargs.get('dificuldade', 'medio'),
            tempo_estimado_min=kwargs.get('tempo_estimado_min', 3),
            palavras_chave=kwargs.get('palavras_chave', []),
            status=kwargs.get('status', 'rascunho'),
            versao=kwargs.get('versao', 1),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return questao
    
    def validar_completude(self, questao: QuestaoCompleta) -> Dict[str, Any]:
        """
        Valida se a questão está completa para aprovação.
        
        Returns:
            Dict com:
            - completa: bool
            - itens_faltando: List[str]
            - porcentagem: int
            - avisos: List[str]
        """
        itens_faltando = []
        avisos = []
        total_itens = 0
        itens_ok = 0
        
        # Enunciado (obrigatório)
        total_itens += 1
        if questao.enunciado and len(questao.enunciado) > 10:
            itens_ok += 1
        else:
            itens_faltando.append("Enunciado")
        
        # Alternativas com explicações (para objetivas)
        if questao.tipo in ['multipla_escolha', 'verdadeiro_falso', 'multipla_resposta']:
            total_itens += 1
            if questao.alternativas and len(questao.alternativas) >= 2:
                itens_ok += 1
                
                # Verificar se todas têm explicação
                total_itens += 1
                todas_tem_explicacao = all(
                    alt.explicacao and len(alt.explicacao) > 5 
                    for alt in questao.alternativas
                )
                if todas_tem_explicacao:
                    itens_ok += 1
                else:
                    itens_faltando.append("Explicação de todas as alternativas")
                
                # Verificar se tem pelo menos uma correta
                tem_correta = any(alt.correta for alt in questao.alternativas)
                if not tem_correta:
                    itens_faltando.append("Alternativa correta não marcada")
            else:
                itens_faltando.append("Alternativas")
        
        # Resposta (para dissertativas e numéricas)
        if questao.tipo in ['dissertativa', 'numerica']:
            total_itens += 1
            if questao.resposta and len(str(questao.resposta)) > 0:
                itens_ok += 1
            else:
                itens_faltando.append("Resposta esperada")
            
            # Critérios de correção para dissertativas
            if questao.tipo == 'dissertativa':
                total_itens += 1
                if questao.criterios_correcao and len(questao.criterios_correcao) > 0:
                    itens_ok += 1
                else:
                    avisos.append("Recomendado: adicionar critérios de correção")
        
        # Explicação geral
        total_itens += 1
        if questao.explicacao_geral and len(questao.explicacao_geral) > 10:
            itens_ok += 1
        else:
            itens_faltando.append("Explicação geral")
        
        # Fontes bibliográficas
        total_itens += 1
        if questao.fontes_bibliograficas and len(questao.fontes_bibliograficas) > 0:
            itens_ok += 1
        else:
            avisos.append("Recomendado: adicionar fontes bibliográficas")
        
        # Erros comuns
        total_itens += 1
        if questao.erros_comuns and len(questao.erros_comuns) > 0:
            itens_ok += 1
        else:
            avisos.append("Recomendado: adicionar erros comuns dos alunos")
        
        porcentagem = int((itens_ok / total_itens) * 100) if total_itens > 0 else 0
        
        return {
            'completa': len(itens_faltando) == 0,
            'itens_faltando': itens_faltando,
            'porcentagem': porcentagem,
            'avisos': avisos,
            'itens_ok': itens_ok,
            'total_itens': total_itens
        }
    
    def para_prova_aluno(self, questao: QuestaoCompleta) -> Dict:
        """
        Converte questão para formato de prova do ALUNO.
        Remove todas as explicações e respostas.
        
        Returns:
            Dict com apenas o necessário para o aluno responder
        """
        resultado = {
            'id': questao.id,
            'tipo': questao.tipo,
            'enunciado': questao.enunciado,
            'tempo_estimado_min': questao.tempo_estimado_min,
        }
        
        # Alternativas SEM explicações
        if questao.alternativas:
            resultado['alternativas'] = [
                {
                    'letra': alt.letra,
                    'texto': alt.texto,
                    # NÃO incluir: correta, explicacao, erro_conceitual, etc.
                }
                for alt in questao.alternativas
            ]
        
        # Para numéricas, incluir tolerância (aluno precisa saber precisão)
        if questao.tipo == 'numerica' and questao.tolerancia:
            resultado['tolerancia'] = questao.tolerancia
        
        return resultado
    
    def para_prova_professor(self, questao: QuestaoCompleta) -> Dict:
        """
        Converte questão para formato de prova do PROFESSOR.
        Inclui TODAS as informações.
        
        Returns:
            Dict com tudo para o professor corrigir e dar feedback
        """
        resultado = {
            'id': questao.id,
            'tipo': questao.tipo,
            'enunciado': questao.enunciado,
            'tempo_estimado_min': questao.tempo_estimado_min,
            'nivel_cognitivo': questao.nivel_cognitivo,
            'dificuldade': questao.dificuldade,
        }
        
        # Alternativas COM explicações completas
        if questao.alternativas:
            resultado['alternativas'] = [
                {
                    'letra': alt.letra,
                    'texto': alt.texto,
                    'correta': alt.correta,
                    'status': 'CORRETA' if alt.correta else 'INCORRETA',
                    'explicacao': alt.explicacao,
                    'erro_conceitual': alt.erro_conceitual,
                    'dica_professor': alt.dica_professor,
                    'conceitos_envolvidos': alt.conceitos_envolvidos,
                }
                for alt in questao.alternativas
            ]
        
        # Resposta
        if questao.resposta:
            resultado['resposta'] = questao.resposta
            if questao.tolerancia:
                resultado['tolerancia'] = questao.tolerancia
        
        # Explicações
        resultado['explicacao_geral'] = questao.explicacao_geral
        resultado['resolucao_passo_a_passo'] = questao.resolucao_passo_a_passo
        
        # Erros comuns
        resultado['erros_comuns'] = [
            {
                'erro': e.erro,
                'frequencia': e.frequencia,
                'como_identificar': e.como_identificar,
                'como_corrigir': e.como_corrigir
            }
            for e in questao.erros_comuns
        ]
        
        # Pontos-chave e dicas
        resultado['pontos_chave'] = questao.pontos_chave
        resultado['dicas_correcao'] = questao.dicas_correcao
        
        # Critérios de correção
        resultado['criterios_correcao'] = [
            {
                'descricao': c.descricao,
                'peso': c.peso,
                'obrigatorio': c.obrigatorio
            }
            for c in questao.criterios_correcao
        ]
        
        # Fontes bibliográficas
        resultado['fontes_bibliograficas'] = [
            {
                'tipo': f.tipo,
                'autor': f.autor,
                'titulo': f.titulo,
                'ano': f.ano,
                'editora': f.editora,
                'edicao': f.edicao,
                'paginas': f.paginas,
                'revista': f.revista,
                'doi': f.doi,
                'url': f.url,
                'relevancia': f.relevancia
            }
            for f in questao.fontes_bibliograficas
        ]
        
        # Palavras-chave
        resultado['palavras_chave'] = questao.palavras_chave
        
        return resultado
    
    def para_banco_dados(self, questao: QuestaoCompleta) -> Dict:
        """
        Converte questão para formato do banco de dados.
        
        Returns:
            Dict pronto para inserir/atualizar no PostgreSQL
        """
        # Alternativas comentadas como JSONB
        alternativas_json = None
        if questao.alternativas:
            alternativas_json = {
                'alternativas': [
                    {
                        'letra': alt.letra,
                        'texto': alt.texto,
                        'correta': alt.correta,
                        'explicacao': alt.explicacao,
                        'erro_conceitual': alt.erro_conceitual,
                        'dica_professor': alt.dica_professor,
                        'conceitos_envolvidos': alt.conceitos_envolvidos
                    }
                    for alt in questao.alternativas
                ]
            }
        
        # Erros comuns como JSONB
        erros_json = [
            {
                'erro': e.erro,
                'frequencia': e.frequencia,
                'como_identificar': e.como_identificar,
                'como_corrigir': e.como_corrigir
            }
            for e in questao.erros_comuns
        ] if questao.erros_comuns else None
        
        # Fontes como JSONB
        fontes_json = [
            {
                'tipo': f.tipo,
                'autor': f.autor,
                'titulo': f.titulo,
                'ano': f.ano,
                'editora': f.editora,
                'edicao': f.edicao,
                'paginas': f.paginas,
                'revista': f.revista,
                'doi': f.doi,
                'url': f.url,
                'relevancia': f.relevancia
            }
            for f in questao.fontes_bibliograficas
        ] if questao.fontes_bibliograficas else None
        
        # Critérios como JSONB
        criterios_json = {
            'criterios': [
                {
                    'descricao': c.descricao,
                    'peso': c.peso,
                    'obrigatorio': c.obrigatorio
                }
                for c in questao.criterios_correcao
            ]
        } if questao.criterios_correcao else None
        
        return {
            'id': questao.id,
            'tipo': questao.tipo,
            'enunciado': questao.enunciado,
            'alternativas_comentadas': json.dumps(alternativas_json) if alternativas_json else None,
            'resposta': questao.resposta,
            'explicacao_geral': questao.explicacao_geral,
            'resolucao_passo_a_passo': questao.resolucao_passo_a_passo,
            'erros_comuns': json.dumps(erros_json) if erros_json else None,
            'fontes_bibliograficas': json.dumps(fontes_json) if fontes_json else None,
            'criterios_correcao': json.dumps(criterios_json) if criterios_json else None,
            'pontos_chave': json.dumps(questao.pontos_chave) if questao.pontos_chave else None,
            'dicas_correcao': json.dumps(questao.dicas_correcao) if questao.dicas_correcao else None,
            'nivel_cognitivo': questao.nivel_cognitivo,
            'dificuldade': questao.dificuldade,
            'tempo_estimado_min': questao.tempo_estimado_min,
            'palavras_chave': json.dumps(questao.palavras_chave) if questao.palavras_chave else None,
            'status': questao.status,
            'versao_atual': questao.versao,
            'updated_at': datetime.now()
        }
    
    def do_banco_dados(self, row: Dict) -> QuestaoCompleta:
        """
        Converte registro do banco de dados para QuestaoCompleta.
        
        Args:
            row: Registro do banco (dict ou Row)
        
        Returns:
            QuestaoCompleta
        """
        # Processar alternativas do JSON
        alternativas = []
        alt_json = row.get('alternativas_comentadas')
        if alt_json:
            if isinstance(alt_json, str):
                alt_json = json.loads(alt_json)
            for alt in alt_json.get('alternativas', []):
                alternativas.append(AlternativaComentada(
                    letra=alt.get('letra', '?'),
                    texto=alt.get('texto', ''),
                    correta=alt.get('correta', False),
                    explicacao=alt.get('explicacao', ''),
                    erro_conceitual=alt.get('erro_conceitual'),
                    dica_professor=alt.get('dica_professor'),
                    conceitos_envolvidos=alt.get('conceitos_envolvidos', [])
                ))
        
        # Processar erros comuns
        erros = []
        erros_json = row.get('erros_comuns')
        if erros_json:
            if isinstance(erros_json, str):
                erros_json = json.loads(erros_json)
            for e in erros_json:
                erros.append(ErroComum(
                    erro=e.get('erro', ''),
                    frequencia=e.get('frequencia', 'media'),
                    como_identificar=e.get('como_identificar', ''),
                    como_corrigir=e.get('como_corrigir', '')
                ))
        
        # Processar fontes
        fontes = []
        fontes_json = row.get('fontes_bibliograficas')
        if fontes_json:
            if isinstance(fontes_json, str):
                fontes_json = json.loads(fontes_json)
            for f in fontes_json:
                fontes.append(FonteBibliografica(
                    tipo=f.get('tipo', 'livro'),
                    autor=f.get('autor', ''),
                    titulo=f.get('titulo', ''),
                    ano=f.get('ano'),
                    editora=f.get('editora'),
                    edicao=f.get('edicao'),
                    paginas=f.get('paginas'),
                    revista=f.get('revista'),
                    doi=f.get('doi'),
                    url=f.get('url'),
                    relevancia=f.get('relevancia')
                ))
        
        # Processar critérios
        criterios = []
        crit_json = row.get('criterios_correcao')
        if crit_json:
            if isinstance(crit_json, str):
                crit_json = json.loads(crit_json)
            for c in crit_json.get('criterios', []):
                criterios.append(CriterioCorrecao(
                    descricao=c.get('descricao', ''),
                    peso=c.get('peso', 1.0),
                    obrigatorio=c.get('obrigatorio', False)
                ))
        
        # Processar listas JSON
        pontos_chave = row.get('pontos_chave', [])
        if isinstance(pontos_chave, str):
            pontos_chave = json.loads(pontos_chave)
        
        dicas_correcao = row.get('dicas_correcao', [])
        if isinstance(dicas_correcao, str):
            dicas_correcao = json.loads(dicas_correcao)
        
        palavras_chave = row.get('palavras_chave', [])
        if isinstance(palavras_chave, str):
            palavras_chave = json.loads(palavras_chave)
        
        return QuestaoCompleta(
            id=str(row.get('id', '')),
            tipo=row.get('tipo', 'multipla_escolha'),
            enunciado=row.get('enunciado', ''),
            alternativas=alternativas,
            resposta=row.get('resposta'),
            tolerancia=row.get('tolerancia'),
            explicacao_geral=row.get('explicacao_geral'),
            resolucao_passo_a_passo=row.get('resolucao_passo_a_passo'),
            erros_comuns=erros,
            pontos_chave=pontos_chave or [],
            dicas_correcao=dicas_correcao or [],
            criterios_correcao=criterios,
            fontes_bibliograficas=fontes,
            nivel_cognitivo=row.get('nivel_cognitivo'),
            dificuldade=row.get('dificuldade', 'medio'),
            tempo_estimado_min=row.get('tempo_estimado_min', 3),
            palavras_chave=palavras_chave or [],
            status=row.get('status', 'rascunho'),
            versao=row.get('versao_atual', 1),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    def gerar_prompt_ia(
        self,
        tipo: str,
        topico: str,
        dificuldade: str = "medio",
        contexto: str = None
    ) -> str:
        """
        Gera o prompt para a IA criar uma questão completa.
        
        Args:
            tipo: Tipo da questão
            topico: Tópico/assunto
            dificuldade: Nível de dificuldade
            contexto: Contexto adicional (curso, disciplina, etc.)
        
        Returns:
            Prompt formatado para a IA
        """
        prompts = {
            'multipla_escolha': f"""
Gere uma questão de MÚLTIPLA ESCOLHA completa sobre: {topico}

ESTRUTURA OBRIGATÓRIA:

1. ENUNCIADO
   - Claro e objetivo
   - Sem ambiguidades
   - Contextualizado quando apropriado

2. ALTERNATIVAS (5 opções: A, B, C, D, E)
   - Apenas UMA correta
   - Para CADA alternativa, forneça:
     * Texto da alternativa
     * Se é correta (true/false)
     * EXPLICAÇÃO DETALHADA:
       - Se CORRETA: Por que está certa, conceitos envolvidos
       - Se INCORRETA: Por que está errada, qual erro conceitual representa
     * Dica para o professor (opcional)

3. EXPLICAÇÃO GERAL
   - Resumo do conceito abordado
   - Contexto teórico

4. ERROS COMUNS DOS ALUNOS
   - Liste 2-3 erros frequentes
   - Como identificar cada erro
   - Como corrigir/explicar

5. FONTES BIBLIOGRÁFICAS
   - Pelo menos 1 referência
   - Preferencialmente livros-texto reconhecidos

PARÂMETROS:
- Dificuldade: {dificuldade}
- Tempo estimado: 3 minutos
{f"- Contexto: {contexto}" if contexto else ""}

Responda em formato JSON estruturado.
""",
            'verdadeiro_falso': f"""
Gere uma questão de VERDADEIRO ou FALSO completa sobre: {topico}

ESTRUTURA OBRIGATÓRIA:

1. AFIRMAÇÃO
   - Clara e sem ambiguidades
   - Passível de ser verdadeira ou falsa

2. RESPOSTA
   - V (Verdadeiro) ou F (Falso)
   - EXPLICAÇÃO DETALHADA:
     * Se VERDADEIRO: Por que a afirmação está correta
     * Se FALSO: O que está errado e qual seria a forma correta

3. ARMADILHAS COMUNS
   - O que pode confundir o aluno
   - Palavras-chave a observar

4. EXPLICAÇÃO GERAL
   - Conceito teórico envolvido

5. FONTE BIBLIOGRÁFICA
   - Referência que sustenta a resposta

PARÂMETROS:
- Dificuldade: {dificuldade}
{f"- Contexto: {contexto}" if contexto else ""}

Responda em formato JSON estruturado.
""",
            'dissertativa': f"""
Gere uma questão DISSERTATIVA completa sobre: {topico}

ESTRUTURA OBRIGATÓRIA:

1. ENUNCIADO
   - Pergunta clara que permita resposta elaborada
   - Delimitação do escopo esperado

2. RESPOSTA ESPERADA
   - Resposta modelo completa
   - Todos os pontos que devem ser abordados

3. CRITÉRIOS DE CORREÇÃO
   Para cada critério:
   - Descrição do que avaliar
   - Peso/pontuação
   - Se é obrigatório ou bonus

4. PONTOS-CHAVE
   - Conceitos essenciais que devem aparecer
   - Termos técnicos esperados

5. ERROS COMUNS
   - O que alunos costumam esquecer
   - Confusões conceituais frequentes

6. DICAS DE CORREÇÃO
   - Como avaliar respostas parciais
   - Critérios para notas intermediárias

7. FONTES BIBLIOGRÁFICAS
   - Referências que embasam a resposta

PARÂMETROS:
- Dificuldade: {dificuldade}
- Pontuação máxima sugerida: 10 pontos
{f"- Contexto: {contexto}" if contexto else ""}

Responda em formato JSON estruturado.
"""
        }
        
        return prompts.get(tipo, prompts['multipla_escolha'])


# Instância global do serviço
questao_completa_service = QuestaoCompletaService()

