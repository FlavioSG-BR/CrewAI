# -*- coding: utf-8 -*-
"""
Prompts especializados para geração de questões de Medicina.
Estes prompts são usados pelos agentes de IA para gerar questões originais.
"""

# =============================================================================
# PROMPTS BASE
# =============================================================================

SYSTEM_PROMPT_PROFESSOR = """Você é um professor universitário de medicina com vasta experiência em elaboração de provas.
Você deve criar questões precisas, cientificamente corretas e pedagogicamente adequadas.

DIRETRIZES:
1. Use terminologia médica correta
2. Baseie-se em evidências científicas atuais
3. Inclua referências quando relevante
4. Adapte a linguagem ao nível de dificuldade solicitado
5. Forneça respostas completas e didáticas
"""

# =============================================================================
# FARMACOLOGIA
# =============================================================================

PROMPT_FARMACOLOGIA = """
{system_prompt}

DISCIPLINA: Farmacologia
TÓPICO: {topico}
DIFICULDADE: {dificuldade}
{observacoes}

Crie uma questão de farmacologia seguindo estas diretrizes:

PARA DIFICULDADE FÁCIL:
- Conceitos básicos (mecanismo de ação, classificação)
- Perguntas diretas
- Resposta objetiva

PARA DIFICULDADE MÉDIA:
- Correlação clínica simples
- Comparação entre fármacos
- Efeitos adversos e interações

PARA DIFICULDADE DIFÍCIL:
- Caso clínico complexo
- Múltiplas variáveis
- Decisão terapêutica fundamentada
- Integração com outras disciplinas

FORMATO DA RESPOSTA (JSON):
{{
    "enunciado": "Texto completo da questão",
    "resposta": "Resposta detalhada e didática",
    "tipo": "Subtópico específico",
    "referencias": ["Referências bibliográficas relevantes"],
    "palavras_chave": ["Termos importantes para indexação"]
}}
"""

# =============================================================================
# HISTOLOGIA
# =============================================================================

PROMPT_HISTOLOGIA = """
{system_prompt}

DISCIPLINA: Histologia
TÓPICO: {topico}
DIFICULDADE: {dificuldade}
{observacoes}

Crie uma questão de histologia que envolva:

PARA DIFICULDADE FÁCIL:
- Identificação de tecidos básicos
- Características morfológicas fundamentais
- Funções principais dos tecidos

PARA DIFICULDADE MÉDIA:
- Diferenciação entre tecidos semelhantes
- Correlação estrutura-função
- Colorações histológicas

PARA DIFICULDADE DIFÍCIL:
- Correlação histopatológica
- Diagnóstico diferencial microscópico
- Integração com clínica

FORMATO DA RESPOSTA (JSON):
{{
    "enunciado": "Texto completo da questão",
    "resposta": "Resposta detalhada e didática",
    "tipo": "Subtópico específico",
    "referencias": ["Referências bibliográficas relevantes"],
    "palavras_chave": ["Termos importantes para indexação"]
}}
"""

# =============================================================================
# ANATOMIA
# =============================================================================

PROMPT_ANATOMIA = """
{system_prompt}

DISCIPLINA: Anatomia Humana
TÓPICO: {topico}
DIFICULDADE: {dificuldade}
{observacoes}

Crie uma questão de anatomia que envolva:

PARA DIFICULDADE FÁCIL:
- Identificação de estruturas
- Nomenclatura anatômica
- Localizações básicas

PARA DIFICULDADE MÉDIA:
- Relações topográficas
- Inervação e vascularização
- Correlação com função

PARA DIFICULDADE DIFÍCIL:
- Anatomia clínica/cirúrgica
- Variações anatômicas
- Correlação com imagem (TC, RM)
- Abordagens cirúrgicas

FORMATO DA RESPOSTA (JSON):
{{
    "enunciado": "Texto completo da questão",
    "resposta": "Resposta detalhada e didática",
    "tipo": "Subtópico específico",
    "referencias": ["Referências bibliográficas relevantes"],
    "palavras_chave": ["Termos importantes para indexação"]
}}
"""

# =============================================================================
# FISIOLOGIA
# =============================================================================

PROMPT_FISIOLOGIA = """
{system_prompt}

DISCIPLINA: Fisiologia Humana
TÓPICO: {topico}
DIFICULDADE: {dificuldade}
{observacoes}

Crie uma questão de fisiologia que envolva:

PARA DIFICULDADE FÁCIL:
- Conceitos fisiológicos básicos
- Definições e valores normais
- Mecanismos simples

PARA DIFICULDADE MÉDIA:
- Regulação de sistemas
- Interpretação de curvas/gráficos
- Integração entre sistemas

PARA DIFICULDADE DIFÍCIL:
- Fisiopatologia
- Cálculos (clearance, débito cardíaco)
- Distúrbios complexos
- Compensações fisiológicas

FORMATO DA RESPOSTA (JSON):
{{
    "enunciado": "Texto completo da questão",
    "resposta": "Resposta detalhada e didática",
    "tipo": "Subtópico específico",
    "referencias": ["Referências bibliográficas relevantes"],
    "palavras_chave": ["Termos importantes para indexação"]
}}
"""

# =============================================================================
# PATOLOGIA
# =============================================================================

PROMPT_PATOLOGIA = """
{system_prompt}

DISCIPLINA: Patologia
TÓPICO: {topico}
DIFICULDADE: {dificuldade}
{observacoes}

Crie uma questão de patologia que envolva:

PARA DIFICULDADE FÁCIL:
- Conceitos de patologia geral
- Tipos de lesão celular
- Definições básicas

PARA DIFICULDADE MÉDIA:
- Fisiopatologia de doenças
- Achados macroscópicos/microscópicos
- Correlação clínico-patológica

PARA DIFICULDADE DIFÍCIL:
- Diagnóstico diferencial
- Patologia molecular
- Marcadores tumorais
- Gradação e estadiamento

FORMATO DA RESPOSTA (JSON):
{{
    "enunciado": "Texto completo da questão",
    "resposta": "Resposta detalhada e didática",
    "tipo": "Subtópico específico",
    "referencias": ["Referências bibliográficas relevantes"],
    "palavras_chave": ["Termos importantes para indexação"]
}}
"""

# =============================================================================
# BIOQUÍMICA
# =============================================================================

PROMPT_BIOQUIMICA = """
{system_prompt}

DISCIPLINA: Bioquímica
TÓPICO: {topico}
DIFICULDADE: {dificuldade}
{observacoes}

Crie uma questão de bioquímica que envolva:

PARA DIFICULDADE FÁCIL:
- Estrutura de biomoléculas
- Vias metabólicas básicas
- Enzimas e cofatores

PARA DIFICULDADE MÉDIA:
- Regulação metabólica
- Integração de vias
- Bioquímica clínica

PARA DIFICULDADE DIFÍCIL:
- Erros inatos do metabolismo
- Bioquímica de doenças
- Interpretação de exames laboratoriais
- Mecanismos moleculares complexos

FORMATO DA RESPOSTA (JSON):
{{
    "enunciado": "Texto completo da questão",
    "resposta": "Resposta detalhada e didática",
    "tipo": "Subtópico específico",
    "referencias": ["Referências bibliográficas relevantes"],
    "palavras_chave": ["Termos importantes para indexação"]
}}
"""

# =============================================================================
# MICROBIOLOGIA
# =============================================================================

PROMPT_MICROBIOLOGIA = """
{system_prompt}

DISCIPLINA: Microbiologia e Imunologia
TÓPICO: {topico}
DIFICULDADE: {dificuldade}
{observacoes}

Crie uma questão de microbiologia/imunologia que envolva:

PARA DIFICULDADE FÁCIL:
- Classificação de microrganismos
- Estrutura bacteriana/viral
- Conceitos imunológicos básicos

PARA DIFICULDADE MÉDIA:
- Mecanismos de patogenicidade
- Diagnóstico microbiológico
- Resposta imune específica

PARA DIFICULDADE DIFÍCIL:
- Resistência antimicrobiana
- Imunopatologia
- Vacinas e imunoterapia
- Casos de infecção complexa

FORMATO DA RESPOSTA (JSON):
{{
    "enunciado": "Texto completo da questão",
    "resposta": "Resposta detalhada e didática",
    "tipo": "Subtópico específico",
    "referencias": ["Referências bibliográficas relevantes"],
    "palavras_chave": ["Termos importantes para indexação"]
}}
"""

# =============================================================================
# CASOS CLÍNICOS
# =============================================================================

PROMPT_CASO_CLINICO = """
{system_prompt}

TIPO: Caso Clínico Integrado
ÁREA: {topico}
DIFICULDADE: {dificuldade}
{observacoes}

Crie um caso clínico completo seguindo este formato:

ESTRUTURA DO CASO:
1. IDENTIFICAÇÃO: Idade, sexo, profissão (quando relevante)
2. QUEIXA PRINCIPAL: Motivo da consulta
3. HISTÓRIA DA DOENÇA ATUAL: Evolução cronológica
4. ANTECEDENTES: Pessoais e familiares relevantes
5. EXAME FÍSICO: Achados pertinentes
6. EXAMES COMPLEMENTARES: Se aplicável

PARA DIFICULDADE FÁCIL:
- Diagnóstico clássico
- Poucos diagnósticos diferenciais
- Conduta padrão

PARA DIFICULDADE MÉDIA:
- Apresentação típica com complicação
- Múltiplos diagnósticos diferenciais
- Necessidade de exames complementares

PARA DIFICULDADE DIFÍCIL:
- Apresentação atípica
- Múltiplas comorbidades
- Decisões terapêuticas complexas
- Integração de múltiplas especialidades

PERGUNTAS A INCLUIR:
a) Qual o diagnóstico mais provável?
b) Quais exames solicitar?
c) Qual a conduta terapêutica?
d) Explique a fisiopatologia

FORMATO DA RESPOSTA (JSON):
{{
    "enunciado": "Caso clínico completo com perguntas",
    "resposta": "Respostas detalhadas para cada pergunta",
    "tipo": "Área/especialidade do caso",
    "referencias": ["Referências bibliográficas"],
    "palavras_chave": ["Diagnósticos e conceitos-chave"]
}}
"""

# =============================================================================
# MAPEAMENTO DE PROMPTS
# =============================================================================

PROMPTS = {
    "farmacologia": PROMPT_FARMACOLOGIA,
    "histologia": PROMPT_HISTOLOGIA,
    "anatomia": PROMPT_ANATOMIA,
    "fisiologia": PROMPT_FISIOLOGIA,
    "patologia": PROMPT_PATOLOGIA,
    "bioquimica": PROMPT_BIOQUIMICA,
    "microbiologia": PROMPT_MICROBIOLOGIA,
    "casos_clinicos": PROMPT_CASO_CLINICO,
}


def get_prompt(disciplina: str, topico: str, dificuldade: str, observacoes: str = "") -> str:
    """
    Retorna o prompt formatado para uma disciplina específica.
    
    Args:
        disciplina: Nome da disciplina (farmacologia, histologia, etc.)
        topico: Tópico específico dentro da disciplina
        dificuldade: Nível de dificuldade (facil, medio, dificil)
        observacoes: Observações adicionais do professor
    
    Returns:
        Prompt formatado pronto para enviar ao LLM
    """
    template = PROMPTS.get(disciplina.lower(), PROMPT_FARMACOLOGIA)
    
    obs_formatadas = ""
    if observacoes:
        obs_formatadas = f"\nOBSERVAÇÕES DO PROFESSOR:\n{observacoes}\n"
    
    return template.format(
        system_prompt=SYSTEM_PROMPT_PROFESSOR,
        topico=topico,
        dificuldade=dificuldade.upper(),
        observacoes=obs_formatadas
    )

