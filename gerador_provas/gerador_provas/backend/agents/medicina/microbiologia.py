# -*- coding: utf-8 -*-
"""
Agente especializado em Microbiologia e Imunologia.
Gera questões sobre bactérias, vírus, fungos, parasitas e imunologia.
"""

import random
from crewai import Agent
from backend.utils.logger import log_questao_gerada


class AgenteMicrobiologia:
    """Agente especializado em questões de Microbiologia."""
    
    def __init__(self):
        self.agent = Agent(
            role="Professor de Microbiologia e Imunologia",
            goal="Criar questões sobre patógenos, mecanismos de infecção e resposta imune",
            backstory="Microbiologista com especialização em bacteriologia clínica e imunologia.",
            verbose=False,
            allow_delegation=False
        )

    def gerar_questao_bacteriologia(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre bacteriologia."""
        
        if dificuldade == "facil":
            enunciado = "Explique a diferença entre bactérias Gram-positivas e Gram-negativas."
            resposta = (
                "COLORAÇÃO DE GRAM:\n\n"
                "GRAM-POSITIVAS (coram em ROXO/VIOLETA):\n"
                "- Parede celular ESPESSA (20-80nm)\n"
                "- Muito peptidoglicano (até 90%)\n"
                "- Ácido teicoico e lipoteicoico\n"
                "- Sem membrana externa\n"
                "- Retêm o cristal violeta + lugol\n"
                "- Exemplos: Staphylococcus, Streptococcus, Enterococcus\n\n"
                "GRAM-NEGATIVAS (coram em ROSA/VERMELHO):\n"
                "- Parede celular FINA (10-15nm)\n"
                "- Pouco peptidoglicano (5-20%)\n"
                "- Espaço periplasmático\n"
                "- MEMBRANA EXTERNA com LPS (lipopolissacarídeo)\n"
                "- O álcool remove cristal violeta, cora com safranina\n"
                "- Exemplos: E. coli, Pseudomonas, Klebsiella, Neisseria\n\n"
                "IMPORTÂNCIA CLÍNICA:\n"
                "- Gram-positivas: sensíveis a penicilinas, vancomicina\n"
                "- Gram-negativas: LPS causa choque séptico; mais resistentes"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        elif dificuldade == "medio":
            enunciado = (
                "Paciente com pneumonia comunitária grave.\n"
                "a) Quais os principais agentes etiológicos?\n"
                "b) Como diferenciá-los clinicamente?\n"
                "c) Qual a cobertura antimicrobiana empírica recomendada?"
            )
            resposta = (
                "a) Principais agentes:\n"
                "   TÍPICOS:\n"
                "   - Streptococcus pneumoniae (mais comum)\n"
                "   - Haemophilus influenzae\n"
                "   - Staphylococcus aureus (pós-influenza, grave)\n\n"
                "   ATÍPICOS:\n"
                "   - Mycoplasma pneumoniae (jovens)\n"
                "   - Chlamydophila pneumoniae\n"
                "   - Legionella pneumophila (grave, hiponatremia)\n\n"
                "b) Diferenciação clínica:\n"
                "   TÍPICA (Pneumococo):\n"
                "   - Início súbito, febre alta\n"
                "   - Tosse produtiva, escarro ferruginoso\n"
                "   - Consolidação lobar ao exame e RX\n"
                "   - Leucocitose com desvio à esquerda\n\n"
                "   ATÍPICA (Mycoplasma, Chlamydia):\n"
                "   - Início insidioso\n"
                "   - Tosse seca, manifestações extrapulmonares\n"
                "   - Infiltrado intersticial\n"
                "   - Dissociação clínico-radiológica\n\n"
                "c) Tratamento empírico (PAC grave):\n"
                "   - Beta-lactâmico + Macrolídeo:\n"
                "     Ceftriaxona + Azitromicina, ou\n"
                "   - Fluoroquinolona respiratória:\n"
                "     Levofloxacino ou Moxifloxacino\n"
                "   * Cobre típicos e atípicos"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            enunciado = (
                "Sobre mecanismos de resistência bacteriana:\n"
                "a) Quais os principais mecanismos de resistência?\n"
                "b) Explique a resistência do MRSA aos beta-lactâmicos.\n"
                "c) O que são beta-lactamases de espectro estendido (ESBL)?\n"
                "d) Por que a resistência é um problema de saúde pública?"
            )
            resposta = (
                "a) Mecanismos de resistência:\n"
                "   1. INATIVAÇÃO ENZIMÁTICA:\n"
                "      - Beta-lactamases (hidrolisam anel beta-lactâmico)\n"
                "      - Enzimas modificadoras de aminoglicosídeos\n\n"
                "   2. ALTERAÇÃO DO ALVO:\n"
                "      - PBPs alteradas (MRSA)\n"
                "      - Alteração ribossomal\n"
                "      - Mutação em DNA girase (quinolonas)\n\n"
                "   3. DIMINUIÇÃO DA PERMEABILIDADE:\n"
                "      - Perda/alteração de porinas\n"
                "      - Comum em Gram-negativos\n\n"
                "   4. EFLUXO ATIVO:\n"
                "      - Bombas que expulsam o antibiótico\n"
                "      - Resistência a múltiplas drogas\n\n"
                "b) Resistência do MRSA:\n"
                "   - Aquisição do gene mecA (cassete SCCmec)\n"
                "   - Codifica PBP2a (proteína ligadora de penicilina alterada)\n"
                "   - PBP2a tem baixíssima afinidade por beta-lactâmicos\n"
                "   - A parede é sintetizada mesmo com antibiótico presente\n"
                "   - Resistência a TODOS os beta-lactâmicos\n"
                "   - Tratamento: Vancomicina, Daptomicina, Linezolida\n\n"
                "c) ESBL (Extended-Spectrum Beta-Lactamases):\n"
                "   - Beta-lactamases que hidrolisam cefalosporinas de 3ª/4ª geração\n"
                "   - Derivadas de TEM, SHV, CTX-M\n"
                "   - Comuns em Enterobacteriaceae (E. coli, Klebsiella)\n"
                "   - Inativadas por inibidores (clavulanato) in vitro\n"
                "   - Tratamento: Carbapenêmicos\n\n"
                "d) Impacto na saúde pública:\n"
                "   - Infecções mais difíceis de tratar\n"
                "   - Maior morbidade, mortalidade e custos\n"
                "   - Uso indiscriminado acelera seleção de resistentes\n"
                "   - Poucos novos antibióticos em desenvolvimento\n"
                "   - Risco de era 'pós-antibiótico'\n"
                "   - Necessidade de uso racional e programas de stewardship"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("microbiologia")
        return {
            **questao,
            "tipo": "Bacteriologia",
            "materia": "microbiologia",
            "dificuldade": dificuldade
        }

    def gerar_questao_imunologia(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre imunologia."""
        
        if dificuldade == "facil":
            enunciado = "Diferencie imunidade inata de imunidade adaptativa."
            resposta = (
                "IMUNIDADE INATA (Natural):\n"
                "- Primeira linha de defesa\n"
                "- Resposta IMEDIATA (minutos a horas)\n"
                "- Não requer exposição prévia\n"
                "- NÃO gera memória imunológica\n"
                "- Reconhece padrões conservados (PAMPs)\n"
                "- Componentes:\n"
                "  * Barreiras físicas (pele, mucosas)\n"
                "  * Fagócitos (macrófagos, neutrófilos)\n"
                "  * Células NK\n"
                "  * Sistema complemento\n"
                "  * Citocinas (interferons)\n\n"
                "IMUNIDADE ADAPTATIVA (Adquirida):\n"
                "- Segunda linha de defesa\n"
                "- Resposta LENTA (dias a semanas na primeira vez)\n"
                "- Requer sensibilização prévia\n"
                "- GERA memória imunológica (resposta mais rápida na reexposição)\n"
                "- Reconhecimento específico (antígenos)\n"
                "- Componentes:\n"
                "  * Linfócitos T (celular)\n"
                "  * Linfócitos B e anticorpos (humoral)\n"
                "  * Células de memória"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        elif dificuldade == "medio":
            enunciado = (
                "Sobre as classes de anticorpos (imunoglobulinas):\n"
                "a) Cite as 5 classes e suas principais funções.\n"
                "b) Qual a primeira classe produzida na resposta primária?\n"
                "c) Qual atravessa a placenta?"
            )
            resposta = (
                "a) Classes de imunoglobulinas:\n"
                "   IgG (75%):\n"
                "   - Mais abundante no soro\n"
                "   - Atravessa a placenta (imunidade passiva ao feto)\n"
                "   - Opsonização, ativação do complemento\n"
                "   - Neutralização de toxinas e vírus\n\n"
                "   IgM (10%):\n"
                "   - Primeira a ser produzida (resposta primária)\n"
                "   - Pentamérica (5 unidades)\n"
                "   - Maior eficiência na ativação do complemento\n"
                "   - Não atravessa placenta\n\n"
                "   IgA (15%):\n"
                "   - Principal Ig das secreções (saliva, leite, lágrima)\n"
                "   - Forma dimérica nas mucosas\n"
                "   - Proteção de superfícies mucosas\n\n"
                "   IgE (<0.01%):\n"
                "   - Associada a alergias e parasitoses\n"
                "   - Liga-se a mastócitos e basófilos\n"
                "   - Liberação de histamina (hipersensibilidade tipo I)\n\n"
                "   IgD (<1%):\n"
                "   - Receptor de antígeno em linfócitos B naive\n"
                "   - Função pouco conhecida no soro\n\n"
                "b) IgM é a primeira produzida:\n"
                "   - Marcador de infecção aguda/recente\n"
                "   - Seguida por IgG (memória/crônica)\n\n"
                "c) IgG atravessa a placenta:\n"
                "   - Transferência via receptor FcRn\n"
                "   - Protege o recém-nascido nos primeiros meses"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            enunciado = (
                "Paciente asmático em crise após exposição a pólen.\n\n"
                "a) Que tipo de reação de hipersensibilidade está ocorrendo?\n"
                "b) Descreva o mecanismo fisiopatológico.\n"
                "c) Qual o papel da IgE e dos mastócitos?\n"
                "d) Explique a fase imediata e a fase tardia da reação."
            )
            resposta = (
                "a) Hipersensibilidade tipo I (imediata/anafilática):\n"
                "   - Mediada por IgE\n"
                "   - Resposta alérgica clássica\n\n"
                "b) Mecanismo fisiopatológico:\n"
                "   SENSIBILIZAÇÃO (primeira exposição):\n"
                "   1. Alérgeno é processado por APCs\n"
                "   2. Apresentação a linfócitos Th2\n"
                "   3. Th2 produz IL-4, IL-13 → switching para IgE\n"
                "   4. Linfócitos B produzem IgE específica\n"
                "   5. IgE liga-se a receptores FcεRI em mastócitos\n"
                "   6. Mastócitos sensibilizados (memória)\n\n"
                "   REEXPOSIÇÃO:\n"
                "   1. Alérgeno faz crosslinking de IgE nos mastócitos\n"
                "   2. Degranulação (liberação de mediadores)\n"
                "   3. Sintomas alérgicos\n\n"
                "c) Papel da IgE e mastócitos:\n"
                "   IgE:\n"
                "   - 'Antena' que reconhece o alérgeno\n"
                "   - Fica ligada à superfície do mastócito\n"
                "   - Crosslinking ativa o mastócito\n\n"
                "   MASTÓCITOS:\n"
                "   - Células efetoras da resposta alérgica\n"
                "   - Liberam mediadores pré-formados e neoformados\n"
                "   - Localizados em mucosas e tecido conjuntivo\n\n"
                "d) Fases da reação:\n"
                "   FASE IMEDIATA (minutos):\n"
                "   - Mediadores pré-formados (grânulos):\n"
                "     * Histamina: vasodilatação, permeabilidade, broncoespasmo\n"
                "     * Triptase, heparina\n"
                "   - Sintomas: prurido, rinorreia, broncoespasmo\n\n"
                "   FASE TARDIA (4-8 horas):\n"
                "   - Mediadores neoformados:\n"
                "     * Leucotrienos (LTC4, LTD4): broncoespasmo prolongado\n"
                "     * Prostaglandinas\n"
                "     * Citocinas (IL-4, IL-5, IL-13)\n"
                "   - Influxo de eosinófilos (inflamação alérgica)\n"
                "   - Sintomas persistentes, hiperreatividade brônquica"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("microbiologia")
        return {
            **questao,
            "tipo": "Imunologia",
            "materia": "microbiologia",
            "dificuldade": dificuldade
        }

    def gerar_questao(self, topico: str = "geral", dificuldade: str = "medio", observacoes: str = "") -> dict:
        """Gera uma questão de microbiologia/imunologia."""
        topico_lower = topico.lower().replace(" ", "_")
        
        mapeamento = {
            "bacteriologia": self.gerar_questao_bacteriologia,
            "bacterias": self.gerar_questao_bacteriologia,
            "gram": self.gerar_questao_bacteriologia,
            "antibioticos": self.gerar_questao_bacteriologia,
            "resistencia": self.gerar_questao_bacteriologia,
            "imunologia": self.gerar_questao_imunologia,
            "imunidade": self.gerar_questao_imunologia,
            "anticorpos": self.gerar_questao_imunologia,
            "alergia": self.gerar_questao_imunologia,
        }
        
        if topico_lower in mapeamento:
            questao = mapeamento[topico_lower](dificuldade)
        else:
            metodo = random.choice([self.gerar_questao_bacteriologia, self.gerar_questao_imunologia])
            questao = metodo(dificuldade)
        
        if observacoes:
            questao["observacoes_professor"] = observacoes
        
        return questao

