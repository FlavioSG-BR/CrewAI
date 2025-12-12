# -*- coding: utf-8 -*-
"""
Agente especializado em Farmacologia.
Gera questões sobre farmacocinética, farmacodinâmica, classes de medicamentos,
interações medicamentosas e casos clínicos com prescrição.
"""

import random
from crewai import Agent
from backend.utils.logger import log_questao_gerada


class AgenteFarmacologia:
    """Agente especializado em questões de Farmacologia."""
    
    def __init__(self):
        self.agent = Agent(
            role="Professor de Farmacologia",
            goal="Criar questões sobre mecanismos de ação, indicações, efeitos adversos e interações medicamentosas",
            backstory="Farmacologista com doutorado e 15 anos de experiência em ensino médico, especialista em farmacologia clínica.",
            verbose=False,
            allow_delegation=False
        )
        
        # Base de dados de fármacos por classe
        self.farmacos = {
            "antibioticos": {
                "beta_lactamicos": {
                    "penicilinas": ["Amoxicilina", "Ampicilina", "Penicilina G", "Oxacilina", "Piperacilina"],
                    "cefalosporinas": {
                        "1a_geracao": ["Cefalexina", "Cefazolina"],
                        "2a_geracao": ["Cefuroxima", "Cefaclor"],
                        "3a_geracao": ["Ceftriaxona", "Ceftazidima", "Cefotaxima"],
                        "4a_geracao": ["Cefepime"],
                        "5a_geracao": ["Ceftarolina", "Ceftobiprole"]
                    },
                    "carbapenemicos": ["Imipenem", "Meropenem", "Ertapenem"],
                    "mecanismo": "Inibição da síntese da parede celular bacteriana (ligação às PBPs)",
                    "resistencia": "Produção de beta-lactamases, alteração de PBPs, redução de porinas"
                },
                "aminoglicosideos": {
                    "farmacos": ["Gentamicina", "Amicacina", "Estreptomicina", "Tobramicina", "Neomicina"],
                    "mecanismo": "Inibição da síntese proteica (ligação à subunidade 30S ribossomal)",
                    "toxicidade": ["Nefrotoxicidade", "Ototoxicidade (vestibular e coclear)"],
                    "espectro": "Gram-negativos aeróbios"
                },
                "quinolonas": {
                    "farmacos": ["Ciprofloxacino", "Levofloxacino", "Moxifloxacino", "Norfloxacino"],
                    "mecanismo": "Inibição da DNA girase e topoisomerase IV",
                    "efeitos_adversos": ["Tendinite/ruptura tendínea", "Prolongamento QT", "Fotossensibilidade"]
                },
                "macrolideos": {
                    "farmacos": ["Azitromicina", "Claritromicina", "Eritromicina"],
                    "mecanismo": "Inibição da síntese proteica (ligação à subunidade 50S ribossomal)",
                    "usos": ["Pneumonias atípicas", "Infecções por Chlamydia", "Coqueluche"]
                },
                "glicopeptideos": {
                    "farmacos": ["Vancomicina", "Teicoplanina"],
                    "mecanismo": "Inibição da síntese da parede celular (ligação ao D-Ala-D-Ala)",
                    "usos": ["MRSA", "Colite pseudomembranosa (Vancomicina oral)"]
                }
            },
            "anti_inflamatorios": {
                "aines": {
                    "nao_seletivos": ["Ibuprofeno", "Naproxeno", "Diclofenaco", "Piroxicam", "AAS"],
                    "cox2_seletivos": ["Celecoxibe", "Etoricoxibe"],
                    "mecanismo": "Inibição da cicloxigenase (COX-1 e/ou COX-2)",
                    "efeitos_adversos": ["Gastropatia", "Nefrotoxicidade", "Risco cardiovascular (COX-2)"]
                },
                "corticoides": {
                    "farmacos": ["Prednisona", "Prednisolona", "Dexametasona", "Hidrocortisona", "Metilprednisolona"],
                    "mecanismo": "Inibição de fosfolipase A2 (via lipocortina), redução de citocinas",
                    "efeitos_adversos": ["Supressão adrenal", "Osteoporose", "Hiperglicemia", "Cushing iatrogênico"]
                }
            },
            "cardiovasculares": {
                "anti_hipertensivos": {
                    "ieca": {
                        "farmacos": ["Captopril", "Enalapril", "Lisinopril", "Ramipril", "Perindopril"],
                        "mecanismo": "Inibição da ECA, redução de Angiotensina II",
                        "efeitos_adversos": ["Tosse seca", "Angioedema", "Hipercalemia"]
                    },
                    "bra": {
                        "farmacos": ["Losartana", "Valsartana", "Candesartana", "Olmesartana", "Telmisartana"],
                        "mecanismo": "Bloqueio do receptor AT1 da Angiotensina II",
                        "vantagem": "Não causa tosse (não afeta bradicinina)"
                    },
                    "bcc": {
                        "diidropiridinicos": ["Anlodipino", "Nifedipino", "Felodipino"],
                        "nao_diidropiridinicos": ["Verapamil", "Diltiazem"],
                        "mecanismo": "Bloqueio de canais de cálcio tipo L"
                    },
                    "diureticos": {
                        "tiazidicos": ["Hidroclorotiazida", "Clortalidona", "Indapamida"],
                        "alca": ["Furosemida", "Bumetanida"],
                        "poupadores_k": ["Espironolactona", "Amilorida"]
                    },
                    "beta_bloqueadores": {
                        "nao_seletivos": ["Propranolol", "Nadolol", "Carvedilol"],
                        "b1_seletivos": ["Atenolol", "Metoprolol", "Bisoprolol", "Nebivolol"],
                        "contraindicacoes": ["Asma", "DPOC grave", "Bradicardia", "BAV 2º/3º grau"]
                    }
                }
            },
            "snc": {
                "ansioliticos": {
                    "benzodiazepinicos": {
                        "farmacos": ["Diazepam", "Alprazolam", "Clonazepam", "Lorazepam", "Midazolam"],
                        "mecanismo": "Potencialização do GABA (moduladores alostéricos do receptor GABA-A)",
                        "efeitos_adversos": ["Sedação", "Dependência", "Amnésia anterógrada"]
                    }
                },
                "antidepressivos": {
                    "isrs": {
                        "farmacos": ["Fluoxetina", "Sertralina", "Paroxetina", "Citalopram", "Escitalopram"],
                        "mecanismo": "Inibição seletiva da recaptação de serotonina"
                    },
                    "irsn": {
                        "farmacos": ["Venlafaxina", "Duloxetina", "Desvenlafaxina"],
                        "mecanismo": "Inibição da recaptação de serotonina e noradrenalina"
                    },
                    "triciclicos": {
                        "farmacos": ["Amitriptilina", "Nortriptilina", "Imipramina", "Clomipramina"],
                        "efeitos_adversos": ["Anticolinérgicos", "Cardiotoxicidade", "Ganho de peso"]
                    }
                },
                "antipsicoticos": {
                    "tipicos": ["Haloperidol", "Clorpromazina", "Flufenazina"],
                    "atipicos": ["Risperidona", "Quetiapina", "Olanzapina", "Clozapina", "Aripiprazol"],
                    "mecanismo": "Bloqueio de receptores D2 dopaminérgicos"
                },
                "antiepilepticos": {
                    "farmacos": ["Carbamazepina", "Fenitoína", "Valproato", "Lamotrigina", "Levetiracetam"],
                    "mecanismos": {
                        "canais_sodio": ["Carbamazepina", "Fenitoína", "Lamotrigina"],
                        "gaba": ["Valproato", "Benzodiazepínicos", "Fenobarbital"],
                        "outros": ["Levetiracetam (SV2A)", "Gabapentina (canais Ca)"]
                    }
                }
            },
            "analgesicos": {
                "opioides": {
                    "fracos": ["Tramadol", "Codeína"],
                    "fortes": ["Morfina", "Fentanil", "Metadona", "Oxicodona"],
                    "mecanismo": "Agonistas de receptores opioides (mu, kappa, delta)",
                    "antagonista": "Naloxona",
                    "efeitos_adversos": ["Depressão respiratória", "Constipação", "Náusea", "Tolerância/Dependência"]
                }
            },
            "endocrinos": {
                "antidiabeticos": {
                    "insulinas": {
                        "ultra_rapida": ["Lispro", "Aspart", "Glulisina"],
                        "rapida": ["Regular"],
                        "intermediaria": ["NPH"],
                        "longa": ["Glargina", "Detemir", "Degludeca"]
                    },
                    "orais": {
                        "metformina": {
                            "mecanismo": "Redução da gliconeogênese hepática, aumento da sensibilidade à insulina",
                            "contraindicacao": "Insuficiência renal (risco de acidose lática)"
                        },
                        "sulfonilureias": {
                            "farmacos": ["Glibenclamida", "Glimepirida", "Gliclazida"],
                            "mecanismo": "Fechamento de canais K-ATP, liberação de insulina"
                        },
                        "inibidores_sglt2": {
                            "farmacos": ["Dapagliflozina", "Empagliflozina", "Canagliflozina"],
                            "mecanismo": "Inibição do cotransportador sódio-glicose 2 no rim"
                        },
                        "inibidores_dpp4": {
                            "farmacos": ["Sitagliptina", "Vildagliptina", "Saxagliptina"],
                            "mecanismo": "Inibição da DPP-4, aumento de incretinas (GLP-1)"
                        }
                    }
                },
                "tireoidianos": {
                    "hipotireoidismo": ["Levotiroxina (T4)"],
                    "hipertireoidismo": {
                        "antitireoidianos": ["Metimazol", "Propiltiouracil"],
                        "mecanismo": "Inibição da peroxidase tireoidiana"
                    }
                }
            }
        }
        
        # Interações medicamentosas importantes
        self.interacoes = [
            {
                "farmacos": ["Varfarina", "AAS"],
                "efeito": "Aumento do risco de sangramento",
                "mecanismo": "Deslocamento da ligação proteica + inibição plaquetária"
            },
            {
                "farmacos": ["IECA", "Espironolactona"],
                "efeito": "Hipercalemia grave",
                "mecanismo": "Ambos reduzem a excreção de potássio"
            },
            {
                "farmacos": ["Metformina", "Contraste iodado"],
                "efeito": "Acidose lática",
                "conduta": "Suspender metformina 48h antes e após o exame"
            },
            {
                "farmacos": ["ISRS", "IMAO"],
                "efeito": "Síndrome serotoninérgica",
                "sintomas": "Hipertermia, rigidez, convulsões, coma"
            },
            {
                "farmacos": ["Quinolonas", "Antiácidos (Al/Mg)"],
                "efeito": "Redução da absorção da quinolona",
                "mecanismo": "Quelação por cátions divalentes"
            },
            {
                "farmacos": ["Aminoglicosídeos", "Furosemida"],
                "efeito": "Potencialização da ototoxicidade",
                "cuidado": "Monitorar função auditiva"
            },
            {
                "farmacos": ["Digoxina", "Amiodarona"],
                "efeito": "Aumento dos níveis de digoxina (toxicidade)",
                "conduta": "Reduzir dose de digoxina em 50%"
            },
            {
                "farmacos": ["Carbamazepina", "Anticoncepcionais orais"],
                "efeito": "Redução da eficácia contraceptiva",
                "mecanismo": "Indução enzimática (CYP3A4)"
            }
        ]

    def gerar_questao_farmacocinetica(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre farmacocinética (ADME)."""
        
        if dificuldade == "facil":
            conceitos = [
                {
                    "enunciado": "Qual a diferença entre biodisponibilidade e meia-vida de um fármaco?",
                    "resposta": "Biodisponibilidade é a fração do fármaco administrado que atinge a circulação sistêmica de forma inalterada. Meia-vida (t1/2) é o tempo necessário para a concentração plasmática do fármaco reduzir à metade."
                },
                {
                    "enunciado": "O que é o efeito de primeira passagem hepática e qual sua importância clínica?",
                    "resposta": "É a metabolização do fármaco pelo fígado antes de atingir a circulação sistêmica, após absorção intestinal. Reduz a biodisponibilidade de fármacos administrados por via oral. Exemplo: morfina oral tem biodisponibilidade de ~30% devido ao intenso metabolismo de primeira passagem."
                },
                {
                    "enunciado": "Por que a via intravenosa tem biodisponibilidade de 100%?",
                    "resposta": "Porque o fármaco é administrado diretamente na corrente sanguínea, sem passar por processos de absorção ou metabolismo pré-sistêmico."
                }
            ]
            questao = random.choice(conceitos)
            
        elif dificuldade == "medio":
            # Questões de cálculo ou conceitos intermediários
            vd_valores = [50, 70, 100, 150, 200]
            dose = random.choice([500, 700, 1000])
            vd = random.choice(vd_valores)
            cp = dose / vd
            
            enunciado = (
                f"Um paciente recebeu {dose} mg de um fármaco por via intravenosa. "
                f"Sabendo que o volume de distribuição (Vd) desse fármaco é {vd} L, "
                f"calcule a concentração plasmática inicial (Cp0) do fármaco."
            )
            resposta = (
                f"Cp0 = Dose / Vd\n"
                f"Cp0 = {dose} mg / {vd} L\n"
                f"Cp0 = {cp:.2f} mg/L ou {cp:.2f} µg/mL"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            t_meias = [2, 4, 6, 8]
            t_meia = random.choice(t_meias)
            tempo = t_meia * random.choice([2, 3, 4])
            n_meias = tempo / t_meia
            cp_inicial = random.choice([100, 200, 400])
            cp_final = cp_inicial / (2 ** n_meias)
            
            enunciado = (
                f"Um fármaco com meia-vida de {t_meia} horas foi administrado por via IV em bolus. "
                f"A concentração plasmática inicial foi de {cp_inicial} mg/L. "
                f"Qual será a concentração plasmática após {tempo} horas? "
                f"Quanto tempo será necessário para eliminar 97% do fármaco do organismo?"
            )
            resposta = (
                f"1) Concentração após {tempo}h:\n"
                f"   - Número de meias-vidas = {tempo}/{t_meia} = {int(n_meias)}\n"
                f"   - Cp = Cp0 × (0.5)^n = {cp_inicial} × (0.5)^{int(n_meias)} = {cp_final:.2f} mg/L\n\n"
                f"2) Tempo para eliminar 97% (restar 3%):\n"
                f"   - São necessárias aproximadamente 5 meias-vidas para eliminar ~97% do fármaco\n"
                f"   - Tempo = 5 × {t_meia}h = {5 * t_meia} horas"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("farmacologia")
        return {
            **questao,
            "tipo": "Farmacocinética",
            "materia": "farmacologia",
            "dificuldade": dificuldade
        }

    def gerar_questao_farmacodinamica(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre farmacodinâmica."""
        
        if dificuldade == "facil":
            conceitos = [
                {
                    "enunciado": "Diferencie agonista total, agonista parcial e antagonista.",
                    "resposta": "Agonista total: liga-se ao receptor e produz resposta máxima (eficácia = 1). Agonista parcial: liga-se ao receptor mas produz resposta submáxima mesmo com ocupação total dos receptores (eficácia < 1). Antagonista: liga-se ao receptor mas não produz resposta intrínseca (eficácia = 0), bloqueando a ação de agonistas."
                },
                {
                    "enunciado": "O que significa dizer que um fármaco tem alta potência?",
                    "resposta": "Um fármaco com alta potência produz o efeito desejado em baixas doses (baixo EC50). Potência está relacionada à afinidade pelo receptor. Um fármaco pode ser muito potente mas ter baixa eficácia, e vice-versa."
                }
            ]
            questao = random.choice(conceitos)
            
        elif dificuldade == "medio":
            enunciado = (
                "Um paciente em uso crônico de morfina para dor oncológica relata que a dose habitual "
                "já não está controlando adequadamente a dor. O médico aumenta a dose e o paciente "
                "melhora novamente.\n\n"
                "a) Qual fenômeno farmacodinâmico está ocorrendo?\n"
                "b) Explique o mecanismo molecular envolvido.\n"
                "c) Se o paciente parar abruptamente a morfina, o que pode ocorrer?"
            )
            resposta = (
                "a) Tolerância farmacológica.\n\n"
                "b) Mecanismos de tolerância aos opioides:\n"
                "   - Dessensibilização de receptores (downregulation de receptores mu)\n"
                "   - Desacoplamento do receptor da proteína G\n"
                "   - Internalização de receptores\n"
                "   - Ativação de sistemas anti-opioides (NMDA, dinorfinas)\n\n"
                "c) Síndrome de abstinência: diarreia, lacrimejamento, rinorreia, piloereção, "
                "sudorese, midríase, cólicas abdominais, insônia, ansiedade. Ocorre devido à "
                "hiperatividade do sistema nervoso simpático após remoção da inibição opioide."
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            enunciado = (
                "Analise o gráfico dose-resposta abaixo (considere hipoteticamente):\n"
                "- Fármaco A: EC50 = 10 nM, Emax = 100%\n"
                "- Fármaco B: EC50 = 100 nM, Emax = 100%\n"
                "- Fármaco C: EC50 = 5 nM, Emax = 50%\n\n"
                "a) Qual fármaco é mais potente?\n"
                "b) Qual fármaco é provavelmente um agonista parcial?\n"
                "c) Se administrarmos C junto com A, qual o efeito esperado?\n"
                "d) Explique o conceito de antagonismo competitivo usando A e B."
            )
            resposta = (
                "a) Fármaco C é mais potente (menor EC50 = 5 nM), seguido de A (10 nM) e B (100 nM).\n\n"
                "b) Fármaco C é um agonista parcial, pois tem Emax de apenas 50%.\n\n"
                "c) C atuará como antagonista parcial de A:\n"
                "   - Se A estiver produzindo 100% de resposta, a adição de C competirá pelos receptores\n"
                "   - Como C tem maior afinidade (menor EC50) mas menor eficácia, a resposta diminuirá\n"
                "   - O efeito final será entre 50-100%, dependendo das concentrações\n\n"
                "d) Antagonismo competitivo:\n"
                "   - Um antagonista competitivo se liga ao mesmo sítio do agonista\n"
                "   - Desloca a curva do agonista para a direita (aumenta EC50)\n"
                "   - Não altera o Emax (pode ser superado aumentando a dose do agonista)\n"
                "   - Exemplo: se um antagonista competitivo estiver presente, A precisará de "
                "concentrações maiores para atingir o mesmo efeito"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("farmacologia")
        return {
            **questao,
            "tipo": "Farmacodinâmica",
            "materia": "farmacologia",
            "dificuldade": dificuldade
        }

    def gerar_questao_antibioticos(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre antibióticos."""
        
        if dificuldade == "facil":
            classe = random.choice(["beta_lactamicos", "aminoglicosideos", "quinolonas", "macrolideos"])
            
            if classe == "beta_lactamicos":
                enunciado = "Qual o mecanismo de ação dos antibióticos beta-lactâmicos e cite 3 exemplos."
                resposta = (
                    "Mecanismo: Inibição da síntese da parede celular bacteriana através da ligação "
                    "às proteínas ligadoras de penicilina (PBPs), enzimas que catalisam a transpeptidação "
                    "na síntese do peptidoglicano.\n\n"
                    "Exemplos: Amoxicilina, Ampicilina, Ceftriaxona, Penicilina G, Meropenem."
                )
            elif classe == "aminoglicosideos":
                enunciado = "Quais são as principais toxicidades dos aminoglicosídeos e qual antibiótico é um exemplo dessa classe?"
                resposta = (
                    "Toxicidades:\n"
                    "1. Nefrotoxicidade: dano tubular renal, geralmente reversível\n"
                    "2. Ototoxicidade: pode ser vestibular (vertigem) ou coclear (surdez), frequentemente irreversível\n"
                    "3. Bloqueio neuromuscular (raro)\n\n"
                    "Exemplos: Gentamicina, Amicacina, Estreptomicina, Tobramicina."
                )
            elif classe == "quinolonas":
                enunciado = "Qual o mecanismo de ação das quinolonas e cite um efeito adverso característico dessa classe."
                resposta = (
                    "Mecanismo: Inibição da DNA girase (topoisomerase II) e topoisomerase IV bacterianas, "
                    "enzimas essenciais para replicação, transcrição e reparo do DNA bacteriano.\n\n"
                    "Efeitos adversos característicos:\n"
                    "- Tendinite e ruptura tendínea (especialmente tendão de Aquiles)\n"
                    "- Prolongamento do intervalo QT\n"
                    "- Fotossensibilidade"
                )
            else:  # macrolideos
                enunciado = "Qual o mecanismo de ação dos macrolídeos e para quais infecções são particularmente úteis?"
                resposta = (
                    "Mecanismo: Ligação à subunidade 50S do ribossomo bacteriano, inibindo a "
                    "síntese proteica (fase de translocação).\n\n"
                    "Indicações principais:\n"
                    "- Pneumonias atípicas (Mycoplasma, Legionella, Chlamydia)\n"
                    "- Infecções por Chlamydia trachomatis\n"
                    "- Coqueluche (Bordetella pertussis)\n"
                    "- Alternativa em alérgicos a penicilina"
                )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        elif dificuldade == "medio":
            enunciado = (
                "Paciente de 65 anos, internado com pneumonia adquirida na comunidade grave, "
                "está em uso de ceftriaxona + azitromicina. Após 5 dias, evolui com piora clínica "
                "e a cultura de escarro revela Pseudomonas aeruginosa resistente a cefalosporinas "
                "de 3ª geração.\n\n"
                "a) Por que a ceftriaxona não foi eficaz contra Pseudomonas?\n"
                "b) Cite duas opções de antibióticos com ação antipseudomonas.\n"
                "c) Qual a importância de associar um aminoglicosídeo neste caso?"
            )
            resposta = (
                "a) A ceftriaxona (cefalosporina de 3ª geração) tem pouca atividade contra "
                "Pseudomonas aeruginosa. A ceftazidima é a cefalosporina de 3ª geração com "
                "melhor ação antipseudomonas. Além disso, Pseudomonas possui mecanismos de "
                "resistência como bombas de efluxo, alteração de porinas e beta-lactamases.\n\n"
                "b) Opções antipseudomonas:\n"
                "   - Piperacilina-tazobactam\n"
                "   - Ceftazidima ou Cefepime\n"
                "   - Carbapenêmicos (Meropenem, Imipenem - exceto Ertapenem)\n"
                "   - Ciprofloxacino ou Levofloxacino\n"
                "   - Aminoglicosídeos (Amicacina, Gentamicina)\n\n"
                "c) A associação com aminoglicosídeo:\n"
                "   - Proporciona sinergismo (mecanismos de ação diferentes)\n"
                "   - Amplia espectro e reduz emergência de resistência\n"
                "   - Aminoglicosídeos têm excelente ação contra Gram-negativos aeróbios"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            enunciado = (
                "Paciente de 72 anos, diabético, é admitido com infecção de pele e partes moles "
                "em membro inferior. A cultura revela Staphylococcus aureus resistente à meticilina (MRSA). "
                "O paciente tem ClCr = 30 mL/min.\n\n"
                "a) Explique o mecanismo de resistência do MRSA aos beta-lactâmicos.\n"
                "b) Qual antibiótico é primeira escolha para MRSA e por quê?\n"
                "c) Como ajustar a dose deste antibiótico para a função renal do paciente?\n"
                "d) Que parâmetro deve ser monitorado e qual o alvo terapêutico?"
            )
            resposta = (
                "a) Mecanismo de resistência do MRSA:\n"
                "   - Aquisição do gene mecA (cassete SCCmec)\n"
                "   - Codifica a PBP2a (PBP alterada) com baixa afinidade por beta-lactâmicos\n"
                "   - A parede celular continua sendo sintetizada mesmo na presença do antibiótico\n"
                "   - Confere resistência a TODOS os beta-lactâmicos\n\n"
                "b) Vancomicina é primeira escolha:\n"
                "   - Glicopeptídeo que inibe síntese da parede por mecanismo diferente\n"
                "   - Liga-se ao dipeptídeo D-Ala-D-Ala, não às PBPs\n"
                "   - MRSA permanece sensível na maioria dos casos\n\n"
                "c) Ajuste para ClCr = 30 mL/min:\n"
                "   - Vancomicina é eliminada por via renal\n"
                "   - Dose inicial: 15-20 mg/kg (ataque)\n"
                "   - Manutenção: 15 mg/kg a cada 24-48h (ao invés de 12h)\n"
                "   - Ou ajustar conforme nível sérico (vancocinemia)\n\n"
                "d) Monitoramento:\n"
                "   - Parâmetro: Vancocinemia (nível sérico de vale)\n"
                "   - Alvo terapêutico: 15-20 µg/mL para infecções graves\n"
                "   - Também monitorar: função renal, hemograma\n"
                "   - Risco: nefrotoxicidade (especialmente se associado a aminoglicosídeos)"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("farmacologia")
        return {
            **questao,
            "tipo": "Antibióticos",
            "materia": "farmacologia",
            "dificuldade": dificuldade
        }

    def gerar_questao_cardiovascular(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre fármacos cardiovasculares."""
        
        if dificuldade == "facil":
            opcoes = [
                {
                    "enunciado": "Qual o mecanismo de ação dos IECA e cite dois efeitos adversos.",
                    "resposta": (
                        "Mecanismo: Inibição da Enzima Conversora de Angiotensina (ECA), que:\n"
                        "- Impede conversão de Angiotensina I em Angiotensina II\n"
                        "- Reduz vasoconstrição e secreção de aldosterona\n"
                        "- Impede degradação da bradicinina (vasodilatador)\n\n"
                        "Efeitos adversos:\n"
                        "1. Tosse seca (10-15%) - por acúmulo de bradicinina\n"
                        "2. Angioedema (raro, mas grave)\n"
                        "3. Hipercalemia\n"
                        "4. Hipotensão (primeira dose)\n"
                        "5. Insuficiência renal aguda (em estenose bilateral de artéria renal)"
                    )
                },
                {
                    "enunciado": "Diferencie os diuréticos tiazídicos dos diuréticos de alça quanto ao local de ação e potência.",
                    "resposta": (
                        "Diuréticos tiazídicos (ex: Hidroclorotiazida):\n"
                        "- Local: Túbulo contorcido distal\n"
                        "- Mecanismo: Inibição do cotransportador Na-Cl\n"
                        "- Potência: Moderada (excretam 5-10% do Na filtrado)\n"
                        "- Uso: Hipertensão, ICC leve\n\n"
                        "Diuréticos de alça (ex: Furosemida):\n"
                        "- Local: Alça de Henle ascendente espessa\n"
                        "- Mecanismo: Inibição do cotransportador Na-K-2Cl\n"
                        "- Potência: Alta (excretam até 25% do Na filtrado)\n"
                        "- Uso: Edema agudo de pulmão, ICC, edema refratário"
                    )
                }
            ]
            questao = random.choice(opcoes)
            
        elif dificuldade == "medio":
            enunciado = (
                "Paciente hipertenso, 58 anos, diabético tipo 2, com microalbuminúria, está em uso de "
                "Losartana 50mg/dia. A pressão arterial continua 150x95 mmHg.\n\n"
                "a) Por que o BRA é uma boa escolha para este paciente?\n"
                "b) Qual classe de anti-hipertensivo você adicionaria e por quê?\n"
                "c) Cite uma classe que deve ser evitada como monoterapia inicial."
            )
            resposta = (
                "a) Benefícios do BRA neste paciente:\n"
                "   - Nefroproteção: reduz progressão da nefropatia diabética\n"
                "   - Reduz microalbuminúria (efeito direto na hemodinâmica glomerular)\n"
                "   - Neutro metabolicamente (não piora glicemia/lipídios)\n"
                "   - Bem tolerado, sem tosse (diferente dos IECA)\n\n"
                "b) Adicionar Bloqueador de Canal de Cálcio (Anlodipino):\n"
                "   - Combinação sinérgica (mecanismos complementares)\n"
                "   - BCC + BRA: uma das combinações mais eficazes\n"
                "   - Anlodipino é neutro metabolicamente\n"
                "   - Alternativa: Tiazídico em dose baixa\n\n"
                "c) Beta-bloqueadores como monoterapia inicial:\n"
                "   - Menos eficazes na redução de eventos CV em hipertensos não complicados\n"
                "   - Podem piorar controle glicêmico e perfil lipídico\n"
                "   - Podem mascarar sintomas de hipoglicemia\n"
                "   - Indicados se: IC, pós-IAM, arritmias, angina"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            enunciado = (
                "Paciente de 68 anos com insuficiência cardíaca com fração de ejeção reduzida (ICFER) "
                "NYHA III, está em uso de: Carvedilol 25mg 2x/dia, Enalapril 10mg 2x/dia, "
                "Furosemida 40mg/dia, Espironolactona 25mg/dia.\n\n"
                "Exames: K+ = 5.8 mEq/L, Cr = 2.1 mg/dL, Na+ = 132 mEq/L.\n\n"
                "a) Explique o mecanismo pelo qual cada um desses medicamentos reduz mortalidade na ICFER.\n"
                "b) Qual medicamento está mais provavelmente causando a hipercalemia?\n"
                "c) Qual nova classe terapêutica poderia substituir o Enalapril com benefício adicional?\n"
                "d) O paciente pode usar AINE para dor articular? Justifique."
            )
            resposta = (
                "a) Mecanismos de redução de mortalidade:\n"
                "   - Carvedilol (beta-bloqueador): bloqueia efeitos tóxicos da ativação simpática crônica, "
                "reverte remodelamento cardíaco, reduz arritmias\n"
                "   - Enalapril (IECA): bloqueia SRAA, reduz pré e pós-carga, reverte remodelamento, "
                "reduz fibrose miocárdica\n"
                "   - Espironolactona: antagonista de aldosterona, reduz fibrose miocárdica, "
                "efeitos independentes da diurese\n"
                "   - Furosemida: não reduz mortalidade, mas alivia sintomas congestivos\n\n"
                "b) Hipercalemia (K+ = 5.8):\n"
                "   - Causas prováveis: IECA + Espironolactona + IR (Cr = 2.1)\n"
                "   - IECA reduz aldosterona → menor excreção de K+\n"
                "   - Espironolactona bloqueia ação da aldosterona → retenção de K+\n"
                "   - Insuficiência renal reduz excreção de K+\n"
                "   - Conduta: reduzir/suspender espironolactona, monitorar potássio\n\n"
                "c) Sacubitril/Valsartana (INRA - Inibidor de Neprilisina e Receptor de Angiotensina):\n"
                "   - Demonstrou superioridade ao Enalapril no estudo PARADIGM-HF\n"
                "   - Inibe neprilisina (aumenta peptídeos natriuréticos)\n"
                "   - Bloqueia receptor AT1\n"
                "   - Reduz mortalidade e internações\n\n"
                "d) AINEs são CONTRAINDICADOS na IC:\n"
                "   - Retenção de sódio e água (antagonizam diuréticos)\n"
                "   - Vasoconstrição renal (pioram função renal)\n"
                "   - Aumentam pré e pós-carga\n"
                "   - Aumentam risco de descompensação e hospitalização\n"
                "   - Alternativa: Paracetamol ou dipirona para analgesia"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("farmacologia")
        return {
            **questao,
            "tipo": "Farmacologia Cardiovascular",
            "materia": "farmacologia",
            "dificuldade": dificuldade
        }

    def gerar_questao_snc(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre fármacos do SNC."""
        
        if dificuldade == "facil":
            opcoes = [
                {
                    "enunciado": "Qual o mecanismo de ação dos benzodiazepínicos e cite 3 indicações clínicas.",
                    "resposta": (
                        "Mecanismo: Moduladores alostéricos positivos do receptor GABA-A.\n"
                        "- Ligam-se a um sítio diferente do GABA no receptor\n"
                        "- Aumentam a frequência de abertura do canal de cloreto\n"
                        "- Potencializam o efeito inibitório do GABA\n\n"
                        "Indicações:\n"
                        "1. Ansiedade (transtorno de ansiedade generalizada, pânico)\n"
                        "2. Insônia\n"
                        "3. Convulsões (status epilepticus, crises agudas)\n"
                        "4. Relaxamento muscular\n"
                        "5. Sedação pré-operatória\n"
                        "6. Síndrome de abstinência alcoólica"
                    )
                },
                {
                    "enunciado": "Qual o mecanismo de ação dos ISRS e por que são primeira escolha no tratamento da depressão?",
                    "resposta": (
                        "Mecanismo: Inibição seletiva da recaptação de serotonina (5-HT) na fenda sináptica.\n"
                        "- Bloqueiam o transportador de serotonina (SERT)\n"
                        "- Aumentam disponibilidade de serotonina\n\n"
                        "Por que são primeira escolha:\n"
                        "1. Eficácia comparável aos tricíclicos\n"
                        "2. Melhor perfil de segurança (menos efeitos anticolinérgicos)\n"
                        "3. Menor toxicidade em overdose\n"
                        "4. Menos efeitos cardiovasculares\n"
                        "5. Dose única diária (melhor adesão)\n"
                        "6. Úteis também para ansiedade, TOC, TEPT"
                    )
                }
            ]
            questao = random.choice(opcoes)
            
        elif dificuldade == "medio":
            enunciado = (
                "Paciente de 45 anos, com depressão maior, inicia tratamento com Sertralina 50mg/dia. "
                "Após 2 semanas, não relata melhora significativa.\n\n"
                "a) Esse tempo de tratamento é suficiente para avaliar resposta?\n"
                "b) Qual a conduta mais adequada neste momento?\n"
                "c) Se o paciente estivesse tomando IMAO previamente, quanto tempo deveria esperar para iniciar ISRS?\n"
                "d) Cite 3 efeitos adversos comuns dos ISRS."
            )
            resposta = (
                "a) Não. Antidepressivos demoram 2-4 semanas para início do efeito terapêutico, "
                "e 6-8 semanas para efeito máximo. É muito cedo para avaliar resposta.\n\n"
                "b) Conduta:\n"
                "   - Manter medicação atual\n"
                "   - Reavaliar em 4-6 semanas\n"
                "   - Verificar adesão ao tratamento\n"
                "   - Considerar aumentar dose se tolerado (máx 200mg/dia)\n"
                "   - Manter suporte psicoterapêutico\n\n"
                "c) Washout de IMAO para ISRS:\n"
                "   - Mínimo de 2 semanas (14 dias)\n"
                "   - Para IMAOs irreversíveis, pode ser necessário mais tempo\n"
                "   - O contrário (ISRS → IMAO): 2-5 semanas dependendo do ISRS\n"
                "   - Risco: Síndrome serotoninérgica (potencialmente fatal)\n\n"
                "d) Efeitos adversos dos ISRS:\n"
                "   1. Náusea/desconforto GI (início do tratamento)\n"
                "   2. Disfunção sexual (diminuição de libido, anorgasmia)\n"
                "   3. Cefaleia\n"
                "   4. Insônia ou sonolência\n"
                "   5. Agitação/inquietude (acatisia)\n"
                "   6. Hiponatremia (especialmente em idosos)"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            enunciado = (
                "Paciente de 28 anos, com esquizofrenia, em uso de Haloperidol 10mg/dia há 3 meses, "
                "apresenta rigidez muscular, tremor, bradicinesia e acatisia.\n\n"
                "a) Como se chamam esses efeitos adversos e qual seu mecanismo?\n"
                "b) Qual a diferença entre antipsicóticos típicos e atípicos em relação a esses efeitos?\n"
                "c) Como tratar/manejar esses efeitos adversos?\n"
                "d) Que efeito adverso grave pode ocorrer se houver febre alta associada à rigidez intensa?"
            )
            resposta = (
                "a) Sintomas extrapiramidais (SEP):\n"
                "   - Mecanismo: bloqueio excessivo de receptores D2 na via nigroestriatal\n"
                "   - Tipos:\n"
                "     * Parkinsonismo medicamentoso (rigidez, tremor, bradicinesia)\n"
                "     * Acatisia (inquietude motora, necessidade de movimento)\n"
                "     * Distonia aguda (espasmos musculares, torcicolo)\n"
                "     * Discinesia tardia (movimentos involuntários, uso crônico)\n\n"
                "b) Diferença típicos vs atípicos:\n"
                "   - Típicos (Haloperidol): alta afinidade D2, mais SEP\n"
                "   - Atípicos (Risperidona, Olanzapina, Quetiapina): menor afinidade D2 relativa, "
                "bloqueio 5-HT2A associado, menos SEP\n"
                "   - Clozapina: praticamente sem SEP, mas risco de agranulocitose\n\n"
                "c) Manejo dos SEP:\n"
                "   - Reduzir dose do antipsicótico\n"
                "   - Trocar por antipsicótico atípico\n"
                "   - Parkinsonismo: anticolinérgico (Biperideno)\n"
                "   - Acatisia: beta-bloqueador (Propranolol), benzodiazepínico\n"
                "   - Distonia aguda: Biperideno IM/IV ou difenidramina\n\n"
                "d) Síndrome Neuroléptica Maligna (SNM):\n"
                "   - Emergência médica potencialmente fatal\n"
                "   - Tétrade: febre alta, rigidez extrema, alteração do nível de consciência, "
                "instabilidade autonômica\n"
                "   - Laboratório: CPK muito elevada, leucocitose, mioglobinúria\n"
                "   - Conduta: suspender antipsicótico, suporte intensivo, Dantrolene, Bromocriptina"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("farmacologia")
        return {
            **questao,
            "tipo": "Farmacologia do SNC",
            "materia": "farmacologia",
            "dificuldade": dificuldade
        }

    def gerar_questao_interacoes(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre interações medicamentosas."""
        
        interacao = random.choice(self.interacoes)
        
        if dificuldade == "facil":
            enunciado = (
                f"Qual o risco da associação de {interacao['farmacos'][0]} com {interacao['farmacos'][1]}?"
            )
            resposta = (
                f"Risco: {interacao['efeito']}\n"
                f"Mecanismo: {interacao.get('mecanismo', interacao.get('sintomas', 'Interação farmacodinâmica'))}"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        elif dificuldade == "medio":
            enunciado = (
                f"Paciente em uso crônico de {interacao['farmacos'][0]} inicia tratamento com "
                f"{interacao['farmacos'][1]}.\n\n"
                f"a) Qual o risco dessa associação?\n"
                f"b) Qual o mecanismo da interação?\n"
                f"c) Qual a conduta recomendada?"
            )
            resposta = (
                f"a) Risco: {interacao['efeito']}\n\n"
                f"b) Mecanismo: {interacao.get('mecanismo', interacao.get('sintomas', 'Interação farmacodinâmica'))}\n\n"
                f"c) Conduta: {interacao.get('conduta', 'Monitorar paciente, ajustar doses ou considerar alternativas')}"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            # Questão com múltiplas interações
            outras_interacoes = random.sample([i for i in self.interacoes if i != interacao], 2)
            
            enunciado = (
                "Avalie as seguintes associações medicamentosas e classifique o risco "
                "(alto, moderado, baixo) e o tipo de interação (farmacocinética ou farmacodinâmica):\n\n"
                f"1. {interacao['farmacos'][0]} + {interacao['farmacos'][1]}\n"
                f"2. {outras_interacoes[0]['farmacos'][0]} + {outras_interacoes[0]['farmacos'][1]}\n"
                f"3. {outras_interacoes[1]['farmacos'][0]} + {outras_interacoes[1]['farmacos'][1]}\n\n"
                "Justifique cada resposta."
            )
            resposta = (
                f"1. {interacao['farmacos'][0]} + {interacao['farmacos'][1]}:\n"
                f"   - Risco: Alto\n"
                f"   - Efeito: {interacao['efeito']}\n"
                f"   - Mecanismo: {interacao.get('mecanismo', interacao.get('sintomas', ''))}\n\n"
                f"2. {outras_interacoes[0]['farmacos'][0]} + {outras_interacoes[0]['farmacos'][1]}:\n"
                f"   - Risco: Alto\n"
                f"   - Efeito: {outras_interacoes[0]['efeito']}\n"
                f"   - Mecanismo: {outras_interacoes[0].get('mecanismo', outras_interacoes[0].get('sintomas', ''))}\n\n"
                f"3. {outras_interacoes[1]['farmacos'][0]} + {outras_interacoes[1]['farmacos'][1]}:\n"
                f"   - Risco: Alto/Moderado\n"
                f"   - Efeito: {outras_interacoes[1]['efeito']}\n"
                f"   - Mecanismo: {outras_interacoes[1].get('mecanismo', outras_interacoes[1].get('sintomas', ''))}"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("farmacologia")
        return {
            **questao,
            "tipo": "Interações Medicamentosas",
            "materia": "farmacologia",
            "dificuldade": dificuldade
        }

    def gerar_questao_endocrino(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre fármacos endócrinos/antidiabéticos."""
        
        if dificuldade == "facil":
            opcoes = [
                {
                    "enunciado": "Qual o mecanismo de ação da Metformina e por que é primeira escolha no DM2?",
                    "resposta": (
                        "Mecanismo de ação:\n"
                        "- Ativação da AMPK (AMP-activated protein kinase)\n"
                        "- Redução da gliconeogênese hepática\n"
                        "- Aumento da captação periférica de glicose\n"
                        "- Leve redução da absorção intestinal de glicose\n\n"
                        "Por que é primeira escolha:\n"
                        "1. Não causa hipoglicemia (quando usada isoladamente)\n"
                        "2. Não causa ganho de peso (pode até reduzir)\n"
                        "3. Baixo custo\n"
                        "4. Redução de eventos cardiovasculares (estudo UKPDS)\n"
                        "5. Melhora do perfil lipídico"
                    )
                },
                {
                    "enunciado": "Diferencie as insulinas de ação rápida das de ação longa quanto ao início e duração do efeito.",
                    "resposta": (
                        "Insulinas de ação rápida/ultrarrápida:\n"
                        "- Exemplos: Regular (rápida), Lispro/Aspart/Glulisina (ultrarrápidas)\n"
                        "- Início: 15-30 min (ultrarrápidas: 5-15 min)\n"
                        "- Pico: 2-3 horas (ultrarrápidas: 1-2h)\n"
                        "- Duração: 5-8 horas (ultrarrápidas: 3-5h)\n"
                        "- Uso: Controle da glicemia pós-prandial\n\n"
                        "Insulinas de ação longa:\n"
                        "- Exemplos: Glargina, Detemir, Degludeca\n"
                        "- Início: 1-2 horas\n"
                        "- Pico: sem pico pronunciado (Degludeca) ou mínimo\n"
                        "- Duração: 20-24h (Degludeca: >42h)\n"
                        "- Uso: Controle da glicemia basal (jejum)"
                    )
                }
            ]
            questao = random.choice(opcoes)
            
        elif dificuldade == "medio":
            enunciado = (
                "Paciente de 55 anos, DM2, IMC 32, em uso de Metformina 2g/dia há 6 meses, "
                "mantém HbA1c de 8.2%. Função renal normal, sem doença cardiovascular estabelecida.\n\n"
                "a) Cite duas classes de antidiabéticos que poderiam ser associadas.\n"
                "b) Qual a vantagem dos inibidores de SGLT2 neste paciente?\n"
                "c) Por que sulfonilureias podem ser problemáticas neste paciente?"
            )
            resposta = (
                "a) Classes que podem ser associadas:\n"
                "   1. Inibidores de SGLT2 (Dapagliflozina, Empagliflozina)\n"
                "   2. Agonistas de GLP-1 (Liraglutida, Semaglutida)\n"
                "   3. Inibidores de DPP-4 (Sitagliptina, Vildagliptina)\n"
                "   4. Sulfonilureias (se custo for limitante)\n"
                "   5. Pioglitazona\n\n"
                "b) Vantagens dos inibidores de SGLT2:\n"
                "   - Perda de peso (paciente obeso, IMC 32)\n"
                "   - Não causam hipoglicemia\n"
                "   - Redução da pressão arterial\n"
                "   - Benefício cardiorrenal comprovado\n"
                "   - Mecanismo independente de insulina\n\n"
                "c) Problemas das sulfonilureias:\n"
                "   - Risco de hipoglicemia (especialmente em idosos)\n"
                "   - Ganho de peso (ruim para paciente já obeso)\n"
                "   - Perda de eficácia ao longo do tempo (exaustão de células beta)\n"
                "   - Não têm benefício cardiovascular demonstrado"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            enunciado = (
                "Paciente de 62 anos, DM2 há 15 anos, com doença renal crônica (TFG = 35 mL/min) "
                "e insuficiência cardíaca com fração de ejeção reduzida. Em uso de Metformina "
                "500mg 2x/dia, Glibenclamida 5mg 2x/dia. HbA1c = 9%.\n\n"
                "a) Avalie criticamente a prescrição atual.\n"
                "b) Qual antidiabético tem benefício cardiovascular e renal comprovado neste perfil?\n"
                "c) Monte uma nova prescrição otimizada para este paciente.\n"
                "d) Qual exame laboratorial específico deve ser monitorado com agonistas de GLP-1?"
            )
            resposta = (
                "a) Críticas à prescrição atual:\n"
                "   - Metformina: dose deve ser ajustada/reduzida com TFG 30-45 (máx 1g/dia)\n"
                "     * TFG < 30: contraindicada (risco de acidose lática)\n"
                "   - Glibenclamida: NÃO recomendada em DRC\n"
                "     * Alto risco de hipoglicemia prolongada\n"
                "     * Acúmulo de metabólitos ativos\n"
                "     * Preferir Glipizida ou Gliclazida se necessário (menos acúmulo)\n\n"
                "b) Inibidores de SGLT2 (Dapagliflozina, Empagliflozina):\n"
                "   - Benefício na IC com FE reduzida (estudos DAPA-HF, EMPEROR-Reduced)\n"
                "   - Nefroproteção (DAPA-CKD, CREDENCE)\n"
                "   - Podem ser usados até TFG 20-25 (para cardioproteção)\n"
                "   - Redução de hospitalização por IC\n\n"
                "c) Nova prescrição otimizada:\n"
                "   1. Suspender Glibenclamida\n"
                "   2. Manter Metformina 500mg 2x/dia (monitorar função renal)\n"
                "   3. Adicionar Dapagliflozina 10mg/dia ou Empagliflozina 10mg\n"
                "   4. Considerar Insulina basal (Glargina) para atingir meta\n"
                "   5. Meta de HbA1c mais flexível: 7.5-8% (devido comorbidades)\n\n"
                "d) Agonistas de GLP-1:\n"
                "   - Monitorar: Lipase e amilase (risco de pancreatite)\n"
                "   - Também: função tireoidiana (risco teórico de câncer medular, contraindicado se NEM2)\n"
                "   - Monitorar função renal se náuseas/vômitos (desidratação)"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("farmacologia")
        return {
            **questao,
            "tipo": "Farmacologia Endócrina",
            "materia": "farmacologia",
            "dificuldade": dificuldade
        }

    def gerar_questao(self, topico: str = "geral", dificuldade: str = "medio", observacoes: str = "") -> dict:
        """
        Gera uma questão de farmacologia baseada no tópico e dificuldade.
        
        Args:
            topico: Tópico da questão (farmacocinetica, farmacodinamica, antibioticos, etc.)
            dificuldade: Nível de dificuldade (facil, medio, dificil)
            observacoes: Observações do professor para direcionar a questão
        
        Returns:
            Dicionário com a questão gerada
        """
        topico_lower = topico.lower().replace(" ", "_").replace("-", "_")
        
        # Mapeia tópicos para métodos
        mapeamento = {
            "farmacocinetica": self.gerar_questao_farmacocinetica,
            "farmacocinética": self.gerar_questao_farmacocinetica,
            "adme": self.gerar_questao_farmacocinetica,
            "farmacodinamica": self.gerar_questao_farmacodinamica,
            "farmacodinâmica": self.gerar_questao_farmacodinamica,
            "receptores": self.gerar_questao_farmacodinamica,
            "antibioticos": self.gerar_questao_antibioticos,
            "antibióticos": self.gerar_questao_antibioticos,
            "antimicrobianos": self.gerar_questao_antibioticos,
            "cardiovascular": self.gerar_questao_cardiovascular,
            "anti_hipertensivos": self.gerar_questao_cardiovascular,
            "cardio": self.gerar_questao_cardiovascular,
            "snc": self.gerar_questao_snc,
            "psicofarmacos": self.gerar_questao_snc,
            "psicofármacos": self.gerar_questao_snc,
            "neurologia": self.gerar_questao_snc,
            "psiquiatria": self.gerar_questao_snc,
            "interacoes": self.gerar_questao_interacoes,
            "interações": self.gerar_questao_interacoes,
            "endocrino": self.gerar_questao_endocrino,
            "endócrino": self.gerar_questao_endocrino,
            "diabetes": self.gerar_questao_endocrino,
            "antidiabeticos": self.gerar_questao_endocrino,
            "antidiabéticos": self.gerar_questao_endocrino,
        }
        
        # Se tópico específico, usa o método correspondente
        if topico_lower in mapeamento:
            questao = mapeamento[topico_lower](dificuldade)
        else:
            # Tópico geral: escolhe aleatoriamente
            metodo = random.choice([
                self.gerar_questao_farmacocinetica,
                self.gerar_questao_farmacodinamica,
                self.gerar_questao_antibioticos,
                self.gerar_questao_cardiovascular,
                self.gerar_questao_snc,
                self.gerar_questao_interacoes,
                self.gerar_questao_endocrino
            ])
            questao = metodo(dificuldade)
        
        # Adiciona observações se fornecidas
        if observacoes:
            questao["observacoes_professor"] = observacoes
        
        return questao

