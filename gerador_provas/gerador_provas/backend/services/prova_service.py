"""
Serviço de Provas - Coordena criação e gerenciamento de provas completas.

Funcionalidades:
- Seleção de tópicos específicos
- Questões dissertativas ou múltipla escolha
- Geração em formato ABNT
- Prova espelho (gabarito) com respostas detalhadas
"""

import os
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from dataclasses import dataclass, field

from backend.repositories.prova_repository import ProvaRepository
from backend.repositories.questao_repository import QuestaoRepository
from backend.services.questao_service import QuestaoService
from backend.services.alternativas_generator import AlternativasGenerator
from backend.utils.prova_pdf_generator import ProvaPDFGenerator
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ConfiguracaoProva:
    """Configuração para geração de prova."""
    titulo: str
    materia: str
    topicos: List[str]
    num_questoes: int = 10
    tipo_questao: Literal["dissertativa", "multipla_escolha", "mista"] = "dissertativa"
    dificuldade: str = "medio"
    distribuicao_dificuldade: Dict[str, int] = field(default_factory=lambda: {
        "facil": 30,
        "medio": 50, 
        "dificil": 20
    })
    pontuacao_por_questao: float = 1.0
    tempo_limite_min: int = None
    com_diagramas: bool = False
    instrucoes: List[str] = None
    instituicao: str = None
    
    # Configurações para múltipla escolha
    num_alternativas: int = 5
    
    # Configurações de saída
    gerar_pdf: bool = True
    gerar_gabarito: bool = True


class ProvaService:
    """
    Serviço para criação e gerenciamento de provas.
    
    Fluxo completo:
    1. Recebe configuração com tópicos e parâmetros
    2. Gera questões dos tópicos especificados
    3. Converte para múltipla escolha se necessário
    4. Gera PDF da prova e gabarito
    5. Salva no banco de dados
    """
    
    # Mapeamento de tópicos por matéria
    TOPICOS_DISPONIVEIS = {
        "matematica": {
            "algebra": ["equacao_1_grau", "equacao_2_grau", "sistemas_lineares", "polinomios"],
            "funcoes": ["funcao_1_grau", "funcao_2_grau", "funcao_exponencial", "logaritmo"],
            "geometria": ["geometria_plana", "geometria_espacial", "trigonometria"],
            "estatistica": ["probabilidade", "combinatoria", "media_moda_mediana"],
        },
        "fisica": {
            "mecanica": ["mru", "mruv", "queda_livre", "lancamento"],
            "dinamica": ["forca", "leis_newton", "atrito", "trabalho_energia"],
            "ondulatoria": ["ondas", "som", "luz"],
            "eletricidade": ["circuito", "corrente", "resistencia", "lei_ohm"],
            "termodinamica": ["calor", "temperatura", "dilatacao"],
        },
        "quimica": {
            "geral": ["tabela_periodica", "modelo_atomico", "ligacoes_quimicas"],
            "organica": ["hidrocarbonetos", "funcoes_organicas", "isomeria"],
            "inorganica": ["acidos", "bases", "sais", "oxidos"],
            "fisico_quimica": ["estequiometria", "solucoes", "equilibrio_quimico"],
        },
        "biologia": {
            "farmaceutica": ["farmacologia", "medicamentos", "farmacos", "interacoes"],
            "medicina": ["anatomia", "fisiologia", "patologia", "sistemas"],
            "celular": ["celula", "organelas", "metabolismo", "citologia"],
            "genetica": ["dna", "hereditariedade", "cromossomos", "biotecnologia"],
            "microbiologia": ["bacterias", "virus", "fungos", "imunologia"],
            "ecologia": ["ecossistema", "cadeia_alimentar", "meio_ambiente", "sucessao"],
        }
    }
    
    def __init__(self):
        self.prova_repository = ProvaRepository()
        self.questao_repository = QuestaoRepository()
        self.questao_service = QuestaoService(persistir=True)
        self.alternativas_generator = AlternativasGenerator()
        self.pdf_generator = ProvaPDFGenerator()
    
    def criar_prova(self, config: ConfiguracaoProva) -> Dict[str, Any]:
        """
        Cria uma prova completa baseada na configuração.
        
        Args:
            config: Configuração da prova
        
        Returns:
            Dicionário com prova, questões e caminhos dos PDFs
        """
        logger.info(f"Criando prova: {config.titulo}")
        logger.info(f"Tópicos: {config.topicos}")
        logger.info(f"Tipo de questão: {config.tipo_questao}")
        
        # 1. Validar tópicos
        topicos_validos = self._validar_topicos(config.materia, config.topicos)
        if not topicos_validos:
            raise ValueError(f"Nenhum tópico válido encontrado para {config.materia}")
        
        # 2. Calcular distribuição de questões por tópico
        questoes_por_topico = self._calcular_distribuicao(
            config.num_questoes, 
            topicos_validos,
            config.distribuicao_dificuldade
        )
        
        # 3. Gerar questões
        questoes = []
        numero = 1
        
        for topico, quantidade in questoes_por_topico.items():
            for _ in range(quantidade):
                try:
                    # Definir dificuldade desta questão
                    dificuldade = self._sortear_dificuldade(config.distribuicao_dificuldade)
                    
                    # Gerar questão
                    questao = self.questao_service.gerar_questao(
                        materia=config.materia,
                        topico=topico,
                        dificuldade=dificuldade,
                        com_diagrama=config.com_diagramas,
                        salvar=True
                    )
                    
                    # Adicionar metadados
                    questao["numero"] = numero
                    questao["pontuacao"] = config.pontuacao_por_questao
                    questao["topico"] = topico
                    
                    # Converter para múltipla escolha se necessário
                    if config.tipo_questao in ["multipla_escolha", "mista"]:
                        if config.tipo_questao == "multipla_escolha" or numero % 2 == 0:
                            questao = self._converter_para_multipla_escolha(
                                questao, 
                                config.num_alternativas
                            )
                    
                    questoes.append(questao)
                    numero += 1
                    
                except Exception as e:
                    logger.error(f"Erro ao gerar questão do tópico {topico}: {e}")
        
        # 4. Montar objeto da prova
        prova = {
            "titulo": config.titulo,
            "materia": config.materia,
            "topicos": config.topicos,
            "num_questoes": len(questoes),
            "tipo_questao": config.tipo_questao,
            "dificuldade": config.dificuldade,
            "tempo_limite_min": config.tempo_limite_min,
            "pontuacao_total": sum(q.get("pontuacao", 1.0) for q in questoes),
            "questoes": questoes,
            "data": datetime.now().strftime("%d/%m/%Y"),
            "criada_em": datetime.now().isoformat()
        }
        
        # 5. Gerar PDFs
        pdfs = {}
        if config.gerar_pdf:
            try:
                nome_base = f"{config.titulo.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                if config.gerar_gabarito:
                    pdfs = self.pdf_generator.gerar_prova_completa(
                        prova,
                        nome_base=nome_base,
                        instituicao=config.instituicao,
                        instrucoes=config.instrucoes
                    )
                else:
                    pdfs["prova"] = self.pdf_generator.gerar_prova_pdf(
                        prova,
                        nome_arquivo=nome_base,
                        instituicao=config.instituicao,
                        instrucoes=config.instrucoes
                    )
                
                prova["pdfs"] = pdfs
                logger.info(f"PDFs gerados: {pdfs}")
                
            except Exception as e:
                logger.error(f"Erro ao gerar PDFs: {e}")
                prova["erro_pdf"] = str(e)
        
        # 6. Salvar no banco
        try:
            prova_id = self._salvar_prova(prova, config)
            prova["id"] = prova_id
        except Exception as e:
            logger.error(f"Erro ao salvar prova: {e}")
        
        return prova
    
    def _validar_topicos(self, materia: str, topicos: List[str]) -> List[str]:
        """Valida e retorna apenas tópicos válidos para a matéria."""
        if materia not in self.TOPICOS_DISPONIVEIS:
            return topicos  # Retorna como está se matéria não mapeada
        
        topicos_materia = self.TOPICOS_DISPONIVEIS[materia]
        
        # Flatten dos tópicos disponíveis
        todos_topicos = []
        for categoria, lista in topicos_materia.items():
            todos_topicos.extend(lista)
            todos_topicos.append(categoria)
        
        # Validar
        validos = []
        for topico in topicos:
            topico_lower = topico.lower().replace(" ", "_")
            if topico_lower in todos_topicos:
                validos.append(topico_lower)
            else:
                # Tentar match parcial
                for t in todos_topicos:
                    if topico_lower in t or t in topico_lower:
                        validos.append(t)
                        break
        
        return list(set(validos)) if validos else topicos
    
    def _calcular_distribuicao(
        self, 
        num_questoes: int, 
        topicos: List[str],
        distribuicao_dificuldade: Dict[str, int]
    ) -> Dict[str, int]:
        """Calcula quantas questões de cada tópico gerar."""
        num_topicos = len(topicos)
        base = num_questoes // num_topicos
        resto = num_questoes % num_topicos
        
        distribuicao = {}
        for i, topico in enumerate(topicos):
            distribuicao[topico] = base + (1 if i < resto else 0)
        
        return distribuicao
    
    def _sortear_dificuldade(self, distribuicao: Dict[str, int]) -> str:
        """Sorteia uma dificuldade baseada na distribuição."""
        import random
        
        total = sum(distribuicao.values())
        r = random.randint(1, total)
        
        acumulado = 0
        for dificuldade, peso in distribuicao.items():
            acumulado += peso
            if r <= acumulado:
                return dificuldade
        
        return "medio"
    
    def _converter_para_multipla_escolha(
        self, 
        questao: Dict, 
        num_alternativas: int = 5
    ) -> Dict:
        """Converte uma questão dissertativa para múltipla escolha."""
        resposta = questao.get("resposta", "")
        
        # Identificar tipo de resposta
        tipo = self.alternativas_generator.identificar_tipo_resposta(resposta, questao)
        
        # Gerar alternativas
        alternativas = self.alternativas_generator.gerar_alternativas(
            resposta_correta=resposta,
            tipo_questao=tipo,
            contexto={"dados": questao.get("dados", {})}
        )
        
        questao["alternativas"] = alternativas
        questao["tipo_questao"] = "multipla_escolha"
        
        return questao
    
    def _salvar_prova(self, prova: Dict, config: ConfiguracaoProva) -> str:
        """Salva a prova no banco de dados."""
        # Obter materia_id
        codigo_materia = QuestaoService.MATERIA_CODIGOS.get(
            config.materia, 
            config.materia.upper()[:3]
        )
        materia_id = self.questao_repository.obter_materia_id_por_codigo(codigo_materia)
        
        # Criar prova
        prova_id = self.prova_repository.criar_prova(
            titulo=config.titulo,
            materia_id=materia_id,
            descricao=f"Prova de {config.materia} - Tópicos: {', '.join(config.topicos)}",
            tempo_limite_min=config.tempo_limite_min,
            instrucoes="\n".join(config.instrucoes) if config.instrucoes else None
        )
        
        # Adicionar questões à prova
        for questao in prova["questoes"]:
            if questao.get("id"):
                self.prova_repository.adicionar_questao_prova(
                    prova_id=prova_id,
                    questao_id=questao["id"],
                    numero=questao.get("numero", 0),
                    pontuacao=questao.get("pontuacao", 1.0)
                )
        
        return prova_id
    
    def criar_prova_rapida(
        self,
        titulo: str,
        materia: str,
        topicos: List[str],
        num_questoes: int = 10,
        tipo: str = "dissertativa",
        dificuldade: str = "medio"
    ) -> Dict:
        """
        Método simplificado para criar prova rapidamente.
        
        Args:
            titulo: Título da prova
            materia: Matéria (fisica, quimica, matematica)
            topicos: Lista de tópicos
            num_questoes: Número de questões
            tipo: "dissertativa" ou "multipla_escolha"
            dificuldade: "facil", "medio" ou "dificil"
        
        Returns:
            Prova gerada com PDFs
        """
        config = ConfiguracaoProva(
            titulo=titulo,
            materia=materia,
            topicos=topicos,
            num_questoes=num_questoes,
            tipo_questao=tipo,
            dificuldade=dificuldade,
            gerar_pdf=True,
            gerar_gabarito=True
        )
        
        return self.criar_prova(config)
    
    def listar_topicos_disponiveis(self, materia: str = None) -> Dict:
        """
        Lista todos os tópicos disponíveis.
        
        Args:
            materia: Se especificada, retorna apenas tópicos da matéria
        
        Returns:
            Dicionário com tópicos organizados
        """
        if materia:
            return self.TOPICOS_DISPONIVEIS.get(materia, {})
        return self.TOPICOS_DISPONIVEIS
    
    def buscar_prova(self, prova_id: str) -> Optional[Dict]:
        """Busca uma prova pelo ID."""
        return self.prova_repository.buscar_prova_por_id(prova_id)
    
    def listar_provas(
        self,
        status: str = None,
        materia: str = None,
        limite: int = 50
    ) -> List[Dict]:
        """Lista provas com filtros."""
        materia_id = None
        if materia:
            codigo = QuestaoService.MATERIA_CODIGOS.get(materia, materia.upper()[:3])
            materia_id = self.questao_repository.obter_materia_id_por_codigo(codigo)
        
        return self.prova_repository.listar_provas(
            status=status,
            materia_id=materia_id,
            limite=limite
        )
    
    def regenerar_pdf(self, prova_id: str, instituicao: str = None) -> Dict[str, str]:
        """Regenera os PDFs de uma prova existente."""
        prova = self.buscar_prova(prova_id)
        if not prova:
            raise ValueError(f"Prova {prova_id} não encontrada")
        
        return self.pdf_generator.gerar_prova_completa(
            prova,
            instituicao=instituicao
        )


# Função utilitária para uso direto
def criar_prova(
    titulo: str,
    materia: str,
    topicos: List[str],
    num_questoes: int = 10,
    tipo: str = "dissertativa",
    dificuldade: str = "medio",
    instituicao: str = None
) -> Dict:
    """
    Função utilitária para criar prova rapidamente.
    
    Exemplo de uso:
    ```python
    prova = criar_prova(
        titulo="Prova de Álgebra",
        materia="matematica",
        topicos=["equacao_1_grau", "logaritmo"],
        num_questoes=10,
        tipo="multipla_escolha"
    )
    print(prova["pdfs"]["prova"])  # Caminho do PDF
    print(prova["pdfs"]["gabarito"])  # Caminho do gabarito
    ```
    """
    service = ProvaService()
    
    config = ConfiguracaoProva(
        titulo=titulo,
        materia=materia,
        topicos=topicos,
        num_questoes=num_questoes,
        tipo_questao=tipo,
        dificuldade=dificuldade,
        instituicao=instituicao,
        gerar_pdf=True,
        gerar_gabarito=True
    )
    
    return service.criar_prova(config)
