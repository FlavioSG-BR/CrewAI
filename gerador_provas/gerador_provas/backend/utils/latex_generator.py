"""
Gerador de PDFs e documentos LaTeX para provas.

Usa PyLaTeX para criar documentos formatados.
"""

import os
import sys
from typing import List, Dict, Optional

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from pylatex import Document, Section, Subsection, Itemize, Enumerate
from pylatex import Command, NoEscape, Package
from pylatex.utils import bold, italic

# Tentar importar configurações
try:
    from config import settings
    PDF_OUTPUT_DIR = settings.PDF_OUTPUT_DIR
    LATEX_OUTPUT_DIR = settings.LATEX_OUTPUT_DIR
except ImportError:
    PDF_OUTPUT_DIR = os.getenv('PDF_OUTPUT_DIR', 'output/pdf')
    LATEX_OUTPUT_DIR = os.getenv('LATEX_OUTPUT_DIR', 'output/latex')

# Criar diretórios se não existirem
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)
os.makedirs(LATEX_OUTPUT_DIR, exist_ok=True)


def gerar_pdf(
    questoes: List[Dict],
    caminho_saida: str = None,
    titulo: str = "Prova",
    instituicao: str = None,
    instrucoes: str = None,
    mostrar_respostas: bool = False
) -> str:
    """
    Gera um PDF com as questões.
    
    Args:
        questoes: Lista de dicionários com questões
        caminho_saida: Caminho para salvar o PDF
        titulo: Título da prova
        instituicao: Nome da instituição
        instrucoes: Instruções para os alunos
        mostrar_respostas: Se True, inclui gabarito
    
    Returns:
        Caminho do PDF gerado
    """
    if caminho_saida is None:
        caminho_saida = os.path.join(PDF_OUTPUT_DIR, "prova")
    
    # Remover extensão se existir
    if caminho_saida.endswith('.pdf'):
        caminho_saida = caminho_saida[:-4]
    
    # Criar documento
    geometry_options = {
        "margin": "2.5cm",
        "top": "2cm",
        "bottom": "2cm"
    }
    
    doc = Document(
        geometry_options=geometry_options,
        document_options=['12pt', 'a4paper']
    )
    
    # Pacotes adicionais
    doc.packages.append(Package('babel', options=['brazil']))
    doc.packages.append(Package('inputenc', options=['utf8']))
    doc.packages.append(Package('amsmath'))
    doc.packages.append(Package('amssymb'))
    
    # Cabeçalho
    if instituicao:
        doc.preamble.append(Command('title', instituicao))
    
    doc.append(NoEscape(r'\begin{center}'))
    doc.append(NoEscape(r'\Large\textbf{' + titulo + r'}'))
    doc.append(NoEscape(r'\end{center}'))
    doc.append(NoEscape(r'\vspace{0.5cm}'))
    
    # Campos para identificação
    doc.append(NoEscape(r'\noindent\textbf{Nome:} \underline{\hspace{10cm}}'))
    doc.append(NoEscape(r'\vspace{0.3cm}'))
    doc.append(NoEscape(r'\noindent\textbf{Data:} \underline{\hspace{3cm}} \hspace{2cm} \textbf{Turma:} \underline{\hspace{3cm}}'))
    doc.append(NoEscape(r'\vspace{0.5cm}'))
    
    # Instruções
    if instrucoes:
        doc.append(NoEscape(r'\noindent\textbf{Instruções:}'))
        doc.append(NoEscape(r'\begin{itemize}'))
        for instrucao in instrucoes.split('\n'):
            if instrucao.strip():
                doc.append(NoEscape(r'\item ' + instrucao.strip()))
        doc.append(NoEscape(r'\end{itemize}'))
        doc.append(NoEscape(r'\vspace{0.5cm}'))
    
    doc.append(NoEscape(r'\hrule'))
    doc.append(NoEscape(r'\vspace{0.5cm}'))
    
    # Questões
    with doc.create(Section('Questões', numbering=False)):
        for i, questao in enumerate(questoes, 1):
            enunciado = questao.get('enunciado', 'Questão sem enunciado')
            tipo = questao.get('tipo', '')
            pontuacao = questao.get('pontuacao', 1.0)
            
            # Número e tipo da questão
            doc.append(NoEscape(
                r'\noindent\textbf{Questão ' + str(i) + 
                r'} (' + str(pontuacao) + ' ponto' + ('s' if pontuacao != 1 else '') + r')'
            ))
            if tipo:
                doc.append(NoEscape(r' \textit{[' + tipo + r']}'))
            doc.append(NoEscape(r'\vspace{0.2cm}'))
            
            # Enunciado
            doc.append(NoEscape(r'\noindent ' + enunciado))
            doc.append(NoEscape(r'\vspace{0.3cm}'))
            
            # Alternativas (se existirem)
            alternativas = questao.get('alternativas', [])
            if alternativas:
                doc.append(NoEscape(r'\begin{enumerate}[(a)]'))
                for alt in alternativas:
                    doc.append(NoEscape(r'\item ' + alt.get('texto', '')))
                doc.append(NoEscape(r'\end{enumerate}'))
            
            # Espaço para resposta
            doc.append(NoEscape(r'\vspace{1cm}'))
            doc.append(NoEscape(r'\hrule'))
            doc.append(NoEscape(r'\vspace{0.5cm}'))
    
    # Gabarito (opcional)
    if mostrar_respostas:
        doc.append(NoEscape(r'\newpage'))
        with doc.create(Section('Gabarito', numbering=False)):
            for i, questao in enumerate(questoes, 1):
                resposta = questao.get('resposta', 'Não disponível')
                doc.append(NoEscape(
                    r'\noindent\textbf{' + str(i) + r'.} ' + str(resposta)
                ))
                doc.append(NoEscape(r'\vspace{0.3cm}'))
    
    # Gerar PDF
    try:
        doc.generate_pdf(caminho_saida, clean_tex=False, compiler='pdflatex')
        return caminho_saida + '.pdf'
    except Exception as e:
        # Se não conseguir gerar PDF, salva o .tex
        doc.generate_tex(caminho_saida)
        return caminho_saida + '.tex'


def gerar_latex(
    questoes: List[Dict],
    caminho_saida: str = None,
    titulo: str = "Prova"
) -> str:
    """
    Gera apenas o arquivo LaTeX (sem compilar para PDF).
    
    Args:
        questoes: Lista de questões
        caminho_saida: Caminho para salvar o .tex
        titulo: Título da prova
    
    Returns:
        Caminho do arquivo .tex gerado
    """
    if caminho_saida is None:
        caminho_saida = os.path.join(LATEX_OUTPUT_DIR, "prova.tex")
    
    if not caminho_saida.endswith('.tex'):
        caminho_saida += '.tex'
    
    doc = Document()
    
    doc.packages.append(Package('babel', options=['brazil']))
    
    with doc.create(Section(titulo)):
        with doc.create(Enumerate()) as enum:
            for questao in questoes:
                enunciado = questao.get('enunciado', '')
                enum.add_item(enunciado)
    
    doc.generate_tex(caminho_saida.replace('.tex', ''))
    return caminho_saida


def exportar_questao_latex(questao: Dict) -> str:
    """
    Exporta uma questão individual para formato LaTeX.
    
    Args:
        questao: Dicionário com a questão
    
    Returns:
        String com o código LaTeX
    """
    latex = []
    
    enunciado = questao.get('enunciado', '')
    resposta = questao.get('resposta', '')
    tipo = questao.get('tipo', '')
    
    latex.append(r'\begin{question}')
    if tipo:
        latex.append(r'\textit{[' + tipo + r']}')
    latex.append(r'\par')
    latex.append(enunciado)
    
    # Alternativas
    alternativas = questao.get('alternativas', [])
    if alternativas:
        latex.append(r'\begin{enumerate}[(a)]')
        for alt in alternativas:
            latex.append(r'\item ' + alt.get('texto', ''))
        latex.append(r'\end{enumerate}')
    
    latex.append(r'\end{question}')
    
    # Resposta
    latex.append(r'\begin{answer}')
    latex.append(resposta)
    latex.append(r'\end{answer}')
    
    return '\n'.join(latex)
