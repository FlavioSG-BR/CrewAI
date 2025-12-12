# -*- coding: utf-8 -*-
"""
Agente especializado em Patologia.
Gera questões sobre patologia geral e sistêmica,
correlações clínico-patológicas e diagnóstico diferencial.
"""

import random
from crewai import Agent
from backend.utils.logger import log_questao_gerada


class AgentePatologia:
    """Agente especializado em questões de Patologia."""
    
    def __init__(self):
        self.agent = Agent(
            role="Professor de Patologia",
            goal="Criar questões sobre mecanismos de doença e correlação clínico-patológica",
            backstory="Patologista com especialização em anatomia patológica e 15 anos de experiência diagnóstica.",
            verbose=False,
            allow_delegation=False
        )

    def gerar_questao_patologia_geral(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre patologia geral."""
        
        if dificuldade == "facil":
            opcoes = [
                {
                    "enunciado": "Diferencie necrose de apoptose.",
                    "resposta": (
                        "NECROSE:\n"
                        "- Morte celular PATOLÓGICA por agressão externa\n"
                        "- Processo passivo, não programado\n"
                        "- Afeta grupos de células\n"
                        "- Tumefação celular, ruptura de membrana\n"
                        "- Lise e liberação de conteúdo intracelular\n"
                        "- Provoca INFLAMAÇÃO\n"
                        "- Causas: isquemia, toxinas, trauma\n\n"
                        "APOPTOSE:\n"
                        "- Morte celular PROGRAMADA (fisiológica ou patológica)\n"
                        "- Processo ativo, dependente de energia e genes\n"
                        "- Afeta células individuais\n"
                        "- Encolhimento celular, condensação de cromatina\n"
                        "- Formação de corpos apoptóticos (fragmentos)\n"
                        "- Fagocitados sem inflamação\n"
                        "- Papel: desenvolvimento, homeostase, eliminação de células danificadas"
                    )
                },
                {
                    "enunciado": "Cite os tipos de necrose e dê um exemplo de cada.",
                    "resposta": (
                        "TIPOS DE NECROSE:\n\n"
                        "1. Necrose de COAGULAÇÃO:\n"
                        "   - Preserva arquitetura tecidual temporariamente\n"
                        "   - Exemplo: Infarto do miocárdio, infarto renal\n\n"
                        "2. Necrose de LIQUEFAÇÃO:\n"
                        "   - Digestão enzimática do tecido\n"
                        "   - Exemplo: Abscesso bacteriano, AVC isquêmico\n\n"
                        "3. Necrose CASEOSA:\n"
                        "   - Aspecto de queijo (friável, esbranquiçado)\n"
                        "   - Exemplo: Tuberculose\n\n"
                        "4. Necrose GORDUROSA:\n"
                        "   - Saponificação de gordura por lipases\n"
                        "   - Exemplo: Pancreatite aguda\n\n"
                        "5. Necrose FIBRINOIDE:\n"
                        "   - Depósito de fibrina em parede vascular\n"
                        "   - Exemplo: Hipertensão maligna, vasculites\n\n"
                        "6. Necrose GANGRENOSA:\n"
                        "   - Combinação de coagulação + liquefação (infecção)\n"
                        "   - Exemplo: Gangrena de membros em diabéticos"
                    )
                }
            ]
            questao = random.choice(opcoes)
            
        elif dificuldade == "medio":
            enunciado = (
                "Sobre inflamação aguda:\n"
                "a) Quais são os sinais cardinais e seus mecanismos?\n"
                "b) Qual a sequência de eventos na resposta inflamatória?\n"
                "c) Cite os principais mediadores químicos."
            )
            resposta = (
                "a) Sinais cardinais (Celsius/Galeno):\n"
                "   1. RUBOR (vermelhidão): vasodilatação arteriolar\n"
                "   2. CALOR: aumento do fluxo sanguíneo + metabolismo\n"
                "   3. TUMOR (edema): aumento da permeabilidade vascular\n"
                "   4. DOR: mediadores + compressão nervosa pelo edema\n"
                "   5. PERDA DE FUNÇÃO: dor + edema + destruição tecidual\n\n"
                "b) Sequência de eventos:\n"
                "   1. Lesão tecidual → liberação de mediadores\n"
                "   2. Vasodilatação arteriolar (hiperemia ativa)\n"
                "   3. Aumento da permeabilidade vascular → edema\n"
                "   4. Marginação leucocitária (diminuição do fluxo)\n"
                "   5. Rolamento → Adesão → Diapedese\n"
                "   6. Quimiotaxia (migração direcionada)\n"
                "   7. Fagocitose e destruição de agentes\n"
                "   8. Resolução ou cronificação\n\n"
                "c) Mediadores químicos:\n"
                "   PRÉ-FORMADOS:\n"
                "   - Histamina (mastócitos): vasodilatação, permeabilidade\n"
                "   - Serotonina (plaquetas)\n\n"
                "   NEO-FORMADOS:\n"
                "   - Prostaglandinas: dor, febre, vasodilatação\n"
                "   - Leucotrienos: quimiotaxia, permeabilidade\n"
                "   - PAF: agregação plaquetária\n"
                "   - Citocinas (IL-1, TNF-α): febre, resposta sistêmica\n"
                "   - Óxido nítrico: vasodilatação\n"
                "   - Complemento (C3a, C5a): quimiotaxia, opsonização"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            enunciado = (
                "Paciente de 55 anos com edema de MMII bilateral, ascite e hepatomegalia.\n\n"
                "a) Diferencie edema por insuficiência cardíaca de cirrose hepática.\n"
                "b) Explique a fisiopatologia do edema em cada caso.\n"
                "c) Qual o papel do sistema renina-angiotensina-aldosterona?\n"
                "d) Por que a hipoalbuminemia causa edema?"
            )
            resposta = (
                "a) Diferenciação clínica:\n"
                "   INSUFICIÊNCIA CARDÍACA:\n"
                "   - Turgência jugular\n"
                "   - Refluxo hepatojugular\n"
                "   - B3/B4, sopros, cardiomegalia\n"
                "   - Dispneia, ortopneia\n"
                "   - Edema mais em MMII (gravitacional)\n\n"
                "   CIRROSE HEPÁTICA:\n"
                "   - Estigmas hepáticos (aranhas vasculares, eritema palmar)\n"
                "   - Circulação colateral (cabeça de medusa)\n"
                "   - Esplenomegalia\n"
                "   - Ascite predominante (maior que edema periférico)\n"
                "   - Ginecomastia, atrofia testicular\n\n"
                "b) Fisiopatologia:\n"
                "   IC (edema por CONGESTÃO):\n"
                "   - ↑ Pressão venosa central → transmissão retrógrada\n"
                "   - ↑ Pressão hidrostática capilar\n"
                "   - Transudação de líquido para interstício\n\n"
                "   CIRROSE (edema por HIPERTENSÃO PORTAL + HIPOALBUMINEMIA):\n"
                "   - Hipertensão portal → ↑ pressão sinusoidal\n"
                "   - ↓ Síntese de albumina → ↓ pressão oncótica\n"
                "   - Vasodilatação esplâncnica → hipovolemia efetiva\n\n"
                "c) Papel do SRAA (comum a ambos):\n"
                "   - Baixo débito (IC) ou hipovolemia efetiva (cirrose)\n"
                "   - Ativa barorreceptores → ativa SRAA\n"
                "   - Angiotensina II: vasoconstrição, sede\n"
                "   - Aldosterona: retenção de Na⁺ e água\n"
                "   - ADH: retenção de água\n"
                "   - Resulta em expansão de volume → piora edema\n\n"
                "d) Hipoalbuminemia e edema:\n"
                "   - Albumina é principal proteína plasmática (60%)\n"
                "   - Responsável por 80% da pressão oncótica\n"
                "   - ↓ Albumina → ↓ pressão oncótica plasmática\n"
                "   - Favorece saída de líquido para interstício\n"
                "   - Equação de Starling: Filtração ∝ (Pc - Pi) - (πc - πi)\n"
                "   - ↓ πc (pressão oncótica capilar) → maior filtração"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("patologia")
        return {
            **questao,
            "tipo": "Patologia Geral",
            "materia": "patologia",
            "dificuldade": dificuldade
        }

    def gerar_questao_neoplasias(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre neoplasias."""
        
        if dificuldade == "facil":
            enunciado = "Diferencie neoplasia benigna de maligna."
            resposta = (
                "NEOPLASIA BENIGNA:\n"
                "- Crescimento lento\n"
                "- Bem diferenciada (semelhante ao tecido de origem)\n"
                "- Bem delimitada, encapsulada\n"
                "- Crescimento expansivo\n"
                "- NÃO invade tecidos adjacentes\n"
                "- NÃO dá metástases\n"
                "- Raramente recidiva após remoção\n"
                "- Nomenclatura: sufixo -OMA (adenoma, lipoma)\n\n"
                "NEOPLASIA MALIGNA:\n"
                "- Crescimento rápido\n"
                "- Pouco diferenciada ou indiferenciada (anaplasia)\n"
                "- Mal delimitada, sem cápsula\n"
                "- Crescimento infiltrativo\n"
                "- Invade tecidos adjacentes\n"
                "- DÁ METÁSTASES\n"
                "- Alta taxa de recidiva\n"
                "- Nomenclatura: CARCINOMA (epitelial), SARCOMA (mesenquimal)"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        elif dificuldade == "medio":
            enunciado = (
                "Sobre carcinogênese:\n"
                "a) Quais são as etapas da carcinogênese?\n"
                "b) Diferencie oncogenes de genes supressores de tumor.\n"
                "c) Cite exemplos de cada e as neoplasias associadas."
            )
            resposta = (
                "a) Etapas da carcinogênese:\n"
                "   1. INICIAÇÃO:\n"
                "      - Mutação do DNA (irreversível)\n"
                "      - Exposição ao carcinógeno\n"
                "      - Célula iniciada (latente)\n\n"
                "   2. PROMOÇÃO:\n"
                "      - Expansão clonal das células iniciadas\n"
                "      - Agentes promotores (não mutagênicos)\n"
                "      - Reversível inicialmente\n\n"
                "   3. PROGRESSÃO:\n"
                "      - Acúmulo de mutações adicionais\n"
                "      - Instabilidade genômica\n"
                "      - Aquisição de fenótipo maligno\n"
                "      - Invasão e metástase\n\n"
                "b) Oncogenes vs Supressores:\n"
                "   ONCOGENES (aceleradores):\n"
                "   - Derivados de proto-oncogenes normais\n"
                "   - Mutação ATIVADORA (ganho de função)\n"
                "   - Dominantes (basta 1 alelo mutado)\n"
                "   - Promovem proliferação\n\n"
                "   GENES SUPRESSORES (freios):\n"
                "   - Normalmente inibem proliferação\n"
                "   - Mutação INATIVADORA (perda de função)\n"
                "   - Recessivos (precisam perder os 2 alelos)\n"
                "   - 'Hipótese dos dois hits' (Knudson)\n\n"
                "c) Exemplos:\n"
                "   ONCOGENES:\n"
                "   - RAS: pâncreas, cólon, pulmão (30% dos tumores)\n"
                "   - MYC: linfoma de Burkitt\n"
                "   - HER2/neu: mama\n"
                "   - BCR-ABL: LMC (cromossomo Philadelphia)\n\n"
                "   SUPRESSORES:\n"
                "   - p53: 'guardião do genoma' - maioria dos tumores\n"
                "   - RB: retinoblastoma\n"
                "   - APC: câncer colorretal familiar\n"
                "   - BRCA1/2: mama e ovário hereditários"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            enunciado = (
                "Paciente de 65 anos com nódulo pulmonar e emagrecimento.\n"
                "Biópsia revela carcinoma de células escamosas.\n\n"
                "a) Quais as vias de metástase e qual a mais provável para este tumor?\n"
                "b) Quais os sítios mais comuns de metástase de câncer de pulmão?\n"
                "c) O que são síndromes paraneoplásicas? Cite exemplos associadas ao CA de pulmão.\n"
                "d) Diferencie carcinoma de pequenas células de não pequenas células."
            )
            resposta = (
                "a) Vias de metástase:\n"
                "   1. HEMATOGÊNICA (venosa): mais comum em sarcomas e carcinomas\n"
                "      - Tumores drenam para veias → coração → disseminação\n"
                "   2. LINFÁTICA: comum em carcinomas\n"
                "      - Via inicial de disseminação de muitos carcinomas\n"
                "   3. IMPLANTE (cavidades): peritoneal, pleural, pericárdica\n"
                "   4. PERINEURAL: adenocarcinoma de pâncreas, CA próstata\n\n"
                "   Para CA escamoso de pulmão:\n"
                "   - Via linfática (linfonodos hilares, mediastinais) + hematogênica\n\n"
                "b) Sítios de metástase do CA pulmão:\n"
                "   - Linfonodos regionais (hilares, mediastinais)\n"
                "   - Fígado\n"
                "   - Osso (osteolíticas, dor, fraturas)\n"
                "   - Cérebro (convulsões, déficits focais)\n"
                "   - Adrenais\n"
                "   - Pulmão contralateral\n\n"
                "c) Síndromes paraneoplásicas:\n"
                "   Definição: manifestações à distância não causadas por metástases\n"
                "   Exemplos em CA pulmão:\n"
                "   - SIADH: hiponatremia (pequenas células)\n"
                "   - Cushing ectópico: ACTH ectópico (pequenas células)\n"
                "   - Hipercalcemia: PTHrP (escamoso)\n"
                "   - Síndrome de Eaton-Lambert: fraqueza muscular (pequenas células)\n"
                "   - Osteoartropatia hipertrófica: baqueteamento digital\n\n"
                "d) Pequenas células vs Não pequenas células:\n"
                "   CARCINOMA DE PEQUENAS CÉLULAS (CPPC - 15%):\n"
                "   - Origem neuroendócrina\n"
                "   - Altamente agressivo, metástases precoces\n"
                "   - Localização central (hilares)\n"
                "   - Forte associação com tabagismo\n"
                "   - Síndromes paraneoplásicas comuns\n"
                "   - Tratamento: QT + RT (raramente cirúrgico)\n\n"
                "   CARCINOMA NÃO PEQUENAS CÉLULAS (CPNPC - 85%):\n"
                "   - Adenocarcinoma (mais comum, periférico)\n"
                "   - Escamoso (central, cavita)\n"
                "   - Grandes células\n"
                "   - Crescimento mais lento\n"
                "   - Tratamento: cirurgia (se ressecável) + QT ± RT"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("patologia")
        return {
            **questao,
            "tipo": "Neoplasias",
            "materia": "patologia",
            "dificuldade": dificuldade
        }

    def gerar_questao(self, topico: str = "geral", dificuldade: str = "medio", observacoes: str = "") -> dict:
        """Gera uma questão de patologia baseada no tópico e dificuldade."""
        topico_lower = topico.lower().replace(" ", "_")
        
        mapeamento = {
            "geral": self.gerar_questao_patologia_geral,
            "necrose": self.gerar_questao_patologia_geral,
            "inflamacao": self.gerar_questao_patologia_geral,
            "edema": self.gerar_questao_patologia_geral,
            "neoplasia": self.gerar_questao_neoplasias,
            "cancer": self.gerar_questao_neoplasias,
            "tumor": self.gerar_questao_neoplasias,
            "oncologia": self.gerar_questao_neoplasias,
        }
        
        if topico_lower in mapeamento:
            questao = mapeamento[topico_lower](dificuldade)
        else:
            metodo = random.choice([
                self.gerar_questao_patologia_geral,
                self.gerar_questao_neoplasias
            ])
            questao = metodo(dificuldade)
        
        if observacoes:
            questao["observacoes_professor"] = observacoes
        
        return questao

