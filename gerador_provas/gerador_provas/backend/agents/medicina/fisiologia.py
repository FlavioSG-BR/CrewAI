# -*- coding: utf-8 -*-
"""
Agente especializado em Fisiologia Humana.
Gera questões sobre mecanismos fisiológicos, regulação hormonal,
homeostase e integração de sistemas.
"""

import random
from crewai import Agent
from backend.utils.logger import log_questao_gerada


class AgenteFisiologia:
    """Agente especializado em questões de Fisiologia."""
    
    def __init__(self):
        self.agent = Agent(
            role="Professor de Fisiologia Humana",
            goal="Criar questões sobre mecanismos fisiológicos e regulação homeostática",
            backstory="Fisiologista com doutorado em fisiologia cardiovascular e experiência em ensino médico.",
            verbose=False,
            allow_delegation=False
        )

    def gerar_questao_cardiovascular(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre fisiologia cardiovascular."""
        
        if dificuldade == "facil":
            enunciado = "Defina débito cardíaco e cite os fatores que o determinam."
            resposta = (
                "DÉBITO CARDÍACO (DC):\n"
                "Volume de sangue bombeado pelo coração por minuto.\n\n"
                "Fórmula: DC = FC × VS\n"
                "- FC: Frequência cardíaca (batimentos/min)\n"
                "- VS: Volume sistólico (volume ejetado por batimento)\n\n"
                "Valor normal: 5 L/min (em repouso)\n\n"
                "Fatores determinantes do VS:\n"
                "1. Pré-carga (Lei de Frank-Starling)\n"
                "2. Pós-carga (resistência vascular)\n"
                "3. Contratilidade miocárdica (inotropismo)\n\n"
                "Fatores que alteram FC:\n"
                "- Sistema nervoso autônomo\n"
                "- Hormônios (catecolaminas, tireoidianos)\n"
                "- Temperatura"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        elif dificuldade == "medio":
            enunciado = (
                "Explique a Lei de Frank-Starling do coração e sua importância clínica:\n"
                "a) Qual o mecanismo fisiológico?\n"
                "b) Por que é importante na insuficiência cardíaca?\n"
                "c) Represente graficamente a relação."
            )
            resposta = (
                "a) Mecanismo fisiológico:\n"
                "   - Quanto maior o estiramento das fibras miocárdicas (pré-carga), maior a força de contração\n"
                "   - Maior volume diastólico final → maior volume sistólico\n"
                "   - Permite igualar débitos de VD e VE batimento a batimento\n"
                "   - Mecanismo molecular: otimização da interação actina-miosina e sensibilidade ao Ca²⁺\n\n"
                "b) Importância na IC:\n"
                "   - Na IC, a curva de Frank-Starling está deslocada para baixo e para direita\n"
                "   - O coração gera menos força para o mesmo grau de estiramento\n"
                "   - Necessita de maior pré-carga para manter o DC → congestão\n"
                "   - Inotrópicos deslocam a curva para cima e esquerda\n\n"
                "c) Representação gráfica:\n"
                "   - Eixo X: Volume diastólico final (pré-carga)\n"
                "   - Eixo Y: Volume sistólico (ou trabalho cardíaco)\n"
                "   - Curva ascendente que atinge um platô\n"
                "   - IC: curva achatada abaixo da normal"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            enunciado = (
                "Paciente hipertenso apresenta PA = 180/110 mmHg.\n\n"
                "a) Quais os mecanismos de regulação da PA a curto, médio e longo prazo?\n"
                "b) Explique o reflexo barorreceptor e por que está 'resetado' neste paciente.\n"
                "c) Por que os IECA são eficazes na hipertensão?\n"
                "d) Calcule a pressão arterial média."
            )
            resposta = (
                "a) Mecanismos de regulação da PA:\n"
                "   CURTO PRAZO (segundos a minutos):\n"
                "   - Reflexo barorreceptor (principal)\n"
                "   - Reflexo quimiorreceptor\n"
                "   - Resposta isquêmica do SNC\n\n"
                "   MÉDIO PRAZO (minutos a horas):\n"
                "   - Sistema renina-angiotensina-aldosterona (SRAA)\n"
                "   - Relaxamento de estresse vascular\n"
                "   - Deslocamento de líquido capilar\n\n"
                "   LONGO PRAZO (dias a semanas):\n"
                "   - Controle renal de volume (natriurese pressórica)\n"
                "   - SRAA (remodelamento vascular)\n\n"
                "b) Reflexo barorreceptor:\n"
                "   - Sensores: barorreceptores no seio carotídeo e arco aórtico\n"
                "   - Aumento da PA → estiramento → aumento de disparos aferentes\n"
                "   - NTS → reduz simpático, aumenta parassimpático\n"
                "   - Resulta em: bradicardia, vasodilatação, redução do DC\n"
                "   'Resetting' na hipertensão crônica:\n"
                "   - O ponto de ajuste dos barorreceptores é elevado\n"
                "   - Passam a reconhecer a PA alta como 'normal'\n"
                "   - Não ativam adequadamente a resposta reflexa\n\n"
                "c) IECA na hipertensão:\n"
                "   - Bloqueiam ECA → reduz Angiotensina II\n"
                "   - Reduz vasoconstrição arteriolar (reduz RVP)\n"
                "   - Reduz secreção de aldosterona (reduz retenção de Na/H2O)\n"
                "   - Reduz remodelamento vascular\n"
                "   - Acumulam bradicinina (vasodilatador adicional)\n\n"
                "d) PAM = PAD + 1/3(PAS - PAD)\n"
                "   PAM = 110 + 1/3(180 - 110)\n"
                "   PAM = 110 + 23,3 = 133,3 mmHg\n"
                "   (Normal: 70-105 mmHg)"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("fisiologia")
        return {
            **questao,
            "tipo": "Fisiologia Cardiovascular",
            "materia": "fisiologia",
            "dificuldade": dificuldade
        }

    def gerar_questao_renal(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre fisiologia renal."""
        
        if dificuldade == "facil":
            enunciado = "Quais são as funções principais dos rins?"
            resposta = (
                "Funções renais:\n\n"
                "1. EXCREÇÃO de produtos do metabolismo:\n"
                "   - Ureia (metabolismo proteico)\n"
                "   - Creatinina (metabolismo muscular)\n"
                "   - Ácido úrico, bilirrubina\n\n"
                "2. REGULAÇÃO DO VOLUME E OSMOLARIDADE:\n"
                "   - Controle da excreção de água e sódio\n"
                "   - Manutenção do volume extracelular\n\n"
                "3. REGULAÇÃO DO EQUILÍBRIO ÁCIDO-BASE:\n"
                "   - Excreção de H⁺\n"
                "   - Reabsorção de HCO₃⁻\n"
                "   - Produção de amônia\n\n"
                "4. REGULAÇÃO DO EQUILÍBRIO ELETROLÍTICO:\n"
                "   - Na⁺, K⁺, Ca²⁺, fosfato, Mg²⁺\n\n"
                "5. FUNÇÃO ENDÓCRINA:\n"
                "   - Eritropoietina (produção de hemácias)\n"
                "   - Renina (regulação da PA)\n"
                "   - 1,25-diidroxivitamina D (metabolismo do cálcio)\n\n"
                "6. GLICONEOGÊNESE (jejum prolongado)"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        elif dificuldade == "medio":
            enunciado = (
                "Explique os processos de formação da urina:\n"
                "a) Filtração glomerular\n"
                "b) Reabsorção tubular\n"
                "c) Secreção tubular\n"
                "Cite exemplos de substâncias em cada processo."
            )
            resposta = (
                "a) FILTRAÇÃO GLOMERULAR:\n"
                "   - Ocorre no corpúsculo renal\n"
                "   - Passagem de plasma através da barreira glomerular\n"
                "   - Depende de: pressão hidrostática, permeabilidade, área\n"
                "   - TFG normal: 180 L/dia (125 mL/min)\n"
                "   - Filtradas: água, glicose, eletrólitos, ureia, creatinina\n"
                "   - NÃO filtradas: proteínas, células\n\n"
                "b) REABSORÇÃO TUBULAR:\n"
                "   - Retorno de substâncias do filtrado para o sangue\n"
                "   - TCP: maior reabsorção (65-70% do filtrado)\n"
                "     * Glicose, aminoácidos (100% em condições normais)\n"
                "     * Na⁺, Cl⁻, K⁺, HCO₃⁻, água\n"
                "   - Alça de Henle: NaCl, água\n"
                "   - TCD e ducto coletor: Na⁺ (aldosterona), água (ADH)\n\n"
                "c) SECREÇÃO TUBULAR:\n"
                "   - Passagem de substâncias do sangue para o túbulo\n"
                "   - Elimina substâncias não filtradas ou em excesso\n"
                "   - Exemplos:\n"
                "     * H⁺ (regulação ácido-base)\n"
                "     * K⁺ (no TCD, dependente de aldosterona)\n"
                "     * Ácidos e bases orgânicas\n"
                "     * Fármacos (penicilina, furosemida)\n"
                "     * Creatinina (pequena quantidade)"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            tfg = random.choice([60, 90, 120])
            creatinina_plasmatica = round(120 / tfg, 1)
            
            enunciado = (
                f"Paciente de 60 anos apresenta creatinina sérica de {creatinina_plasmatica} mg/dL.\n\n"
                "a) Estime a TFG usando a fórmula simplificada (Clearance de creatinina ≈ 120/Cr).\n"
                "b) Por que a creatinina é usada para estimar a TFG?\n"
                "c) Quais as limitações deste marcador?\n"
                "d) Como o rim compensa a redução de néfrons funcionantes?"
            )
            resposta = (
                f"a) TFG estimada:\n"
                f"   Clearance Cr ≈ 120 / {creatinina_plasmatica} = {tfg} mL/min\n"
                f"   (fórmula simplificada; na prática usar CKD-EPI)\n\n"
                "b) Por que usar creatinina:\n"
                "   - Produção relativamente constante (metabolismo muscular)\n"
                "   - Livremente filtrada no glomérulo\n"
                "   - Minimamente reabsorvida\n"
                "   - Não metabolizada pelo rim\n"
                "   - Medição simples e barata\n\n"
                "c) Limitações:\n"
                "   - Secreção tubular (superestima TFG, especialmente se TFG baixa)\n"
                "   - Varia com massa muscular (idosos, desnutridos, amputados)\n"
                "   - Afetada por dieta rica em proteínas/creatina\n"
                "   - Drogas competem pela secreção (trimetoprim, cimetidina)\n"
                "   - Não detecta lesão aguda precoce (reserva funcional)\n\n"
                "d) Compensação renal (hiperfiltração):\n"
                "   - Néfrons remanescentes hipertrofiam\n"
                "   - Aumento da TFG por néfron individual\n"
                "   - Mantém função até perda de 50-70% dos néfrons\n"
                "   - A longo prazo: glomeruloesclerose (ciclo vicioso)\n"
                "   - Justifica controle rigoroso da PA (IECA/BRA protegem)"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("fisiologia")
        return {
            **questao,
            "tipo": "Fisiologia Renal",
            "materia": "fisiologia",
            "dificuldade": dificuldade
        }

    def gerar_questao_endocrina(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre fisiologia endócrina."""
        
        if dificuldade == "facil":
            enunciado = "Explique o eixo hipotálamo-hipófise-tireoide e o mecanismo de feedback negativo."
            resposta = (
                "EIXO HIPOTÁLAMO-HIPÓFISE-TIREOIDE:\n\n"
                "1. HIPOTÁLAMO:\n"
                "   - Secreta TRH (hormônio liberador de tireotrofina)\n"
                "   - Liberado na eminência mediana\n"
                "   - Chega à hipófise via sistema porta-hipofisário\n\n"
                "2. HIPÓFISE (adenohipófise):\n"
                "   - TRH estimula os tireotrofos\n"
                "   - Secretam TSH (hormônio tireoestimulante)\n\n"
                "3. TIREOIDE:\n"
                "   - TSH estimula células foliculares\n"
                "   - Produzem T4 (tiroxina) e T3 (triiodotironina)\n"
                "   - T4 é convertido em T3 (forma ativa) nos tecidos\n\n"
                "FEEDBACK NEGATIVO:\n"
                "- T3 e T4 circulantes inibem:\n"
                "  * Hipotálamo (reduz TRH)\n"
                "  * Hipófise (reduz resposta ao TRH e secreção de TSH)\n"
                "- Mantém níveis hormonais em faixa fisiológica\n"
                "- No hipertireoidismo: TSH suprimido\n"
                "- No hipotireoidismo primário: TSH elevado"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        elif dificuldade == "medio":
            enunciado = (
                "Sobre a regulação da glicemia:\n"
                "a) Quais hormônios participam e qual o efeito de cada um?\n"
                "b) O que acontece após uma refeição rica em carboidratos?\n"
                "c) E durante o jejum prolongado?"
            )
            resposta = (
                "a) Hormônios reguladores:\n"
                "   INSULINA (hipoglicemiante):\n"
                "   - Células beta das ilhotas pancreáticas\n"
                "   - Estimula captação de glicose (GLUT4)\n"
                "   - Estimula glicogênese (síntese de glicogênio)\n"
                "   - Estimula lipogênese\n"
                "   - Inibe gliconeogênese e glicogenólise\n\n"
                "   GLUCAGON (hiperglicemiante):\n"
                "   - Células alfa das ilhotas\n"
                "   - Estimula glicogenólise hepática\n"
                "   - Estimula gliconeogênese\n"
                "   - Estimula lipólise\n\n"
                "   Outros hiperglicemiantes: cortisol, GH, catecolaminas\n\n"
                "b) Após refeição rica em carboidratos:\n"
                "   - Glicemia aumenta → estímulo para células beta\n"
                "   - ↑ Secreção de insulina (bifásica)\n"
                "   - ↓ Secreção de glucagon\n"
                "   - Glicose captada por músculo e tecido adiposo\n"
                "   - Síntese de glicogênio no fígado e músculo\n"
                "   - Glicemia normaliza em 2h\n\n"
                "c) Jejum prolongado:\n"
                "   - Glicemia tende a cair → células alfa estimuladas\n"
                "   - ↑ Glucagon, ↓ Insulina\n"
                "   - Glicogenólise hepática (primeiras horas)\n"
                "   - Gliconeogênese (aminoácidos, glicerol, lactato)\n"
                "   - Lipólise → ácidos graxos → corpos cetônicos\n"
                "   - Cérebro passa a usar corpos cetônicos\n"
                "   - Preservação de proteínas musculares"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            enunciado = (
                "Paciente com suspeita de Síndrome de Cushing.\n\n"
                "a) Quais são as causas de hipercortisolismo e como diferenciá-las?\n"
                "b) Explique o teste de supressão com dexametasona.\n"
                "c) Quais as manifestações clínicas do excesso de cortisol?\n"
                "d) Por que pacientes com Cushing têm hipertensão e hipocalemia?"
            )
            resposta = (
                "a) Causas de hipercortisolismo:\n"
                "   ACTH-DEPENDENTE (80%):\n"
                "   - Doença de Cushing (adenoma hipofisário): ACTH alto\n"
                "   - Secreção ectópica de ACTH (carcinoma broncogênico)\n\n"
                "   ACTH-INDEPENDENTE (20%):\n"
                "   - Adenoma adrenal: ACTH suprimido\n"
                "   - Carcinoma adrenal\n"
                "   - Hiperplasia nodular\n"
                "   - Cushing iatrogênico (corticoides exógenos)\n\n"
                "b) Teste de supressão com dexametasona:\n"
                "   Baixa dose (1mg overnight):\n"
                "   - Rastreamento: normal suprime cortisol\n"
                "   - Cushing: não suprime (cortisol matinal > 1,8 µg/dL)\n\n"
                "   Alta dose (8mg):\n"
                "   - Doença de Cushing: suprime > 50%\n"
                "   - Ectópico ou adrenal: não suprime\n\n"
                "c) Manifestações clínicas:\n"
                "   - Obesidade centrípeta, fácies de lua cheia\n"
                "   - Giba de búfalo, estrias violáceas\n"
                "   - Hipertensão, hiperglicemia\n"
                "   - Fraqueza muscular proximal (miopatia)\n"
                "   - Osteoporose, fraturas\n"
                "   - Pele fina, equimoses fáceis\n"
                "   - Alterações psiquiátricas\n\n"
                "d) Hipertensão e hipocalemia:\n"
                "   - Cortisol em excesso satura a 11β-HSD2\n"
                "   - Esta enzima converte cortisol em cortisona (inativa)\n"
                "   - Quando saturada, cortisol ativa receptores mineralocorticoides\n"
                "   - Efeito 'mineralocorticoide': retenção de Na⁺, excreção de K⁺\n"
                "   - Expansão de volume → hipertensão\n"
                "   - Hipocalemia e alcalose metabólica"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("fisiologia")
        return {
            **questao,
            "tipo": "Fisiologia Endócrina",
            "materia": "fisiologia",
            "dificuldade": dificuldade
        }

    def gerar_questao(self, topico: str = "geral", dificuldade: str = "medio", observacoes: str = "") -> dict:
        """Gera uma questão de fisiologia baseada no tópico e dificuldade."""
        topico_lower = topico.lower().replace(" ", "_")
        
        mapeamento = {
            "cardiovascular": self.gerar_questao_cardiovascular,
            "cardio": self.gerar_questao_cardiovascular,
            "coracao": self.gerar_questao_cardiovascular,
            "hemodinamica": self.gerar_questao_cardiovascular,
            "renal": self.gerar_questao_renal,
            "rim": self.gerar_questao_renal,
            "nefron": self.gerar_questao_renal,
            "urina": self.gerar_questao_renal,
            "endocrina": self.gerar_questao_endocrina,
            "endocrino": self.gerar_questao_endocrina,
            "hormonios": self.gerar_questao_endocrina,
            "tireoide": self.gerar_questao_endocrina,
        }
        
        if topico_lower in mapeamento:
            questao = mapeamento[topico_lower](dificuldade)
        else:
            metodo = random.choice([
                self.gerar_questao_cardiovascular,
                self.gerar_questao_renal,
                self.gerar_questao_endocrina
            ])
            questao = metodo(dificuldade)
        
        if observacoes:
            questao["observacoes_professor"] = observacoes
        
        return questao

