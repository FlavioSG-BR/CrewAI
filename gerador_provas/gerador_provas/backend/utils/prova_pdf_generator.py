"""
Gerador de PDFs de Provas em formato ABNT.

Gera:
1. Prova para o aluno (sem respostas)
2. Prova espelho/gabarito (com respostas detalhadas)
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Optional, Any

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from pylatex import Document, Section, Subsection, Command, Package
from pylatex import NoEscape, MiniPage, LineBreak, NewLine, NewPage
from pylatex import Tabular, MultiColumn, LongTable
from pylatex.utils import bold, italic

try:
    from config import settings
    PDF_OUTPUT_DIR = settings.PDF_OUTPUT_DIR
except ImportError:
    PDF_OUTPUT_DIR = os.getenv('PDF_OUTPUT_DIR', 'output/pdf')

os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)


class ProvaPDFGenerator:
    """
    Gerador de provas em PDF formatadas segundo ABNT.
    
    Características ABNT:
    - Fonte Times New Roman 12pt
    - Margens: superior e esquerda 3cm, inferior e direita 2cm
    - Espaçamento 1,5
    - Títulos em negrito
    """
    
    def __init__(self):
        self.output_dir = PDF_OUTPUT_DIR
    
    def _criar_documento_abnt(self) -> Document:
        """Cria um documento LaTeX com formatação ABNT."""
        geometry_options = {
            "top": "3cm",
            "bottom": "2cm", 
            "left": "3cm",
            "right": "2cm"
        }
        
        doc = Document(
            geometry_options=geometry_options,
            document_options=['12pt', 'a4paper', 'oneside']
        )
        
        # Pacotes necessários
        doc.packages.append(Package('babel', options=['brazil']))
        doc.packages.append(Package('inputenc', options=['utf8']))
        doc.packages.append(Package('fontenc', options=['T1']))
        doc.packages.append(Package('times'))  # Fonte Times
        doc.packages.append(Package('setspace'))  # Espaçamento
        doc.packages.append(Package('amsmath'))
        doc.packages.append(Package('amssymb'))
        doc.packages.append(Package('graphicx'))
        doc.packages.append(Package('enumerate'))
        doc.packages.append(Package('enumitem'))
        doc.packages.append(Package('fancyhdr'))  # Cabeçalho/rodapé
        doc.packages.append(Package('lastpage'))  # Total de páginas
        doc.packages.append(Package('array'))
        doc.packages.append(Package('tabularx'))
        
        # Configuração de espaçamento 1,5
        doc.preamble.append(NoEscape(r'\onehalfspacing'))
        
        # Configuração de cabeçalho e rodapé
        doc.preamble.append(NoEscape(r'\pagestyle{fancy}'))
        doc.preamble.append(NoEscape(r'\fancyhf{}'))
        doc.preamble.append(NoEscape(r'\renewcommand{\headrulewidth}{0.5pt}'))
        doc.preamble.append(NoEscape(r'\renewcommand{\footrulewidth}{0.5pt}'))
        
        return doc
    
    def _adicionar_cabecalho(
        self, 
        doc: Document, 
        prova: Dict,
        instituicao: str = None,
        is_gabarito: bool = False
    ):
        """Adiciona cabeçalho da prova."""
        titulo = prova.get('titulo', 'Prova')
        if is_gabarito:
            titulo = f"{titulo} - GABARITO"
        
        # Cabeçalho superior
        doc.preamble.append(NoEscape(
            r'\fancyhead[L]{\small ' + (instituicao or 'Instituição de Ensino') + r'}'
        ))
        doc.preamble.append(NoEscape(
            r'\fancyhead[R]{\small Página \thepage\ de \pageref{LastPage}}'
        ))
        doc.preamble.append(NoEscape(
            r'\fancyfoot[C]{\small ' + titulo + r'}'
        ))
        
        # Título centralizado
        doc.append(NoEscape(r'\begin{center}'))
        doc.append(NoEscape(r'\Large\textbf{' + (instituicao or 'INSTITUIÇÃO DE ENSINO') + r'}'))
        doc.append(NoEscape(r'\\[0.3cm]'))
        doc.append(NoEscape(r'\large\textbf{' + titulo + r'}'))
        doc.append(NoEscape(r'\\[0.2cm]'))
        
        # Data e informações
        materia = prova.get('materia', '')
        if materia:
            doc.append(NoEscape(r'\normalsize Disciplina: ' + materia.capitalize()))
            doc.append(NoEscape(r'\\'))
        
        data = prova.get('data', datetime.now().strftime('%d/%m/%Y'))
        doc.append(NoEscape(r'\normalsize Data: ' + data))
        doc.append(NoEscape(r'\\'))
        
        tempo = prova.get('tempo_limite_min')
        if tempo:
            doc.append(NoEscape(r'\normalsize Duração: ' + str(tempo) + r' minutos'))
            doc.append(NoEscape(r'\\'))
        
        doc.append(NoEscape(r'\end{center}'))
        doc.append(NoEscape(r'\vspace{0.3cm}'))
        
        # Campos para preenchimento (apenas na prova, não no gabarito)
        if not is_gabarito:
            doc.append(NoEscape(r'\noindent\textbf{Nome:} \underline{\hspace{10cm}}'))
            doc.append(NoEscape(r'\\[0.3cm]'))
            doc.append(NoEscape(r'\noindent\textbf{Turma:} \underline{\hspace{3cm}} '
                               r'\hspace{2cm} \textbf{Nº:} \underline{\hspace{2cm}}'))
            doc.append(NoEscape(r'\\[0.5cm]'))
        
        doc.append(NoEscape(r'\hrule'))
        doc.append(NoEscape(r'\vspace{0.5cm}'))
    
    def _adicionar_instrucoes(self, doc: Document, instrucoes: List[str] = None):
        """Adiciona instruções da prova."""
        if not instrucoes:
            instrucoes = [
                "Leia atentamente cada questão antes de responder.",
                "Use caneta azul ou preta para as respostas.",
                "Não é permitido o uso de calculadora, salvo indicação contrária.",
                "As respostas devem ser justificadas quando solicitado.",
                "Boa prova!"
            ]
        
        doc.append(NoEscape(r'\noindent\textbf{INSTRUÇÕES:}'))
        doc.append(NoEscape(r'\begin{itemize}[leftmargin=1cm]'))
        for instrucao in instrucoes:
            doc.append(NoEscape(r'\item ' + instrucao))
        doc.append(NoEscape(r'\end{itemize}'))
        doc.append(NoEscape(r'\vspace{0.5cm}'))
        doc.append(NoEscape(r'\hrule'))
        doc.append(NoEscape(r'\vspace{0.5cm}'))
    
    def _adicionar_questao_dissertativa(
        self, 
        doc: Document, 
        numero: int, 
        questao: Dict,
        mostrar_resposta: bool = False
    ):
        """Adiciona uma questão dissertativa."""
        enunciado = questao.get('enunciado', '')
        pontuacao = questao.get('pontuacao', 1.0)
        topico = questao.get('topico', '')
        
        # Cabeçalho da questão
        doc.append(NoEscape(
            r'\noindent\textbf{Questão ' + str(numero) + 
            r'} (' + str(pontuacao) + r' ponto' + ('s' if pontuacao != 1 else '') + r')'
        ))
        
        if topico:
            doc.append(NoEscape(r' \textit{[' + topico + r']}'))
        
        doc.append(NoEscape(r'\\[0.2cm]'))
        
        # Enunciado
        doc.append(NoEscape(r'\noindent ' + self._escapar_latex(enunciado)))
        doc.append(NoEscape(r'\\[0.3cm]'))
        
        # Diagrama se existir
        diagrama = questao.get('diagrama')
        if diagrama and os.path.exists(diagrama.replace('/static/', 'static/')):
            doc.append(NoEscape(r'\begin{center}'))
            doc.append(NoEscape(r'\includegraphics[width=0.5\textwidth]{' + 
                               diagrama.replace('/static/', 'static/') + r'}'))
            doc.append(NoEscape(r'\end{center}'))
        
        if mostrar_resposta:
            # Mostrar resposta detalhada
            resposta = questao.get('resposta', '')
            explicacao = questao.get('explicacao', '')
            
            doc.append(NoEscape(r'\vspace{0.3cm}'))
            doc.append(NoEscape(r'\noindent\fbox{\parbox{\textwidth}{'))
            doc.append(NoEscape(r'\textbf{Resposta:} ' + self._escapar_latex(resposta)))
            
            if explicacao:
                doc.append(NoEscape(r'\\[0.2cm]'))
                doc.append(NoEscape(r'\textbf{Explicação:} ' + self._escapar_latex(explicacao)))
            
            doc.append(NoEscape(r'}}'))
        else:
            # Espaço para resposta
            linhas = questao.get('linhas_resposta', 5)
            doc.append(NoEscape(r'\vspace{0.3cm}'))
            doc.append(NoEscape(r'\noindent\textbf{Resposta:}'))
            doc.append(NoEscape(r'\\[0.2cm]'))
            for _ in range(linhas):
                doc.append(NoEscape(r'\noindent\underline{\hspace{\textwidth}}'))
                doc.append(NoEscape(r'\\[0.3cm]'))
        
        doc.append(NoEscape(r'\vspace{0.5cm}'))
        doc.append(NoEscape(r'\hrule'))
        doc.append(NoEscape(r'\vspace{0.5cm}'))
    
    def _adicionar_questao_multipla_escolha(
        self, 
        doc: Document, 
        numero: int, 
        questao: Dict,
        mostrar_resposta: bool = False
    ):
        """Adiciona uma questão de múltipla escolha."""
        enunciado = questao.get('enunciado', '')
        alternativas = questao.get('alternativas', [])
        pontuacao = questao.get('pontuacao', 1.0)
        topico = questao.get('topico', '')
        
        # Cabeçalho da questão
        doc.append(NoEscape(
            r'\noindent\textbf{Questão ' + str(numero) + 
            r'} (' + str(pontuacao) + r' ponto' + ('s' if pontuacao != 1 else '') + r')'
        ))
        
        if topico:
            doc.append(NoEscape(r' \textit{[' + topico + r']}'))
        
        doc.append(NoEscape(r'\\[0.2cm]'))
        
        # Enunciado
        doc.append(NoEscape(r'\noindent ' + self._escapar_latex(enunciado)))
        doc.append(NoEscape(r'\\[0.3cm]'))
        
        # Diagrama se existir
        diagrama = questao.get('diagrama')
        if diagrama and os.path.exists(diagrama.replace('/static/', 'static/')):
            doc.append(NoEscape(r'\begin{center}'))
            doc.append(NoEscape(r'\includegraphics[width=0.5\textwidth]{' + 
                               diagrama.replace('/static/', 'static/') + r'}'))
            doc.append(NoEscape(r'\end{center}'))
        
        # Alternativas
        doc.append(NoEscape(r'\begin{enumerate}[(A)]'))
        for alt in alternativas:
            letra = alt.get('letra', '')
            texto = alt.get('texto', '')
            correta = alt.get('correta', False)
            
            if mostrar_resposta and correta:
                doc.append(NoEscape(r'\item \textbf{' + self._escapar_latex(texto) + 
                                   r'} $\leftarrow$ \textit{Resposta correta}'))
            else:
                doc.append(NoEscape(r'\item ' + self._escapar_latex(texto)))
        doc.append(NoEscape(r'\end{enumerate}'))
        
        if mostrar_resposta:
            explicacao = questao.get('explicacao', '')
            if explicacao:
                doc.append(NoEscape(r'\vspace{0.2cm}'))
                doc.append(NoEscape(r'\noindent\fbox{\parbox{\textwidth}{'))
                doc.append(NoEscape(r'\textbf{Explicação:} ' + self._escapar_latex(explicacao)))
                doc.append(NoEscape(r'}}'))
        
        doc.append(NoEscape(r'\vspace{0.5cm}'))
        doc.append(NoEscape(r'\hrule'))
        doc.append(NoEscape(r'\vspace{0.5cm}'))
    
    def _adicionar_tabela_gabarito(self, doc: Document, questoes: List[Dict]):
        """Adiciona tabela resumo do gabarito."""
        doc.append(NoEscape(r'\section*{Gabarito Resumido}'))
        doc.append(NoEscape(r'\begin{center}'))
        
        # Calcular número de colunas
        num_questoes = len(questoes)
        colunas_por_linha = min(10, num_questoes)
        
        doc.append(NoEscape(r'\begin{tabular}{|' + 'c|' * (colunas_por_linha + 1) + r'}'))
        doc.append(NoEscape(r'\hline'))
        
        # Cabeçalho
        cabecalho = r'\textbf{Questão}'
        for i in range(1, colunas_por_linha + 1):
            cabecalho += r' & \textbf{' + str(i) + r'}'
        cabecalho += r' \\ \hline'
        doc.append(NoEscape(cabecalho))
        
        # Respostas
        linha = r'\textbf{Resposta}'
        for i, q in enumerate(questoes[:colunas_por_linha]):
            if q.get('alternativas'):
                # Questão de múltipla escolha
                for alt in q['alternativas']:
                    if alt.get('correta'):
                        linha += r' & ' + alt['letra']
                        break
            else:
                # Questão dissertativa
                resp = q.get('resposta', '-')[:10]
                linha += r' & ' + self._escapar_latex(resp)
        linha += r' \\ \hline'
        doc.append(NoEscape(linha))
        
        doc.append(NoEscape(r'\end{tabular}'))
        doc.append(NoEscape(r'\end{center}'))
        doc.append(NoEscape(r'\vspace{1cm}'))
    
    def _escapar_latex(self, texto: str) -> str:
        """Escapa caracteres especiais do LaTeX."""
        if not texto:
            return ""
        
        # Mapeamento de caracteres especiais
        mapa = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
        }
        
        for char, escape in mapa.items():
            texto = texto.replace(char, escape)
        
        return texto
    
    def gerar_prova_pdf(
        self,
        prova: Dict,
        nome_arquivo: str = None,
        instituicao: str = None,
        instrucoes: List[str] = None
    ) -> str:
        """
        Gera o PDF da prova (versão do aluno, sem respostas).
        
        Args:
            prova: Dicionário com dados da prova e questões
            nome_arquivo: Nome do arquivo (sem extensão)
            instituicao: Nome da instituição
            instrucoes: Lista de instruções
        
        Returns:
            Caminho do PDF gerado
        """
        doc = self._criar_documento_abnt()
        
        self._adicionar_cabecalho(doc, prova, instituicao, is_gabarito=False)
        self._adicionar_instrucoes(doc, instrucoes)
        
        questoes = prova.get('questoes', [])
        
        for i, questao in enumerate(questoes, 1):
            if questao.get('alternativas'):
                self._adicionar_questao_multipla_escolha(doc, i, questao, mostrar_resposta=False)
            else:
                self._adicionar_questao_dissertativa(doc, i, questao, mostrar_resposta=False)
        
        # Salvar
        if not nome_arquivo:
            nome_arquivo = f"prova_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        caminho = os.path.join(self.output_dir, nome_arquivo)
        
        try:
            doc.generate_pdf(caminho, clean_tex=False, compiler='pdflatex')
            return caminho + '.pdf'
        except Exception as e:
            # Se não conseguir gerar PDF, salva o .tex
            doc.generate_tex(caminho)
            return caminho + '.tex'
    
    def gerar_gabarito_pdf(
        self,
        prova: Dict,
        nome_arquivo: str = None,
        instituicao: str = None,
        incluir_explicacoes: bool = True
    ) -> str:
        """
        Gera o PDF do gabarito (prova espelho com respostas).
        
        Args:
            prova: Dicionário com dados da prova e questões
            nome_arquivo: Nome do arquivo (sem extensão)
            instituicao: Nome da instituição
            incluir_explicacoes: Se True, inclui explicações detalhadas
        
        Returns:
            Caminho do PDF gerado
        """
        doc = self._criar_documento_abnt()
        
        self._adicionar_cabecalho(doc, prova, instituicao, is_gabarito=True)
        
        questoes = prova.get('questoes', [])
        
        # Tabela resumo do gabarito
        self._adicionar_tabela_gabarito(doc, questoes)
        
        doc.append(NoEscape(r'\section*{Respostas Detalhadas}'))
        
        for i, questao in enumerate(questoes, 1):
            if questao.get('alternativas'):
                self._adicionar_questao_multipla_escolha(doc, i, questao, mostrar_resposta=True)
            else:
                self._adicionar_questao_dissertativa(doc, i, questao, mostrar_resposta=True)
        
        # Salvar
        if not nome_arquivo:
            nome_arquivo = f"gabarito_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        caminho = os.path.join(self.output_dir, nome_arquivo)
        
        try:
            doc.generate_pdf(caminho, clean_tex=False, compiler='pdflatex')
            return caminho + '.pdf'
        except Exception as e:
            doc.generate_tex(caminho)
            return caminho + '.tex'
    
    def gerar_prova_completa(
        self,
        prova: Dict,
        nome_base: str = None,
        instituicao: str = None,
        instrucoes: List[str] = None
    ) -> Dict[str, str]:
        """
        Gera tanto a prova quanto o gabarito.
        
        Returns:
            Dicionário com caminhos: {'prova': '...', 'gabarito': '...'}
        """
        if not nome_base:
            nome_base = f"prova_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        prova_pdf = self.gerar_prova_pdf(
            prova,
            nome_arquivo=nome_base,
            instituicao=instituicao,
            instrucoes=instrucoes
        )
        
        gabarito_pdf = self.gerar_gabarito_pdf(
            prova,
            nome_arquivo=f"{nome_base}_gabarito",
            instituicao=instituicao
        )
        
        return {
            'prova': prova_pdf,
            'gabarito': gabarito_pdf
        }

