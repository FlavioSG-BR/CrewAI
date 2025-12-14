"""
Serviço de Provas Individuais - Gera N provas únicas para uma turma.

Este serviço integra:
- Seleção de questões do banco
- Embaralhamento de questões e alternativas
- Geração de PDFs individuais
- Criação de gabaritos únicos
- Empacotamento em ZIP
"""

import os
import json
import zipfile
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from copy import deepcopy
import uuid

from backend.services.embaralhamento_service import EmbaralhamentoService, ProvaEmbaralhada
from backend.services.revisao_service import RevisaoService
from backend.utils.prova_pdf_generator import ProvaPDFGenerator
from backend.utils.logger import get_logger
from config import settings

logger = get_logger(__name__)


@dataclass
class ConfiguracaoProvaIndividual:
    """Configuração para geração de provas individuais."""
    titulo: str
    questoes_ids: List[str]
    quantidade_alunos: int
    embaralhar_questoes: bool = True
    embaralhar_alternativas: bool = True
    instituicao: Optional[str] = None
    instrucoes: Optional[List[str]] = None
    tempo_limite_min: Optional[int] = None
    incluir_campo_nome: bool = True
    incluir_campo_matricula: bool = True
    gerar_pdf: bool = True
    gerar_zip: bool = True
    gerar_prova_professor: bool = True  # Gera prova mestre comentada


@dataclass
class ProvaProfessor:
    """Prova do professor com gabarito e comentários."""
    titulo: str
    questoes: List[Dict]
    gabarito_completo: Dict[str, Any]
    comentarios: Dict[str, str]
    fontes_bibliograficas: List[Dict]
    caminho_pdf: Optional[str] = None
    total_questoes: int = 0
    resumo_por_tipo: Dict[str, int] = field(default_factory=dict)


@dataclass
class ResultadoLoteProvas:
    """Resultado da geração de um lote de provas."""
    lote_id: str
    titulo: str
    quantidade_alunos: int
    provas_geradas: int  # N alunos + 1 professor
    provas_alunos: List[Dict]  # Apenas provas dos alunos
    prova_professor: Optional[Dict] = None  # Prova mestre
    gabarito_consolidado: Dict = field(default_factory=dict)
    caminho_zip: Optional[str] = None
    tempo_geracao_seg: float = 0
    status: str = "concluido"
    erro: Optional[str] = None
    
    @property
    def provas(self) -> List[Dict]:
        """Compatibilidade: retorna todas as provas (alunos + professor)."""
        todas = list(self.provas_alunos)
        if self.prova_professor:
            todas.insert(0, self.prova_professor)
        return todas


class ProvaIndividualService:
    """
    Serviço para criação de provas individualizadas por aluno.
    
    Fluxo:
    1. Recebe lista de questões selecionadas + número de alunos
    2. Para cada aluno, gera uma versão com embaralhamento único
    3. Gera PDF individual + gabarito individual
    4. Empacota tudo em um ZIP
    """
    
    def __init__(self):
        self.embaralhamento = EmbaralhamentoService()
        self.revisao_service = RevisaoService()
        self.pdf_generator = ProvaPDFGenerator()
        
        # Diretório para provas geradas
        self.output_dir = os.path.join(settings.OUTPUT_DIR, "provas_individuais")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def obter_questoes_por_ids(self, questoes_ids: List[str]) -> List[Dict]:
        """
        Obtém questões do banco pelos IDs.
        
        Args:
            questoes_ids: Lista de IDs das questões
        
        Returns:
            Lista de questões
        """
        questoes = []
        
        for questao_id in questoes_ids:
            questao = self.revisao_service.obter_questao(questao_id)
            if questao:
                questoes.append(questao)
            else:
                logger.warning(f"Questão {questao_id} não encontrada")
        
        return questoes
    
    def gerar_provas_individuais(
        self,
        config: ConfiguracaoProvaIndividual
    ) -> ResultadoLoteProvas:
        """
        Gera um lote de provas individuais para todos os alunos + prova do professor.
        
        Gera N+1 provas:
        - 1 Prova do Professor (mestre, comentada, com respostas)
        - N Provas dos Alunos (embaralhadas, sem respostas)
        
        Args:
            config: Configuração do lote de provas
        
        Returns:
            ResultadoLoteProvas com todas as provas geradas
        """
        inicio = datetime.now()
        lote_id = str(uuid.uuid4())[:8]
        
        total_provas = config.quantidade_alunos + (1 if config.gerar_prova_professor else 0)
        logger.info(f"Iniciando geração de {total_provas} provas ({config.quantidade_alunos} alunos + professor) - Lote {lote_id}")
        
        try:
            # 1. Obter questões selecionadas
            questoes = self.obter_questoes_por_ids(config.questoes_ids)
            
            if not questoes:
                return ResultadoLoteProvas(
                    lote_id=lote_id,
                    titulo=config.titulo,
                    quantidade_alunos=config.quantidade_alunos,
                    provas_geradas=0,
                    provas_alunos=[],
                    prova_professor=None,
                    gabarito_consolidado={},
                    status="erro",
                    erro="Nenhuma questão encontrada com os IDs fornecidos"
                )
            
            logger.info(f"Encontradas {len(questoes)} questões")
            
            # 2. Criar diretório do lote
            data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_lote = f"{config.titulo.replace(' ', '_').lower()}_{data_hora}"
            lote_dir = os.path.join(self.output_dir, nome_lote)
            os.makedirs(lote_dir, exist_ok=True)
            
            provas_dir = os.path.join(lote_dir, "provas_alunos")
            gabaritos_dir = os.path.join(lote_dir, "gabaritos")
            professor_dir = os.path.join(lote_dir, "prova_professor")
            os.makedirs(provas_dir, exist_ok=True)
            os.makedirs(gabaritos_dir, exist_ok=True)
            os.makedirs(professor_dir, exist_ok=True)
            
            # 3. Gerar PROVA DO PROFESSOR (mestre, comentada)
            prova_professor_dict = None
            if config.gerar_prova_professor:
                prova_professor_dict = self._gerar_prova_professor(
                    questoes=questoes,
                    config=config,
                    output_dir=professor_dir
                )
                logger.info("Prova do professor gerada")
            
            # 4. Gerar provas embaralhadas para os alunos
            provas_embaralhadas = self.embaralhamento.gerar_multiplas_provas(
                questoes=questoes,
                quantidade_alunos=config.quantidade_alunos,
                embaralhar_questoes=config.embaralhar_questoes,
                embaralhar_alternativas=config.embaralhar_alternativas
            )
            
            # 5. Gerar PDFs dos alunos
            provas_alunos = []
            
            for prova in provas_embaralhadas:
                prova_dict = self._preparar_prova_para_pdf(prova, config)
                
                if config.gerar_pdf:
                    try:
                        # Gerar PDF da prova do aluno
                        nome_prova = f"prova_{prova.codigo_prova}"
                        caminho_prova = self.pdf_generator.gerar_prova_pdf(
                            prova_dict,
                            nome_arquivo=nome_prova,
                            output_dir=provas_dir,
                            instituicao=config.instituicao,
                            instrucoes=config.instrucoes
                        )
                        
                        # Gerar PDF do gabarito individual
                        nome_gabarito = f"gabarito_{prova.codigo_prova}"
                        caminho_gabarito = self.pdf_generator.gerar_gabarito_pdf(
                            prova_dict,
                            nome_arquivo=nome_gabarito,
                            output_dir=gabaritos_dir
                        )
                        
                        prova_dict['caminho_pdf'] = caminho_prova
                        prova_dict['caminho_gabarito'] = caminho_gabarito
                        
                    except Exception as e:
                        logger.error(f"Erro ao gerar PDF da prova {prova.codigo_prova}: {e}")
                        prova_dict['erro_pdf'] = str(e)
                
                provas_alunos.append(prova_dict)
            
            # 6. Gerar gabarito consolidado
            gabarito_consolidado = self.embaralhamento.gerar_gabarito_consolidado(provas_embaralhadas)
            
            # Adicionar prova do professor ao gabarito
            if prova_professor_dict:
                gabarito_consolidado["PROFESSOR"] = {
                    "numero_aluno": 0,
                    "gabarito": prova_professor_dict.get("gabarito_completo", {}),
                    "hash": "master",
                    "comentada": True
                }
            
            # Salvar gabarito consolidado em JSON
            gabarito_path = os.path.join(lote_dir, "gabarito_consolidado.json")
            with open(gabarito_path, 'w', encoding='utf-8') as f:
                json.dump(gabarito_consolidado, f, ensure_ascii=False, indent=2)
            
            # 7. Criar ZIP
            caminho_zip = None
            if config.gerar_zip:
                caminho_zip = self._criar_zip_lote(lote_dir, nome_lote)
            
            # Calcular tempo
            fim = datetime.now()
            tempo_geracao = (fim - inicio).total_seconds()
            
            total_geradas = len(provas_alunos) + (1 if prova_professor_dict else 0)
            logger.info(f"Lote {lote_id} concluído: {total_geradas} provas em {tempo_geracao:.2f}s")
            
            return ResultadoLoteProvas(
                lote_id=lote_id,
                titulo=config.titulo,
                quantidade_alunos=config.quantidade_alunos,
                provas_geradas=total_geradas,
                provas_alunos=provas_alunos,
                prova_professor=prova_professor_dict,
                gabarito_consolidado=gabarito_consolidado,
                caminho_zip=caminho_zip,
                tempo_geracao_seg=tempo_geracao,
                status="concluido"
            )
            
        except Exception as e:
            logger.error(f"Erro ao gerar lote de provas: {e}")
            return ResultadoLoteProvas(
                lote_id=lote_id,
                titulo=config.titulo,
                quantidade_alunos=config.quantidade_alunos,
                provas_geradas=0,
                provas_alunos=[],
                prova_professor=None,
                gabarito_consolidado={},
                status="erro",
                erro=str(e)
            )
    
    def _gerar_prova_professor(
        self,
        questoes: List[Dict],
        config: ConfiguracaoProvaIndividual,
        output_dir: str
    ) -> Dict:
        """
        Gera a prova do professor (mestre) com gabarito completo e comentários.
        
        A prova do professor inclui:
        - Questões na ordem original (sem embaralhamento)
        - Resposta correta destacada em cada questão
        - Explicação DETALHADA de CADA alternativa:
          * Por que a correta está certa
          * Por que cada errada está errada
        - Comentários gerais e resolução
        - Fontes bibliográficas
        - Gabarito completo comentado
        
        Args:
            questoes: Lista de questões originais
            config: Configuração da prova
            output_dir: Diretório de saída
        
        Returns:
            Dicionário com dados da prova do professor
        """
        # Preparar questões com respostas e comentários
        questoes_comentadas = []
        gabarito_completo = {}
        comentarios = {}
        fontes_todas = []
        resumo_por_tipo = {}
        
        for i, questao in enumerate(questoes):
            numero = i + 1
            numero_str = str(numero)
            
            # Copiar questão
            q_comentada = deepcopy(questao)
            q_comentada['numero'] = numero
            
            # Identificar tipo
            tipo = q_comentada.get('tipo_questao', q_comentada.get('tipo_identificado', 'multipla_escolha'))
            resumo_por_tipo[tipo] = resumo_por_tipo.get(tipo, 0) + 1
            
            # Extrair resposta correta e processar alternativas
            alternativas = q_comentada.get('alternativas', [])
            resposta_correta = None
            
            if alternativas:
                # Processar cada alternativa com explicação
                corretas = []
                for alt in alternativas:
                    letra = alt.get('letra', '?')
                    
                    if alt.get('correta', False):
                        corretas.append(letra)
                        alt['destaque'] = True
                        alt['status'] = 'CORRETA'
                        
                        # Explicação de por que está correta
                        if not alt.get('explicacao'):
                            alt['explicacao'] = alt.get('justificativa', 
                                f"Esta é a alternativa correta. {alt.get('motivo_correto', '')}")
                    else:
                        alt['status'] = 'INCORRETA'
                        
                        # Explicação de por que está errada
                        if not alt.get('explicacao'):
                            # Tentar obter explicação do erro
                            alt['explicacao'] = alt.get('justificativa', 
                                alt.get('motivo_erro', 
                                    alt.get('erro_comum', 
                                        self._gerar_explicacao_erro_padrao(alt, letra))))
                
                if len(corretas) == 1:
                    resposta_correta = corretas[0]
                elif len(corretas) > 1:
                    resposta_correta = corretas
                else:
                    resposta_correta = 'N/A'
            else:
                # Dissertativa ou numérica
                resposta_correta = q_comentada.get('resposta', 'Resposta não definida')
                
                # Adicionar critérios de correção para dissertativa
                if tipo in ['dissertativa', 'DISSERTATIVA']:
                    q_comentada['criterios_correcao'] = q_comentada.get('criterios_correcao', [
                        "Avaliar clareza da resposta",
                        "Verificar uso correto de conceitos",
                        "Considerar argumentação lógica"
                    ])
                    q_comentada['pontos_chave'] = q_comentada.get('pontos_chave', [])
            
            gabarito_completo[numero_str] = resposta_correta
            
            # Adicionar explicação/resolução geral da questão
            explicacao = q_comentada.get('explicacao', q_comentada.get('resolucao', ''))
            if explicacao:
                q_comentada['explicacao_geral'] = explicacao
                comentarios[numero_str] = explicacao
            
            # Adicionar dicas de correção
            q_comentada['dicas_correcao'] = q_comentada.get('dicas_correcao', [])
            
            # Adicionar erros comuns dos alunos (se disponível)
            q_comentada['erros_comuns'] = q_comentada.get('erros_comuns', [])
            
            # Coletar fontes bibliográficas
            fontes = q_comentada.get('fontes_bibliograficas', [])
            if fontes:
                fontes_todas.extend(fontes)
            
            questoes_comentadas.append(q_comentada)
        
        # Remover fontes duplicadas
        fontes_unicas = []
        fontes_vistas = set()
        for fonte in fontes_todas:
            chave = f"{fonte.get('autor', '')}-{fonte.get('titulo', '')}"
            if chave not in fontes_vistas:
                fontes_vistas.add(chave)
                fontes_unicas.append(fonte)
        
        # Montar prova do professor
        prova_professor = {
            'titulo': f"{config.titulo} - PROVA DO PROFESSOR",
            'codigo_prova': 'PROFESSOR',
            'numero_aluno': 0,
            'e_prova_professor': True,
            'questoes': questoes_comentadas,
            'gabarito_completo': gabarito_completo,
            'comentarios': comentarios,
            'fontes_bibliograficas': fontes_unicas,
            'tempo_limite_min': config.tempo_limite_min,
            'instituicao': config.instituicao,
            'data': datetime.now().strftime("%d/%m/%Y"),
            'num_questoes': len(questoes_comentadas),
            'resumo_por_tipo': resumo_por_tipo,
            'instrucoes_professor': [
                "Esta é a PROVA MESTRE com gabarito comentado.",
                "Cada alternativa possui explicação detalhada.",
                "As alternativas corretas estão destacadas em VERDE.",
                "As alternativas incorretas incluem explicação do erro.",
                "Use este documento para correção e feedback aos alunos.",
            ]
        }
    
    def _gerar_explicacao_erro_padrao(self, alternativa: Dict, letra: str) -> str:
        """
        Gera uma explicação padrão para alternativa incorreta.
        
        Args:
            alternativa: Dados da alternativa
            letra: Letra da alternativa
        
        Returns:
            Explicação do erro
        """
        texto = alternativa.get('texto', '')
        
        # Tentar identificar tipo de erro comum
        texto_lower = texto.lower()
        
        if 'não' in texto_lower or 'nunca' in texto_lower or 'jamais' in texto_lower:
            return "Esta alternativa contém uma negação que a torna incorreta no contexto da questão."
        elif 'sempre' in texto_lower or 'todos' in texto_lower or 'qualquer' in texto_lower:
            return "Esta alternativa faz uma generalização excessiva que não se aplica a todos os casos."
        elif 'somente' in texto_lower or 'apenas' in texto_lower or 'único' in texto_lower:
            return "Esta alternativa é restritiva demais, excluindo outras possibilidades válidas."
        else:
            return f"Alternativa ({letra}) incorreta. Verifique a explicação da alternativa correta para entender o conceito."
        
        # Gerar PDF da prova do professor (se configurado)
        if config.gerar_pdf:
            try:
                caminho_pdf = self.pdf_generator.gerar_prova_professor_pdf(
                    prova_professor,
                    nome_arquivo="prova_professor",
                    output_dir=output_dir,
                    instituicao=config.instituicao
                )
                prova_professor['caminho_pdf'] = caminho_pdf
            except Exception as e:
                logger.error(f"Erro ao gerar PDF da prova do professor: {e}")
                prova_professor['erro_pdf'] = str(e)
                # Tentar gerar como prova comum com gabarito
                try:
                    caminho_pdf = self.pdf_generator.gerar_gabarito_pdf(
                        prova_professor,
                        nome_arquivo="prova_professor_gabarito",
                        output_dir=output_dir
                    )
                    prova_professor['caminho_pdf'] = caminho_pdf
                except:
                    pass
        
        # Salvar JSON da prova do professor
        json_path = os.path.join(output_dir, "prova_professor.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            # Criar versão serializável
            prova_json = {
                k: v for k, v in prova_professor.items() 
                if k not in ['questoes']  # Questões podem ser grandes
            }
            prova_json['resumo_questoes'] = [
                {
                    'numero': q['numero'],
                    'tipo': q.get('tipo_questao', 'multipla_escolha'),
                    'resposta': gabarito_completo.get(str(q['numero']), 'N/A')
                }
                for q in questoes_comentadas
            ]
            json.dump(prova_json, f, ensure_ascii=False, indent=2)
        
        return prova_professor
    
    def _preparar_prova_para_pdf(
        self,
        prova: ProvaEmbaralhada,
        config: ConfiguracaoProvaIndividual
    ) -> Dict:
        """Prepara os dados da prova para geração do PDF."""
        return {
            'titulo': config.titulo,
            'codigo_prova': prova.codigo_prova,
            'numero_aluno': prova.numero_aluno,
            'questoes': prova.questoes,
            'gabarito': prova.gabarito,
            'hash_verificacao': prova.hash_verificacao,
            'tempo_limite_min': config.tempo_limite_min,
            'instituicao': config.instituicao,
            'instrucoes': config.instrucoes,
            'data': datetime.now().strftime("%d/%m/%Y"),
            'incluir_campo_nome': config.incluir_campo_nome,
            'incluir_campo_matricula': config.incluir_campo_matricula,
            'num_questoes': len(prova.questoes),
            'pontuacao_total': len(prova.questoes)
        }
    
    def _criar_zip_lote(self, lote_dir: str, nome_lote: str) -> str:
        """Cria arquivo ZIP com todas as provas e gabaritos."""
        zip_path = os.path.join(self.output_dir, f"{nome_lote}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(lote_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, lote_dir)
                    zipf.write(file_path, arcname)
        
        logger.info(f"ZIP criado: {zip_path}")
        return zip_path
    
    def gerar_prova_rapida(
        self,
        titulo: str,
        questoes_ids: List[str],
        quantidade_alunos: int,
        instituicao: Optional[str] = None
    ) -> ResultadoLoteProvas:
        """
        Método simplificado para geração rápida de provas.
        
        Args:
            titulo: Título da prova
            questoes_ids: IDs das questões selecionadas
            quantidade_alunos: Número de alunos
            instituicao: Nome da instituição (opcional)
        
        Returns:
            Resultado do lote de provas
        """
        config = ConfiguracaoProvaIndividual(
            titulo=titulo,
            questoes_ids=questoes_ids,
            quantidade_alunos=quantidade_alunos,
            embaralhar_questoes=True,
            embaralhar_alternativas=True,
            instituicao=instituicao,
            gerar_pdf=True,
            gerar_zip=True
        )
        
        return self.gerar_provas_individuais(config)
    
    def listar_lotes(self, limite: int = 20) -> List[Dict]:
        """Lista os lotes de provas gerados."""
        lotes = []
        
        if not os.path.exists(self.output_dir):
            return lotes
        
        for item in os.listdir(self.output_dir):
            item_path = os.path.join(self.output_dir, item)
            
            if os.path.isdir(item_path):
                # É um diretório de lote
                gabarito_path = os.path.join(item_path, "gabarito_consolidado.json")
                
                if os.path.exists(gabarito_path):
                    with open(gabarito_path, 'r', encoding='utf-8') as f:
                        gabarito = json.load(f)
                    
                    lotes.append({
                        'nome': item,
                        'quantidade_provas': len(gabarito),
                        'diretorio': item_path,
                        'data_criacao': datetime.fromtimestamp(
                            os.path.getctime(item_path)
                        ).strftime("%d/%m/%Y %H:%M")
                    })
        
        # Ordenar por data (mais recente primeiro)
        lotes.sort(key=lambda x: x['data_criacao'], reverse=True)
        
        return lotes[:limite]
    
    def obter_estatisticas_lote(self, lote_nome: str) -> Dict:
        """Obtém estatísticas de um lote específico."""
        lote_dir = os.path.join(self.output_dir, lote_nome)
        
        if not os.path.exists(lote_dir):
            return {"erro": "Lote não encontrado"}
        
        gabarito_path = os.path.join(lote_dir, "gabarito_consolidado.json")
        
        if not os.path.exists(gabarito_path):
            return {"erro": "Gabarito não encontrado"}
        
        with open(gabarito_path, 'r', encoding='utf-8') as f:
            gabarito = json.load(f)
        
        # Contar arquivos
        provas_dir = os.path.join(lote_dir, "provas")
        gabaritos_dir = os.path.join(lote_dir, "gabaritos")
        
        num_provas_pdf = len(os.listdir(provas_dir)) if os.path.exists(provas_dir) else 0
        num_gabaritos_pdf = len(os.listdir(gabaritos_dir)) if os.path.exists(gabaritos_dir) else 0
        
        return {
            'nome': lote_nome,
            'quantidade_versoes': len(gabarito),
            'provas_pdf': num_provas_pdf,
            'gabaritos_pdf': num_gabaritos_pdf,
            'gabarito_consolidado': gabarito
        }


# Instância global do serviço
prova_individual_service = ProvaIndividualService()

