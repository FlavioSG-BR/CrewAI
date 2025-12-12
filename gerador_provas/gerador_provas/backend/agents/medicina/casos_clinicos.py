# -*- coding: utf-8 -*-
"""
Agente especializado em Casos Clínicos.
Gera casos clínicos integrando múltiplas disciplinas médicas.
"""

import random
from crewai import Agent
from backend.utils.logger import log_questao_gerada


class AgenteCasosClinico:
    """Agente especializado em casos clínicos integrativos."""
    
    def __init__(self):
        self.agent = Agent(
            role="Preceptor de Casos Clínicos",
            goal="Criar casos clínicos que integrem conhecimentos de múltiplas disciplinas",
            backstory="Médico clínico com experiência em medicina interna e preceptoria de residentes.",
            verbose=False,
            allow_delegation=False
        )

    def gerar_caso_clinico(self, dificuldade: str = "medio", especialidade: str = "geral") -> dict:
        """Gera um caso clínico completo."""
        
        casos = {
            "facil": [
                {
                    "caso": (
                        "CASO CLÍNICO:\n\n"
                        "Paciente feminina, 22 anos, procura UBS com queixa de disúria, polaciúria "
                        "e urgência miccional há 2 dias. Nega febre, dor lombar ou corrimento vaginal.\n\n"
                        "Exame físico: BEG, afebril, PA 120x80 mmHg. Abdome: sem alterações. "
                        "Punho-percussão lombar negativa bilateralmente.\n\n"
                        "EAS: Leucocitúria (80 leucócitos/campo), nitrito positivo, bacteriúria."
                    ),
                    "perguntas": (
                        "a) Qual o diagnóstico mais provável?\n"
                        "b) Qual o agente etiológico mais comum?\n"
                        "c) Qual o tratamento indicado?\n"
                        "d) Quando solicitar urocultura?"
                    ),
                    "resposta": (
                        "a) INFECÇÃO DO TRATO URINÁRIO BAIXA (Cistite aguda não complicada)\n"
                        "   - Sintomas urinários baixos\n"
                        "   - Sem sinais de pielonefrite (febre, dor lombar)\n"
                        "   - Mulher jovem, não grávida, sem comorbidades\n\n"
                        "b) Escherichia coli (80-85% dos casos)\n"
                        "   - Outros: Staphylococcus saprophyticus, Klebsiella, Proteus\n\n"
                        "c) Tratamento:\n"
                        "   - Primeira linha: Nitrofurantoína 100mg 12/12h por 5-7 dias, ou\n"
                        "   - Fosfomicina 3g dose única, ou\n"
                        "   - Sulfametoxazol-trimetoprim (se resistência local <20%)\n"
                        "   - Quinolonas: reservar para casos selecionados\n\n"
                        "d) Urocultura:\n"
                        "   - Não é necessária em cistite não complicada (tratamento empírico)\n"
                        "   - Indicada em: recorrência, falha terapêutica, complicações\n"
                        "   - Em gestantes, homens, ITU complicada: sempre solicitar"
                    ),
                    "tipo": "Infecciosa/Urologia"
                }
            ],
            "medio": [
                {
                    "caso": (
                        "CASO CLÍNICO:\n\n"
                        "Paciente masculino, 58 anos, hipertenso e tabagista (40 maços-ano), "
                        "procura emergência com dor torácica retroesternal opressiva há 2 horas, "
                        "irradiada para membro superior esquerdo. Refere sudorese e náuseas.\n\n"
                        "Exame físico: Ansioso, pálido, sudoreico. PA 150x90 mmHg, FC 95 bpm, "
                        "SatO2 94% em ar ambiente. ACV: B3, sem sopros. AP: MV+, crepitantes bibasais.\n\n"
                        "ECG: Supradesnivelamento de ST de 3mm em V1-V4.\n"
                        "Troponina: pendente."
                    ),
                    "perguntas": (
                        "a) Qual o diagnóstico?\n"
                        "b) Qual parede do coração está acometida e qual artéria provavelmente ocluída?\n"
                        "c) Qual a conduta imediata?\n"
                        "d) Qual a significância da B3 e dos crepitantes?\n"
                        "e) Qual o mecanismo fisiopatológico da elevação da troponina?"
                    ),
                    "resposta": (
                        "a) INFARTO AGUDO DO MIOCÁRDIO COM SUPRADESNIVELAMENTO DE ST (IAMCSST)\n"
                        "   - Dor típica, fatores de risco, alteração de ECG\n\n"
                        "b) Localização:\n"
                        "   - Parede anterior do ventrículo esquerdo\n"
                        "   - Supra em V1-V4 = território da artéria descendente anterior (DA)\n"
                        "   - IAM anterior: maior área de necrose, pior prognóstico\n\n"
                        "c) Conduta imediata:\n"
                        "   - MONABCH:\n"
                        "     * Morfina (se dor refratária)\n"
                        "     * Oxigênio (se SatO2 < 94%)\n"
                        "     * Nitrato SL (se não hipotensão)\n"
                        "     * AAS 300mg mastigar\n"
                        "     * Clopidogrel/Ticagrelor (dupla antiagregação)\n"
                        "     * Heparina (anticoagulação)\n"
                        "   - REPERFUSÃO:\n"
                        "     * Angioplastia primária (preferencial se <120 min do primeiro contato)\n"
                        "     * Fibrinolítico (se não disponível cateterismo em tempo hábil)\n\n"
                        "d) B3 e crepitantes:\n"
                        "   - B3: sobrecarga de volume, disfunção sistólica de VE\n"
                        "   - Crepitantes bibasais: congestão pulmonar\n"
                        "   - Sugerem INSUFICIÊNCIA CARDÍACA AGUDA (Killip II)\n"
                        "   - Indicadores de pior prognóstico\n\n"
                        "e) Troponina:\n"
                        "   - Proteína do complexo regulatório do músculo cardíaco\n"
                        "   - Liberada na circulação quando há necrose de cardiomiócitos\n"
                        "   - Lesão da membrana celular → liberação de conteúdo intracelular\n"
                        "   - Eleva-se em 3-6h, pico em 12-24h, normaliza em 7-14 dias\n"
                        "   - Marcador de alta sensibilidade e especificidade para IAM"
                    ),
                    "tipo": "Cardiologia/Emergência"
                }
            ],
            "dificil": [
                {
                    "caso": (
                        "CASO CLÍNICO:\n\n"
                        "Paciente feminina, 45 anos, apresenta há 3 meses fadiga progressiva, "
                        "ganho de peso (8kg), constipação, pele seca, intolerância ao frio e "
                        "edema facial. Refere irregularidade menstrual.\n\n"
                        "Exame físico: Bradicardia (52 bpm), PA 100x70 mmHg, pele seca e fria, "
                        "edema periorbital, reflexos tendinosos profundos com relaxamento lentificado, "
                        "tireoide aumentada e firme.\n\n"
                        "Exames laboratoriais:\n"
                        "- TSH: 85 mUI/L (VR: 0,4-4,0)\n"
                        "- T4 livre: 0,3 ng/dL (VR: 0,8-1,8)\n"
                        "- Anti-TPO: 1.200 UI/mL (VR: <35)\n"
                        "- Colesterol total: 280 mg/dL"
                    ),
                    "perguntas": (
                        "a) Qual o diagnóstico e sua etiologia?\n"
                        "b) Explique a fisiopatologia dos sintomas.\n"
                        "c) Por que há hipercolesterolemia?\n"
                        "d) Qual o tratamento e como monitorar?\n"
                        "e) Qual a correlação histológica esperada na tireoide?"
                    ),
                    "resposta": (
                        "a) Diagnóstico:\n"
                        "   HIPOTIREOIDISMO PRIMÁRIO por TIREOIDITE DE HASHIMOTO\n"
                        "   - TSH muito elevado (primário)\n"
                        "   - T4L baixo (confirma hipotireoidismo)\n"
                        "   - Anti-TPO elevado: autoimunidade → Hashimoto\n"
                        "   - Bócio: característico da fase inicial\n\n"
                        "b) Fisiopatologia dos sintomas:\n"
                        "   - Hormônio tireoidiano baixo → metabolismo reduzido\n"
                        "   - FADIGA: menor produção de ATP, menor consumo de O2\n"
                        "   - GANHO DE PESO: menor taxa metabólica basal\n"
                        "   - CONSTIPAÇÃO: menor motilidade GI\n"
                        "   - PELE SECA/FRIA: menor termogênese, vasoconstricção\n"
                        "   - BRADICARDIA: efeito cronotrópico negativo\n"
                        "   - EDEMA: mixedema (acúmulo de mucopolissacarídeos)\n"
                        "   - REFLEXOS LENTOS: menor condução nervosa e contração muscular\n\n"
                        "c) Hipercolesterolemia:\n"
                        "   - T3/T4 estimulam receptores hepáticos de LDL\n"
                        "   - Hipotireoidismo → menos receptores de LDL\n"
                        "   - Menor clearance de LDL-colesterol do plasma\n"
                        "   - Também reduz conversão de colesterol em ácidos biliares\n"
                        "   - Risco cardiovascular aumentado\n\n"
                        "d) Tratamento e monitoramento:\n"
                        "   TRATAMENTO:\n"
                        "   - Levotiroxina (T4) via oral em jejum\n"
                        "   - Dose inicial: 1,6 µg/kg/dia (ajustar em idosos/cardiopatas)\n"
                        "   - Iniciar com doses baixas e titular gradualmente\n\n"
                        "   MONITORAMENTO:\n"
                        "   - Dosar TSH após 6-8 semanas de dose estável\n"
                        "   - Meta: TSH na faixa normal\n"
                        "   - Ajustar dose até eutireoidismo\n"
                        "   - Após estabilização: TSH anual\n\n"
                        "e) Histologia (Tireoidite de Hashimoto):\n"
                        "   - Infiltrado linfocitário difuso com folículos linfoides\n"
                        "   - Centros germinativos na tireoide\n"
                        "   - Destruição de folículos tireoidianos\n"
                        "   - Células de Hürthle (oxifílicas): metaplasia\n"
                        "   - Fibrose (fases avançadas)\n"
                        "   - Atrofia folicular progressiva"
                    ),
                    "tipo": "Endocrinologia"
                }
            ]
        }
        
        # Seleciona um caso baseado na dificuldade
        caso_selecionado = random.choice(casos.get(dificuldade, casos["medio"]))
        
        log_questao_gerada("casos_clinicos")
        
        return {
            "enunciado": caso_selecionado["caso"] + "\n\n" + caso_selecionado["perguntas"],
            "resposta": caso_selecionado["resposta"],
            "tipo": f"Caso Clínico - {caso_selecionado['tipo']}",
            "materia": "casos_clinicos",
            "dificuldade": dificuldade
        }

    def gerar_questao(self, topico: str = "geral", dificuldade: str = "medio", observacoes: str = "") -> dict:
        """Gera um caso clínico."""
        questao = self.gerar_caso_clinico(dificuldade, topico)
        
        if observacoes:
            questao["observacoes_professor"] = observacoes
        
        return questao

