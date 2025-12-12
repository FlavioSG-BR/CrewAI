# -*- coding: utf-8 -*-
"""
Agente especializado em Anatomia Humana.
Gera questões sobre sistemas orgânicos, estruturas anatômicas,
relações topográficas e anatomia clínica/radiológica.
"""

import random
from crewai import Agent
from backend.utils.logger import log_questao_gerada


class AgenteAnatomia:
    """Agente especializado em questões de Anatomia."""
    
    def __init__(self):
        self.agent = Agent(
            role="Professor de Anatomia Humana",
            goal="Criar questões sobre estruturas anatômicas, relações topográficas e anatomia clínica",
            backstory="Anatomista com especialização em anatomia clínica e cirúrgica, 12 anos de docência.",
            verbose=False,
            allow_delegation=False
        )

    def gerar_questao_osteologia(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre ossos e articulações."""
        
        if dificuldade == "facil":
            opcoes = [
                {
                    "enunciado": "Quantos ossos compõem o esqueleto humano adulto e como são classificados quanto à forma?",
                    "resposta": (
                        "O esqueleto humano adulto possui 206 ossos.\n\n"
                        "Classificação quanto à forma:\n"
                        "1. Ossos longos: comprimento > largura/espessura (fêmur, úmero)\n"
                        "2. Ossos curtos: dimensões aproximadamente iguais (carpos, tarsos)\n"
                        "3. Ossos planos: finos, achatados (escápula, ossos do crânio)\n"
                        "4. Ossos irregulares: forma complexa (vértebras, osso esfenóide)\n"
                        "5. Ossos sesamoides: desenvolvidos em tendões (patela)\n"
                        "6. Ossos pneumáticos: contêm cavidades com ar (frontal, etmóide)"
                    )
                },
                {
                    "enunciado": "Cite os ossos que compõem o neurocrânio.",
                    "resposta": (
                        "O neurocrânio (caixa craniana) é formado por 8 ossos:\n\n"
                        "Ossos ímpares (4):\n"
                        "1. Frontal\n"
                        "2. Occipital\n"
                        "3. Esfenóide\n"
                        "4. Etmóide\n\n"
                        "Ossos pares (2):\n"
                        "5. Parietais (2)\n"
                        "6. Temporais (2)"
                    )
                }
            ]
            questao = random.choice(opcoes)
            
        elif dificuldade == "medio":
            enunciado = (
                "Em relação ao membro superior:\n"
                "a) Quais ossos formam a articulação do ombro?\n"
                "b) Quais os movimentos possíveis nessa articulação?\n"
                "c) Qual estrutura óssea pode ser fraturada em quedas com o braço estendido?"
            )
            resposta = (
                "a) Articulação do ombro (glenoumeral):\n"
                "   - Cabeça do úmero\n"
                "   - Cavidade glenoide da escápula\n"
                "   * Articulação sinovial do tipo esferóide (enartrorse)\n\n"
                "b) Movimentos:\n"
                "   - Flexão e extensão (plano sagital)\n"
                "   - Abdução e adução (plano frontal)\n"
                "   - Rotação medial e lateral (eixo longitudinal)\n"
                "   - Circundução (combinação de todos)\n\n"
                "c) Fraturas por queda com braço estendido:\n"
                "   - Clavícula (mais comum): por transmissão de força\n"
                "   - Extremidade distal do rádio (fratura de Colles)\n"
                "   - Colo cirúrgico do úmero (especialmente em idosos)"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            enunciado = (
                "Um paciente sofreu fratura do colo do fêmur. Explique:\n"
                "a) Qual a vascularização da cabeça do fêmur?\n"
                "b) Por que fraturas do colo femoral podem levar a necrose avascular?\n"
                "c) Diferencie fraturas intracapsulares de extracapsulares em termos de prognóstico.\n"
                "d) Qual nervo pode ser lesado em luxações posteriores do quadril?"
            )
            resposta = (
                "a) Vascularização da cabeça do fêmur:\n"
                "   - Artérias circunflexas femorais (medial > lateral)\n"
                "     * Ramos da artéria femoral profunda\n"
                "   - Artéria do ligamento da cabeça do fêmur\n"
                "     * Ramo da artéria obturatória (menor contribuição)\n"
                "   - As artérias retinaculares ascendem pelo colo\n\n"
                "b) Necrose avascular:\n"
                "   - As artérias retinaculares cursam pela superfície do colo\n"
                "   - Fraturas do colo podem romper esses vasos\n"
                "   - A artéria do ligamento é insuficiente sozinha\n"
                "   - A cabeça fica sem suprimento sanguíneo adequado\n\n"
                "c) Fraturas intra vs extracapsulares:\n"
                "   Intracapsulares (colo femoral):\n"
                "   - Maior risco de necrose avascular\n"
                "   - Interferem na vascularização retinacular\n"
                "   - Frequentemente necessitam prótese\n\n"
                "   Extracapsulares (transtrocantéricas):\n"
                "   - Menor risco de necrose\n"
                "   - Vascularização preservada\n"
                "   - Geralmente consolidam com fixação\n\n"
                "d) Nervo ciático:\n"
                "   - Passa posterior à articulação do quadril\n"
                "   - Risco em luxações posteriores\n"
                "   - Pode causar pé caído, perda sensitiva em perna/pé"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("anatomia")
        return {
            **questao,
            "tipo": "Osteologia",
            "materia": "anatomia",
            "dificuldade": dificuldade
        }

    def gerar_questao_sistema_cardiovascular(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre anatomia cardiovascular."""
        
        if dificuldade == "facil":
            enunciado = "Descreva o trajeto do sangue pela circulação pulmonar (pequena circulação)."
            resposta = (
                "Trajeto da circulação pulmonar:\n\n"
                "1. Ventrículo direito\n"
                "   ↓\n"
                "2. Tronco pulmonar\n"
                "   ↓\n"
                "3. Artérias pulmonares (direita e esquerda)\n"
                "   ↓\n"
                "4. Capilares pulmonares (troca gasosa nos alvéolos)\n"
                "   ↓\n"
                "5. Veias pulmonares (4 veias - 2 de cada lado)\n"
                "   ↓\n"
                "6. Átrio esquerdo\n\n"
                "OBS: As artérias pulmonares carregam sangue venoso (desoxigenado) "
                "e as veias pulmonares carregam sangue arterial (oxigenado)."
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        elif dificuldade == "medio":
            enunciado = (
                "Sobre a anatomia das artérias coronárias:\n"
                "a) De onde se originam?\n"
                "b) Quais são as principais artérias e que áreas irrigam?\n"
                "c) O que é dominância coronariana?"
            )
            resposta = (
                "a) Origem:\n"
                "   - Seios de Valsalva (seios aórticos), logo acima da valva aórtica\n"
                "   - Coronária direita: seio coronariano direito\n"
                "   - Coronária esquerda: seio coronariano esquerdo\n\n"
                "b) Artérias e territórios:\n"
                "   CORONÁRIA ESQUERDA:\n"
                "   - Tronco da coronária esquerda → bifurca em:\n"
                "     * Artéria descendente anterior (DA): parede anterior do VE, septo anterior, ápice\n"
                "     * Artéria circunflexa (Cx): parede lateral e posterior do VE\n\n"
                "   CORONÁRIA DIREITA:\n"
                "   - Parede inferior do VE\n"
                "   - Ventrículo direito\n"
                "   - Nó sinoatrial (55% dos casos)\n"
                "   - Nó atrioventricular (90% - se dominância direita)\n\n"
                "c) Dominância coronariana:\n"
                "   - Refere-se a qual artéria origina a artéria descendente posterior\n"
                "   - Dominância DIREITA (85%): coronária direita origina a DP\n"
                "   - Dominância ESQUERDA (8%): circunflexa origina a DP\n"
                "   - Codominância (7%): ambas contribuem"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            enunciado = (
                "Paciente com infarto agudo do miocárdio de parede inferior.\n\n"
                "a) Qual artéria coronária está mais provavelmente ocluída?\n"
                "b) Que outras estruturas podem ser afetadas e quais complicações podem surgir?\n"
                "c) Por que infartos de parede inferior podem causar bradicardia?\n"
                "d) Como diferenciar anatomicamente um IAM anterior de um inferior?"
            )
            resposta = (
                "a) Artéria coronária direita (mais comum) ou circunflexa (se dominância esquerda).\n\n"
                "b) Estruturas afetadas e complicações:\n"
                "   - Nó AV (90%): bloqueio atrioventricular\n"
                "   - Ventrículo direito: disfunção de VD, hipotensão\n"
                "   - Músculo papilar posteromedial: insuficiência mitral\n"
                "   - Parede posterior do VE: extensão do infarto\n\n"
                "c) Bradicardia no IAM inferior:\n"
                "   - A coronária direita irriga o nó sinoatrial (55%) e AV (90%)\n"
                "   - Isquemia do nó sinusal → bradicardia sinusal\n"
                "   - Isquemia do nó AV → bloqueios AV\n"
                "   - Reflexo de Bezold-Jarisch: aferentes vagais ativados\n\n"
                "d) Diferenciação anatômica:\n"
                "   IAM ANTERIOR:\n"
                "   - Artéria descendente anterior\n"
                "   - Parede anterior do VE, septo\n"
                "   - ECG: supradesnivelamento em V1-V4\n"
                "   - Complicações: aneurisma apical, CIV\n\n"
                "   IAM INFERIOR:\n"
                "   - Coronária direita (ou Cx)\n"
                "   - Parede diafragmática do VE\n"
                "   - ECG: supradesnivelamento em D2, D3, aVF\n"
                "   - Complicações: bradicardia, infarto de VD"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("anatomia")
        return {
            **questao,
            "tipo": "Sistema Cardiovascular",
            "materia": "anatomia",
            "dificuldade": dificuldade
        }

    def gerar_questao_sistema_nervoso(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre neuroanatomia."""
        
        if dificuldade == "facil":
            enunciado = "Quais são as divisões do sistema nervoso? Cite as partes de cada divisão."
            resposta = (
                "SISTEMA NERVOSO CENTRAL (SNC):\n"
                "1. Encéfalo:\n"
                "   - Cérebro (telencéfalo + diencéfalo)\n"
                "   - Cerebelo\n"
                "   - Tronco encefálico (mesencéfalo, ponte, bulbo)\n"
                "2. Medula espinal\n\n"
                "SISTEMA NERVOSO PERIFÉRICO (SNP):\n"
                "1. Nervos:\n"
                "   - Cranianos (12 pares)\n"
                "   - Espinais (31 pares)\n"
                "2. Gânglios:\n"
                "   - Sensitivos\n"
                "   - Autônomos\n"
                "3. Terminações nervosas\n\n"
                "Divisão funcional do SNP:\n"
                "- Somático (voluntário)\n"
                "- Autônomo (involuntário):\n"
                "  * Simpático\n"
                "  * Parassimpático\n"
                "  * Entérico"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        elif dificuldade == "medio":
            enunciado = (
                "Sobre o plexo braquial:\n"
                "a) Quais raízes nervosas o formam?\n"
                "b) Cite os principais nervos terminais e os músculos que inervam.\n"
                "c) Qual nervo é lesado na 'mão em garra'?"
            )
            resposta = (
                "a) Raízes: C5, C6, C7, C8 e T1\n"
                "   (lembrar: troncos → divisões → fascículos → nervos)\n\n"
                "b) Principais nervos terminais:\n"
                "   MUSCULOCUTÂNEO (C5-C7):\n"
                "   - Bíceps braquial, braquial, coracobraquial\n"
                "   - Flexão do cotovelo\n\n"
                "   MEDIANO (C6-T1):\n"
                "   - Flexores do punho e dedos (superficiais)\n"
                "   - Músculos tenares (exceto adutor do polegar)\n\n"
                "   ULNAR (C8-T1):\n"
                "   - Flexor ulnar do carpo, parte do flexor profundo\n"
                "   - Músculos hipotenares, interósseos, lumbricais 3-4\n\n"
                "   RADIAL (C5-T1):\n"
                "   - Extensores do punho e dedos\n"
                "   - Tríceps braquial\n\n"
                "   AXILAR (C5-C6):\n"
                "   - Deltoide, redondo menor\n\n"
                "c) 'Mão em garra': lesão do nervo ULNAR\n"
                "   - Hiperextensão das MCF 4-5 (interósseos fracos)\n"
                "   - Flexão das IF (flexores profundos intactos)"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            enunciado = (
                "Paciente vítima de AVC apresenta hemiplegia à direita e afasia.\n\n"
                "a) Em qual hemisfério ocorreu o AVC?\n"
                "b) Quais áreas corticais provavelmente foram afetadas?\n"
                "c) Qual artéria foi provavelmente acometida?\n"
                "d) Diferencie afasia de Broca de afasia de Wernicke.\n"
                "e) Por que a face inferior está mais acometida que a superior no AVC cortical?"
            )
            resposta = (
                "a) Hemisfério ESQUERDO:\n"
                "   - Hemiplegia à direita (decussação piramidal)\n"
                "   - Afasia (centro da linguagem é dominante à esquerda em 95%)\n\n"
                "b) Áreas corticais afetadas:\n"
                "   - Córtex motor primário (giro pré-central) → hemiplegia\n"
                "   - Áreas de linguagem (Broca e/ou Wernicke) → afasia\n\n"
                "c) Artéria cerebral média esquerda:\n"
                "   - Irriga a maior parte da face lateral do hemisfério\n"
                "   - Inclui área motora e áreas de linguagem\n\n"
                "d) Afasias:\n"
                "   BROCA (motora, de expressão):\n"
                "   - Área de Broca: giro frontal inferior\n"
                "   - Fala não fluente, telegráfica\n"
                "   - Compreensão preservada\n"
                "   - Paciente frustrado\n\n"
                "   WERNICKE (sensorial, de compreensão):\n"
                "   - Área de Wernicke: giro temporal superior\n"
                "   - Fala fluente mas sem sentido (jargonofasia)\n"
                "   - Compreensão prejudicada\n"
                "   - Paciente não percebe o déficit\n\n"
                "e) Face inferior mais acometida:\n"
                "   - O 'homúnculo motor' mostra representação maior da face na parte lateral\n"
                "   - Córtex lateral é irrigado pela cerebral média\n"
                "   - Membro inferior tem representação mais medial (cerebral anterior)\n"
                "   - AVC da cerebral média: face/braço >> perna"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("anatomia")
        return {
            **questao,
            "tipo": "Sistema Nervoso",
            "materia": "anatomia",
            "dificuldade": dificuldade
        }

    def gerar_questao(self, topico: str = "geral", dificuldade: str = "medio", observacoes: str = "") -> dict:
        """Gera uma questão de anatomia baseada no tópico e dificuldade."""
        topico_lower = topico.lower().replace(" ", "_")
        
        mapeamento = {
            "osteologia": self.gerar_questao_osteologia,
            "ossos": self.gerar_questao_osteologia,
            "articulacoes": self.gerar_questao_osteologia,
            "esqueleto": self.gerar_questao_osteologia,
            "cardiovascular": self.gerar_questao_sistema_cardiovascular,
            "coracao": self.gerar_questao_sistema_cardiovascular,
            "coronarias": self.gerar_questao_sistema_cardiovascular,
            "vasos": self.gerar_questao_sistema_cardiovascular,
            "nervoso": self.gerar_questao_sistema_nervoso,
            "neuroanatomia": self.gerar_questao_sistema_nervoso,
            "cerebro": self.gerar_questao_sistema_nervoso,
            "plexos": self.gerar_questao_sistema_nervoso,
        }
        
        if topico_lower in mapeamento:
            questao = mapeamento[topico_lower](dificuldade)
        else:
            metodo = random.choice([
                self.gerar_questao_osteologia,
                self.gerar_questao_sistema_cardiovascular,
                self.gerar_questao_sistema_nervoso
            ])
            questao = metodo(dificuldade)
        
        if observacoes:
            questao["observacoes_professor"] = observacoes
        
        return questao

