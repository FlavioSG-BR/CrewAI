# -*- coding: utf-8 -*-
"""
Agente especializado em Histologia.
Gera questões sobre tecidos, células, correlações clínico-patológicas
e identificação de estruturas histológicas.
"""

import random
from crewai import Agent
from backend.utils.logger import log_questao_gerada


class AgenteHistologia:
    """Agente especializado em questões de Histologia."""
    
    def __init__(self):
        self.agent = Agent(
            role="Professor de Histologia",
            goal="Criar questões sobre tecidos, células e correlação estrutura-função",
            backstory="Histologista com mestrado em morfologia e 10 anos de experiência em microscopia e ensino médico.",
            verbose=False,
            allow_delegation=False
        )
        
        # Base de dados de tecidos
        self.tecidos = {
            "epitelial": {
                "revestimento": {
                    "simples_pavimentoso": {
                        "localizacao": ["Endotélio vascular", "Mesotélio (serosas)", "Cápsula de Bowman"],
                        "funcao": "Troca de substâncias, revestimento de baixo atrito",
                        "caracteristicas": "Células achatadas, núcleo alongado central"
                    },
                    "simples_cubico": {
                        "localizacao": ["Túbulos renais", "Ductos de glândulas", "Superfície do ovário"],
                        "funcao": "Absorção e secreção",
                        "caracteristicas": "Células com altura = largura, núcleo central esférico"
                    },
                    "simples_cilindrico": {
                        "localizacao": ["Intestino delgado", "Estômago", "Vesícula biliar"],
                        "funcao": "Absorção, secreção, proteção",
                        "caracteristicas": "Células altas, núcleo basal oval, pode ter microvilosidades"
                    },
                    "pseudoestratificado": {
                        "localizacao": ["Traqueia", "Brônquios", "Epidídimo"],
                        "funcao": "Proteção, movimento de muco (ciliado)",
                        "caracteristicas": "Todos os núcleos em alturas diferentes, todos tocam a lâmina basal"
                    },
                    "estratificado_pavimentoso": {
                        "localizacao": ["Pele (queratinizado)", "Esôfago (não queratinizado)", "Vagina"],
                        "funcao": "Proteção mecânica, resistência ao atrito",
                        "caracteristicas": "Múltiplas camadas, células basais cuboides/cilíndricas, superfície pavimentosa"
                    },
                    "transicao": {
                        "localizacao": ["Bexiga", "Ureter", "Pelve renal"],
                        "funcao": "Distensão, barreira impermeável",
                        "caracteristicas": "Células em guarda-chuva na superfície, muda de forma com distensão"
                    }
                },
                "glandular": {
                    "exocrino": {
                        "classificacao_forma": ["Tubular", "Acinosa/Alveolar", "Tubuloacinosa"],
                        "classificacao_secrecao": {
                            "merocrina": "Exocitose (maioria das glândulas)",
                            "apocrina": "Liberação de parte do citoplasma apical (mama)",
                            "holocrina": "Liberação de toda a célula (sebácea)"
                        }
                    },
                    "endocrino": {
                        "tipos": ["Cordonal (adrenal)", "Folicular (tireoide)", "Ilhotas (pâncreas)"],
                        "secrecao": "Hormônios para o sangue"
                    }
                }
            },
            "conjuntivo": {
                "celulas": {
                    "fibroblastos": "Síntese de fibras e matriz extracelular",
                    "macrofagos": "Fagocitose, apresentação de antígenos",
                    "mastocitos": "Histamina, reações alérgicas",
                    "plasmocitos": "Produção de anticorpos",
                    "adipocitos": "Armazenamento de energia"
                },
                "fibras": {
                    "colagenas": "Resistência à tração, tipo I mais comum",
                    "elasticas": "Elasticidade, rica em elastina",
                    "reticulares": "Arcabouço de órgãos, colágeno tipo III"
                },
                "tipos": {
                    "frouxo": "Muita matriz, poucas fibras, localizado em derme papilar",
                    "denso_modelado": "Fibras paralelas, tendões e ligamentos",
                    "denso_nao_modelado": "Fibras em várias direções, derme reticular"
                }
            },
            "muscular": {
                "esqueletico": {
                    "caracteristicas": "Células multinucleadas, estriações transversais, núcleos periféricos",
                    "unidade_funcional": "Sarcômero (banda A, banda I, linha Z, linha M)",
                    "contracao": "Voluntária, rápida"
                },
                "cardiaco": {
                    "caracteristicas": "Células ramificadas, núcleo central, discos intercalares",
                    "discos_intercalares": "Junções gap (comunicação), desmossomos (adesão), fáscia aderente",
                    "contracao": "Involuntária, rítmica"
                },
                "liso": {
                    "caracteristicas": "Células fusiformes, núcleo central único, sem estriações",
                    "localizacao": "Parede de vísceras ocas, vasos sanguíneos",
                    "contracao": "Involuntária, lenta e sustentada"
                }
            },
            "nervoso": {
                "neuronios": {
                    "partes": ["Corpo celular (pericário)", "Dendritos", "Axônio"],
                    "classificacao_polar": ["Multipolar", "Bipolar", "Pseudounipolar"],
                    "classificacao_funcional": ["Sensitivo", "Motor", "Interneurônio"]
                },
                "glia_snc": {
                    "astrocitos": "Suporte, barreira hematoencefálica, homeostase",
                    "oligodendrocitos": "Mielinização no SNC",
                    "microglia": "Fagocitose, defesa imune",
                    "ependima": "Revestimento dos ventrículos, produção de LCR"
                },
                "glia_snp": {
                    "celulas_schwann": "Mielinização no SNP",
                    "celulas_satelite": "Suporte aos corpos neuronais nos gânglios"
                }
            }
        }
        
        # Sistemas/Órgãos
        self.sistemas = {
            "digestorio": {
                "esofago": {
                    "camadas": ["Mucosa (ep. estrat. pavim.)", "Submucosa", "Muscular", "Adventícia/Serosa"],
                    "caracteristicas": "Glândulas mucosas na submucosa, músculo estriado (1/3 sup) a liso (1/3 inf)"
                },
                "estomago": {
                    "glandulas": {
                        "celulas_parietais": "HCl e fator intrínseco, acidófilas, região apical",
                        "celulas_principais": "Pepsinogênio, basófilas, região basal",
                        "celulas_mucosas": "Muco protetor, região do colo",
                        "celulas_enteroendocrinas": "Gastrina, serotonina"
                    }
                },
                "intestino_delgado": {
                    "vilosidades": "Projeções da mucosa, aumentam superfície de absorção",
                    "microvilosidades": "Borda em escova, aumentam ainda mais a superfície",
                    "criptas_lieberkuhn": "Glândulas intestinais, células de Paneth na base",
                    "diferencas_regionais": {
                        "duodeno": "Glândulas de Brunner (submucosa), vilosidades largas",
                        "jejuno": "Vilosidades longas, maior absorção",
                        "ileo": "Placas de Peyer (folículos linfoides)"
                    }
                },
                "figado": {
                    "lobulo_hepatico": "Veia centro-lobular central, tríades portais na periferia",
                    "triades_portais": ["Ramo da veia porta", "Ramo da artéria hepática", "Ducto biliar"],
                    "sinusoides": "Capilares fenestrados, células de Kupffer (macrófagos)",
                    "espaco_disse": "Entre hepatócitos e sinusoides, células estreladas (Ito)"
                }
            },
            "respiratorio": {
                "traqueia": {
                    "epitélio": "Pseudoestratificado cilíndrico ciliado com células caliciformes",
                    "cartilagem": "Anéis em C de cartilagem hialina",
                    "musculo": "Músculo liso na parede posterior"
                },
                "bronquios": {
                    "caracteristicas": "Placas de cartilagem, músculo liso, glândulas seromucosas"
                },
                "bronquiolos": {
                    "caracteristicas": "Sem cartilagem, sem glândulas, músculo liso proeminente",
                    "celulas_clara": "Células secretoras não ciliadas"
                },
                "alveolos": {
                    "pneumocitos_tipo_I": "Revestimento (95% da superfície), troca gasosa",
                    "pneumocitos_tipo_II": "Produção de surfactante, células cuboides",
                    "macrofagos_alveolares": "Fagocitose de partículas inaladas"
                }
            },
            "urinario": {
                "rim": {
                    "nefron": {
                        "corpusculo_renal": {
                            "capsula_bowman": "Epitélio simples pavimentoso (folheto parietal), podócitos (visceral)",
                            "glomerulo": "Capilares fenestrados, células mesangiais"
                        },
                        "tubulo_contorcido_proximal": "Microvilosidades (borda em escova), células acidófilas",
                        "alca_henle": "Porção delgada (epitélio simples pavimentoso), porção espessa",
                        "tubulo_contorcido_distal": "Células menores, sem borda em escova, mácula densa"
                    },
                    "ducto_coletor": "Células principais (claras) e intercaladas (escuras)"
                }
            },
            "endocrino": {
                "tireoide": {
                    "foliculos": "Células foliculares (T3, T4), coloide central",
                    "celulas_c": "Células parafoliculares, calcitonina"
                },
                "adrenal": {
                    "cortex": {
                        "zona_glomerulosa": "Mineralocorticoides (aldosterona)",
                        "zona_fasciculada": "Glicocorticoides (cortisol)",
                        "zona_reticulada": "Androgênios"
                    },
                    "medula": "Células cromafins, catecolaminas (adrenalina, noradrenalina)"
                },
                "pancreas": {
                    "exocrino": "Ácinos serosos, enzimas digestivas",
                    "endocrino": {
                        "ilhotas_langerhans": {
                            "celulas_alfa": "Glucagon (periféricas)",
                            "celulas_beta": "Insulina (centrais, maioria)",
                            "celulas_delta": "Somatostatina"
                        }
                    }
                }
            }
        }
        
        # Colorações histológicas
        self.coloracoes = {
            "HE": {
                "hematoxilina": "Corante básico, cora estruturas ácidas (núcleo) em roxo/azul",
                "eosina": "Corante ácido, cora estruturas básicas (citoplasma) em rosa"
            },
            "PAS": {
                "detecta": "Polissacarídeos, glicogênio, mucinas neutras",
                "aplicacoes": "Membrana basal, células caliciformes, glicogenoses"
            },
            "Tricomico_Masson": {
                "detecta": "Colágeno (azul/verde), músculo (vermelho), núcleo (preto)",
                "aplicacoes": "Fibrose, diferenciação de tecidos"
            },
            "Prata": {
                "detecta": "Fibras reticulares, melanina",
                "aplicacoes": "Arcabouço de órgãos linfoides, fígado"
            },
            "Alcian_Blue": {
                "detecta": "Mucopolissacarídeos ácidos, proteoglicanos",
                "aplicacoes": "Cartilagem, mucinas ácidas"
            }
        }

    def gerar_questao_tecidos(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre tecidos básicos."""
        
        if dificuldade == "facil":
            opcoes = [
                {
                    "enunciado": "Cite os quatro tipos básicos de tecido e a principal característica de cada um.",
                    "resposta": (
                        "1. Tecido Epitelial:\n"
                        "   - Células justapostas, pouca matriz extracelular\n"
                        "   - Funções: revestimento, proteção, secreção, absorção\n\n"
                        "2. Tecido Conjuntivo:\n"
                        "   - Abundante matriz extracelular (fibras + substância fundamental)\n"
                        "   - Funções: suporte, conexão, nutrição, defesa\n\n"
                        "3. Tecido Muscular:\n"
                        "   - Células especializadas em contração\n"
                        "   - Tipos: esquelético, cardíaco, liso\n\n"
                        "4. Tecido Nervoso:\n"
                        "   - Neurônios (condução de impulsos) e células da glia (suporte)\n"
                        "   - Funções: comunicação, integração, coordenação"
                    )
                },
                {
                    "enunciado": "Qual a diferença entre tecido epitelial de revestimento simples e estratificado?",
                    "resposta": (
                        "Epitélio Simples:\n"
                        "- Uma única camada de células\n"
                        "- Todas as células tocam a lâmina basal\n"
                        "- Mais delicado, facilita trocas\n"
                        "- Exemplos: endotélio, epitélio intestinal, alvéolos\n\n"
                        "Epitélio Estratificado:\n"
                        "- Múltiplas camadas de células\n"
                        "- Apenas a camada basal toca a lâmina basal\n"
                        "- Mais resistente, proteção mecânica\n"
                        "- Exemplos: pele (queratinizado), esôfago, vagina"
                    )
                }
            ]
            questao = random.choice(opcoes)
            
        elif dificuldade == "medio":
            enunciado = (
                "Em uma lâmina histológica, você observa um epitélio com as seguintes características:\n"
                "- Todas as células parecem repousar sobre a lâmina basal\n"
                "- Os núcleos estão em diferentes alturas\n"
                "- Presença de cílios na superfície apical\n"
                "- Células caliciformes intercaladas\n\n"
                "a) Qual o tipo de epitélio?\n"
                "b) Onde esse epitélio é encontrado?\n"
                "c) Qual a função dos cílios e das células caliciformes?"
            )
            resposta = (
                "a) Epitélio pseudoestratificado cilíndrico ciliado com células caliciformes\n\n"
                "b) Localizações:\n"
                "   - Traqueia\n"
                "   - Brônquios principais\n"
                "   - Cavidade nasal\n"
                "   - Parte da faringe\n\n"
                "c) Funções:\n"
                "   - Cílios: movimento do muco em direção à faringe (escada rolante mucociliar)\n"
                "   - Células caliciformes: produção de muco que aprisiona partículas e microrganismos\n"
                "   - Juntos formam o sistema de defesa mucociliar das vias aéreas"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            enunciado = (
                "Compare os três tipos de tecido muscular em relação a:\n"
                "a) Características morfológicas das células\n"
                "b) Localização dos núcleos\n"
                "c) Presença e tipo de estriações\n"
                "d) Tipo de controle (voluntário/involuntário)\n"
                "e) Estruturas especializadas de comunicação/adesão"
            )
            resposta = (
                "MÚSCULO ESQUELÉTICO:\n"
                "a) Células cilíndricas longas, multinucleadas, até 30cm\n"
                "b) Núcleos periféricos (subsarcolemais)\n"
                "c) Estriações transversais bem evidentes (bandas A e I)\n"
                "d) Controle voluntário (neurônio motor somático)\n"
                "e) Junção neuromuscular (placa motora)\n\n"
                "MÚSCULO CARDÍACO:\n"
                "a) Células ramificadas, 1-2 núcleos, 80-100µm\n"
                "b) Núcleo central\n"
                "c) Estriações transversais (menos regulares que esquelético)\n"
                "d) Controle involuntário (autônomo, intrínseco)\n"
                "e) Discos intercalares: junções gap (comunicação elétrica), desmossomos e "
                "fáscia aderente (adesão mecânica)\n\n"
                "MÚSCULO LISO:\n"
                "a) Células fusiformes, núcleo único, 20-500µm\n"
                "b) Núcleo central (forma de saca-rolhas quando contraído)\n"
                "c) Sem estriações (miofilamentos não organizados em sarcômeros)\n"
                "d) Controle involuntário (autônomo, hormonal)\n"
                "e) Junções gap (comunicação), corpos densos (ancoragem de actina)"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("histologia")
        return {
            **questao,
            "tipo": "Tecidos Básicos",
            "materia": "histologia",
            "dificuldade": dificuldade
        }

    def gerar_questao_sistema_digestorio(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre histologia do sistema digestório."""
        
        if dificuldade == "facil":
            opcoes = [
                {
                    "enunciado": "Quais são as quatro camadas (túnicas) da parede do tubo digestório?",
                    "resposta": (
                        "Da luz para a periferia:\n\n"
                        "1. MUCOSA:\n"
                        "   - Epitélio de revestimento\n"
                        "   - Lâmina própria (tecido conjuntivo frouxo)\n"
                        "   - Muscular da mucosa\n\n"
                        "2. SUBMUCOSA:\n"
                        "   - Tecido conjuntivo denso\n"
                        "   - Vasos e nervos (plexo de Meissner)\n\n"
                        "3. MUSCULAR:\n"
                        "   - Circular interna\n"
                        "   - Longitudinal externa\n"
                        "   - Plexo mioentérico (Auerbach) entre as camadas\n\n"
                        "4. ADVENTÍCIA ou SEROSA:\n"
                        "   - Adventícia: conjuntivo (órgãos retroperitoneais)\n"
                        "   - Serosa: mesotélio + conjuntivo (órgãos intraperitoneais)"
                    )
                },
                {
                    "enunciado": "Como diferenciar histologicamente o intestino delgado do intestino grosso?",
                    "resposta": (
                        "INTESTINO DELGADO:\n"
                        "- Presença de vilosidades (projeções da mucosa)\n"
                        "- Borda em escova evidente (microvilosidades)\n"
                        "- Enterócitos absortivos predominantes\n"
                        "- Células de Paneth nas criptas (grânulos eosinofílicos)\n"
                        "- Placas de Peyer (íleo)\n\n"
                        "INTESTINO GROSSO:\n"
                        "- Ausência de vilosidades (superfície plana)\n"
                        "- Muitas células caliciformes (produção de muco)\n"
                        "- Criptas mais profundas e retas\n"
                        "- Sem células de Paneth\n"
                        "- Tênias (concentração de músculo longitudinal)"
                    )
                }
            ]
            questao = random.choice(opcoes)
            
        elif dificuldade == "medio":
            enunciado = (
                "Em uma lâmina histológica de estômago corada por HE:\n\n"
                "a) Identifique as células parietais e principais. Como diferenciá-las?\n"
                "b) Qual a função de cada uma?\n"
                "c) Por que as células parietais são mais abundantes no corpo gástrico?"
            )
            resposta = (
                "a) Diferenciação das células:\n"
                "   CÉLULAS PARIETAIS (oxínticas):\n"
                "   - Localizadas na região apical/média da glândula\n"
                "   - Citoplasma intensamente acidófilo (rosa-eosinofílico)\n"
                "   - Grandes, arredondadas ou piramidais\n"
                "   - Núcleo central esférico\n\n"
                "   CÉLULAS PRINCIPAIS (zimogênicas):\n"
                "   - Localizadas na base/fundo da glândula\n"
                "   - Citoplasma basófilo (azulado) por RER abundante\n"
                "   - Menores, forma cuboide\n"
                "   - Grânulos de secreção apicais\n\n"
                "b) Funções:\n"
                "   - Células parietais: secretam HCl (ácido) e Fator Intrínseco (absorção B12)\n"
                "   - Células principais: secretam pepsinogênio (precursor da pepsina)\n\n"
                "c) O corpo gástrico tem mais células parietais porque:\n"
                "   - É a principal região de secreção ácida\n"
                "   - Antro: mais células G (gastrina) e mucosas\n"
                "   - Cárdia: principalmente células mucosas"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            enunciado = (
                "Correlacione a estrutura histológica com a função no fígado:\n\n"
                "a) Descreva a organização do lóbulo hepático clássico e identifique as estruturas.\n"
                "b) Qual a composição da tríade portal?\n"
                "c) Explique o espaço de Disse e sua importância funcional.\n"
                "d) Diferencie células de Kupffer de células estreladas (Ito).\n"
                "e) Como o fluxo sanguíneo e biliar se organizam no lóbulo?"
            )
            resposta = (
                "a) Lóbulo hepático clássico:\n"
                "   - Forma hexagonal com veia centro-lobular no centro\n"
                "   - Tríades portais nos vértices (cantos)\n"
                "   - Cordões de hepatócitos radiando do centro para a periferia\n"
                "   - Sinusoides entre os cordões\n\n"
                "b) Tríade portal (espaço porta):\n"
                "   1. Ramo da veia porta (sangue do TGI, baço)\n"
                "   2. Ramo da artéria hepática (sangue oxigenado)\n"
                "   3. Ducto biliar (epitélio cuboide)\n"
                "   * Pode incluir vasos linfáticos\n\n"
                "c) Espaço de Disse:\n"
                "   - Espaço entre hepatócitos e sinusoides\n"
                "   - Contém microvilosidades dos hepatócitos\n"
                "   - Células estreladas (armazenam vitamina A)\n"
                "   - Permite troca de substâncias entre sangue e hepatócitos\n"
                "   - Drenagem linfática começa aqui\n\n"
                "d) Diferenciação celular:\n"
                "   Células de Kupffer:\n"
                "   - Macrófagos residentes do fígado\n"
                "   - Dentro dos sinusoides (intraluminais)\n"
                "   - Fagocitose de bactérias, debris, eritrócitos velhos\n\n"
                "   Células estreladas (Ito):\n"
                "   - No espaço de Disse (perisinusoidais)\n"
                "   - Armazenam vitamina A em gotículas lipídicas\n"
                "   - Quando ativadas: produzem colágeno (fibrose/cirrose)\n\n"
                "e) Fluxo no lóbulo:\n"
                "   - Sangue: periferia → centro (centrípeto)\n"
                "     Tríade portal → sinusoides → veia centro-lobular\n"
                "   - Bile: centro → periferia (centrífugo)\n"
                "     Canalículos biliares → ductos de Hering → ducto biliar da tríade"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("histologia")
        return {
            **questao,
            "tipo": "Sistema Digestório",
            "materia": "histologia",
            "dificuldade": dificuldade
        }

    def gerar_questao_coloracoes(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre colorações histológicas."""
        
        if dificuldade == "facil":
            enunciado = (
                "Na coloração de Hematoxilina e Eosina (HE):\n"
                "a) Qual o princípio da coloração?\n"
                "b) O que cada corante cora?"
            )
            resposta = (
                "a) Princípio: baseia-se na afinidade entre corantes e estruturas celulares\n"
                "   por diferença de pH/carga elétrica.\n\n"
                "b) Hematoxilina:\n"
                "   - Corante BÁSICO (catiônico)\n"
                "   - Cora estruturas ÁCIDAS (aniônicas): BASOFILIA\n"
                "   - Coram em ROXO/AZUL:\n"
                "     * Núcleo (DNA, RNA)\n"
                "     * Ribossomos (RER)\n"
                "     * Heterocromatina\n\n"
                "   Eosina:\n"
                "   - Corante ÁCIDO (aniônico)\n"
                "   - Cora estruturas BÁSICAS (catiônicas): ACIDOFILIA\n"
                "   - Coram em ROSA/VERMELHO:\n"
                "     * Citoplasma (proteínas)\n"
                "     * Fibras colágenas\n"
                "     * Grânulos de células parietais"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        elif dificuldade == "medio":
            enunciado = (
                "Você precisa avaliar a presença de fibrose em uma biópsia hepática.\n\n"
                "a) Qual coloração especial você solicitaria?\n"
                "b) Como essa coloração diferencia o colágeno de outras estruturas?\n"
                "c) Cite outra situação clínica onde essa coloração é útil."
            )
            resposta = (
                "a) Tricrômico de Masson (ou Tricrômico de Gomori, Picrosirius Red)\n\n"
                "b) Diferenciação de estruturas:\n"
                "   - Colágeno: AZUL ou VERDE (dependendo da técnica)\n"
                "   - Fibras musculares: VERMELHO\n"
                "   - Núcleos: PRETO ou AZUL-ESCURO\n"
                "   - Citoplasma: ROSA/VERMELHO\n"
                "   * Na fibrose hepática, áreas de colágeno (azul) substituem parênquima normal\n\n"
                "c) Outras aplicações:\n"
                "   - Fibrose miocárdica (pós-infarto)\n"
                "   - Fibrose pulmonar\n"
                "   - Cicatrização de feridas\n"
                "   - Diferenciação de tumores (estroma vs parênquima)\n"
                "   - Glomeruloesclerose renal"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            enunciado = (
                "Para cada situação clínico-patológica, indique a coloração especial mais adequada "
                "e justifique sua escolha:\n\n"
                "a) Suspeita de doença de depósito de glicogênio (glicogenose)\n"
                "b) Avaliação de melanoma vs carcinoma pouco diferenciado\n"
                "c) Diagnóstico de amiloidose\n"
                "d) Identificação de microrganismos fúngicos em tecido\n"
                "e) Avaliação de ferro tecidual"
            )
            resposta = (
                "a) GLICOGENOSE - PAS (Periodic Acid-Schiff):\n"
                "   - PAS cora glicogênio em MAGENTA\n"
                "   - Comparar com PAS-diastase (diastase digere glicogênio)\n"
                "   - Se PAS+ e PAS-diastase negativo = glicogênio presente\n\n"
                "b) MELANOMA - Fontana-Masson (prata):\n"
                "   - Detecta melanina (grânulos pretos/marrons)\n"
                "   - Alternativa: imunohistoquímica (S100, HMB-45, Melan-A)\n"
                "   - Ajuda a diferenciar de outros tumores\n\n"
                "c) AMILOIDOSE - Vermelho Congo:\n"
                "   - Amiloide cora em vermelho/rosa\n"
                "   - Sob luz polarizada: birrefringência verde-maçã\n"
                "   - Patognomônico de amiloidose\n"
                "   - Alternativa: Tioflavina T (fluorescência)\n\n"
                "d) FUNGOS - Grocott-Gomori (prata metenamina) ou PAS:\n"
                "   - Grocott: fungos coram em PRETO, fundo verde\n"
                "   - PAS: fungos coram em MAGENTA\n"
                "   - Detecta parede fúngica (polissacarídeos)\n\n"
                "e) FERRO - Azul da Prússia (Perls):\n"
                "   - Ferro (hemossiderina) cora em AZUL\n"
                "   - Útil em hemocromatose, hemossiderose\n"
                "   - Quantifica depósitos de ferro"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("histologia")
        return {
            **questao,
            "tipo": "Colorações Histológicas",
            "materia": "histologia",
            "dificuldade": dificuldade
        }

    def gerar_questao(self, topico: str = "geral", dificuldade: str = "medio", observacoes: str = "") -> dict:
        """
        Gera uma questão de histologia baseada no tópico e dificuldade.
        """
        topico_lower = topico.lower().replace(" ", "_").replace("-", "_")
        
        mapeamento = {
            "tecidos": self.gerar_questao_tecidos,
            "tecidos_basicos": self.gerar_questao_tecidos,
            "epitelial": self.gerar_questao_tecidos,
            "conjuntivo": self.gerar_questao_tecidos,
            "muscular": self.gerar_questao_tecidos,
            "nervoso": self.gerar_questao_tecidos,
            "digestorio": self.gerar_questao_sistema_digestorio,
            "digestório": self.gerar_questao_sistema_digestorio,
            "tgi": self.gerar_questao_sistema_digestorio,
            "figado": self.gerar_questao_sistema_digestorio,
            "intestino": self.gerar_questao_sistema_digestorio,
            "estomago": self.gerar_questao_sistema_digestorio,
            "coloracoes": self.gerar_questao_coloracoes,
            "colorações": self.gerar_questao_coloracoes,
            "he": self.gerar_questao_coloracoes,
            "pas": self.gerar_questao_coloracoes,
            "tricromico": self.gerar_questao_coloracoes,
        }
        
        if topico_lower in mapeamento:
            questao = mapeamento[topico_lower](dificuldade)
        else:
            metodo = random.choice([
                self.gerar_questao_tecidos,
                self.gerar_questao_sistema_digestorio,
                self.gerar_questao_coloracoes
            ])
            questao = metodo(dificuldade)
        
        if observacoes:
            questao["observacoes_professor"] = observacoes
        
        return questao

