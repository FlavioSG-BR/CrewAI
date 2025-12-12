# -*- coding: utf-8 -*-
"""
Agente especializado em Bioquímica.
Gera questões sobre metabolismo, enzimas e bioquímica clínica.
"""

import random
from crewai import Agent
from backend.utils.logger import log_questao_gerada


class AgenteBioquimica:
    """Agente especializado em questões de Bioquímica."""
    
    def __init__(self):
        self.agent = Agent(
            role="Professor de Bioquímica",
            goal="Criar questões sobre vias metabólicas, enzimas e marcadores bioquímicos",
            backstory="Bioquímico com PhD em metabolismo e experiência em bioquímica clínica.",
            verbose=False,
            allow_delegation=False
        )

    def gerar_questao_metabolismo(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre vias metabólicas."""
        
        if dificuldade == "facil":
            enunciado = "Descreva as fases da glicólise e seu saldo energético."
            resposta = (
                "GLICÓLISE:\n"
                "Via de degradação da glicose no citoplasma.\n\n"
                "FASE DE INVESTIMENTO (gasto de energia):\n"
                "1. Glicose → Glicose-6-P (hexoquinase/glicoquinase) - 1 ATP\n"
                "2. G6P → Frutose-6-P (fosfoglicose isomerase)\n"
                "3. F6P → Frutose-1,6-biP (PFK-1) - 1 ATP *enzima reguladora*\n"
                "4. F1,6biP → 2 trioses (aldolase)\n\n"
                "FASE DE RENDIMENTO (produção de energia):\n"
                "5-10. Cada triose gera: 2 ATP + 1 NADH\n"
                "       Para 2 trioses: 4 ATP + 2 NADH\n\n"
                "SALDO FINAL (por glicose):\n"
                "- 2 ATP (4 produzidos - 2 investidos)\n"
                "- 2 NADH (→ 4-6 ATP na cadeia respiratória)\n"
                "- 2 Piruvato\n\n"
                "Destino do piruvato:\n"
                "- Aeróbico: Acetil-CoA → Ciclo de Krebs\n"
                "- Anaeróbico: Lactato (regenera NAD+)"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        elif dificuldade == "medio":
            enunciado = (
                "Sobre o ciclo de Krebs:\n"
                "a) Onde ocorre e qual seu papel?\n"
                "b) Quais os produtos por volta do ciclo?\n"
                "c) Como é regulado?\n"
                "d) Por que é chamado de ciclo anfibólico?"
            )
            resposta = (
                "a) Local e função:\n"
                "   - Matriz mitocondrial\n"
                "   - Via final comum do metabolismo de carboidratos, lipídios e proteínas\n"
                "   - Gera coenzimas reduzidas (NADH, FADH2) para cadeia respiratória\n\n"
                "b) Produtos por volta (por Acetil-CoA):\n"
                "   - 3 NADH → 7,5 ATP\n"
                "   - 1 FADH2 → 1,5 ATP\n"
                "   - 1 GTP (= 1 ATP)\n"
                "   - 2 CO2\n"
                "   Total: ~10 ATP por Acetil-CoA\n\n"
                "c) Regulação:\n"
                "   Enzimas reguladoras:\n"
                "   1. Citrato sintase: inibida por ATP, citrato, NADH\n"
                "   2. Isocitrato desidrogenase: ativada por ADP, inibida por ATP, NADH\n"
                "   3. α-cetoglutarato desidrogenase: inibida por Succinil-CoA, NADH\n"
                "   - Controlado pela razão ATP/ADP e NADH/NAD+\n\n"
                "d) Ciclo anfibólico:\n"
                "   - CATABÓLICO: degrada Acetil-CoA gerando energia\n"
                "   - ANABÓLICO: fornece intermediários para biossíntese\n"
                "     * Citrato → ácidos graxos\n"
                "     * α-cetoglutarato → aminoácidos (glutamato)\n"
                "     * Oxaloacetato → gliconeogênese, aminoácidos (aspartato)\n"
                "     * Succinil-CoA → heme"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            enunciado = (
                "Paciente diabético descompensado, cetoacidose diabética.\n\n"
                "a) Explique a via de formação dos corpos cetônicos.\n"
                "b) Por que a cetogênese está aumentada no DM descompensado?\n"
                "c) Quais os corpos cetônicos e qual causa acidose?\n"
                "d) Por que o hálito do paciente tem odor de maçã podre?"
            )
            resposta = (
                "a) Cetogênese (na mitocôndria hepática):\n"
                "   1. β-oxidação de ácidos graxos → Acetil-CoA (excesso)\n"
                "   2. 2 Acetil-CoA → Acetoacetil-CoA (tiolase)\n"
                "   3. + Acetil-CoA → HMG-CoA (HMG-CoA sintase)\n"
                "   4. HMG-CoA → Acetoacetato + Acetil-CoA (HMG-CoA liase)\n"
                "   5. Acetoacetato ⇌ β-hidroxibutirato (desidrogenase)\n"
                "   6. Acetoacetato → Acetona (descarboxilação espontânea)\n\n"
                "b) Aumento no DM descompensado:\n"
                "   - Deficiência de insulina → lipólise intensa\n"
                "   - Ácidos graxos livres em excesso no fígado\n"
                "   - Glucagon elevado ativa CPT-1 (transporte para mitocôndria)\n"
                "   - Malonil-CoA baixo (não inibe CPT-1)\n"
                "   - β-oxidação intensa → excesso de Acetil-CoA\n"
                "   - Ciclo de Krebs saturado (oxaloacetato desviado para gliconeogênese)\n"
                "   - Acetil-CoA desviado para cetogênese\n\n"
                "c) Corpos cetônicos:\n"
                "   - Acetoacetato: ácido (libera H+) → causa acidose\n"
                "   - β-hidroxibutirato: ácido, principal na CAD\n"
                "   - Acetona: volátil, não ionizável, não causa acidose\n"
                "   * Acidose: acúmulo de H+ + esgotamento do tampão bicarbonato\n\n"
                "d) Hálito de maçã podre:\n"
                "   - ACETONA é volátil\n"
                "   - Eliminada pelos pulmões na expiração\n"
                "   - Odor característico (cetônico/frutado)\n"
                "   - Sinal clínico de cetoacidose"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("bioquimica")
        return {
            **questao,
            "tipo": "Metabolismo",
            "materia": "bioquimica",
            "dificuldade": dificuldade
        }

    def gerar_questao_enzimas(self, dificuldade: str = "medio") -> dict:
        """Gera questão sobre enzimas."""
        
        if dificuldade == "facil":
            enunciado = "Diferencie inibição enzimática competitiva de não-competitiva."
            resposta = (
                "INIBIÇÃO COMPETITIVA:\n"
                "- Inibidor compete com substrato pelo sítio ativo\n"
                "- Estrutura similar ao substrato\n"
                "- Aumenta Km aparente (menor afinidade aparente)\n"
                "- Vmax INALTERADA (pode ser superada com excesso de substrato)\n"
                "- Exemplo: Estatinas inibem HMG-CoA redutase\n\n"
                "INIBIÇÃO NÃO-COMPETITIVA:\n"
                "- Inibidor liga-se em sítio diferente (alostérico)\n"
                "- Não compete com substrato\n"
                "- Km INALTERADO (afinidade pelo substrato não muda)\n"
                "- Vmax DIMINUÍDA (menor quantidade de enzima funcional)\n"
                "- Não pode ser revertida aumentando substrato\n"
                "- Exemplo: Metais pesados inativando grupos -SH"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        elif dificuldade == "medio":
            enunciado = (
                "Sobre a cinética enzimática de Michaelis-Menten:\n"
                "a) O que representa a constante Km?\n"
                "b) Como determinar Km graficamente?\n"
                "c) Qual o significado fisiológico de um Km baixo?"
            )
            resposta = (
                "a) Constante de Michaelis (Km):\n"
                "   - Concentração de substrato na qual V = Vmax/2\n"
                "   - Medida inversa da afinidade enzima-substrato\n"
                "   - Km BAIXO = alta afinidade\n"
                "   - Km ALTO = baixa afinidade\n"
                "   - Característica de cada par enzima-substrato\n\n"
                "b) Determinação gráfica:\n"
                "   Gráfico hiperbólico (V vs [S]):\n"
                "   - Encontrar Vmax (platô da curva)\n"
                "   - Calcular Vmax/2\n"
                "   - Km = [S] correspondente a Vmax/2\n\n"
                "   Gráfico de Lineweaver-Burk (1/V vs 1/[S]):\n"
                "   - Reta com intercepto y = 1/Vmax\n"
                "   - Intercepto x = -1/Km\n\n"
                "c) Significado de Km baixo:\n"
                "   - Enzima atinge saturação em baixas [S]\n"
                "   - Opera próximo de Vmax mesmo com pouco substrato\n"
                "   - Importante em vias que precisam ser eficientes\n"
                "   - Exemplo: Hexoquinase (Km = 0.1mM para glicose)\n"
                "     * Fosforila glicose mesmo em baixas concentrações"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
            
        else:  # dificil
            enunciado = (
                "Explique a regulação da PFK-1 (fosfofrutoquinase-1), enzima-chave da glicólise:\n"
                "a) Por que é considerada enzima-chave?\n"
                "b) Quais são seus moduladores alostéricos positivos e negativos?\n"
                "c) Qual o papel da frutose-2,6-bisfosfato?\n"
                "d) Como hormônios (insulina/glucagon) regulam indiretamente a PFK-1?"
            )
            resposta = (
                "a) Enzima-chave:\n"
                "   - Catalisa reação irreversível (comprometimento com glicólise)\n"
                "   - Ponto de regulação mais importante da via\n"
                "   - Primeira reação específica da glicólise\n"
                "   - Determina o fluxo de toda a via\n\n"
                "b) Moduladores alostéricos:\n"
                "   ATIVADORES (indicam necessidade de energia/glicólise):\n"
                "   - AMP, ADP (baixa carga energética)\n"
                "   - Frutose-2,6-bifosfato (ativador mais potente)\n"
                "   - Pi (fosfato inorgânico)\n\n"
                "   INIBIDORES (indicam suficiência energética):\n"
                "   - ATP (alta carga energética)\n"
                "   - Citrato (Ciclo de Krebs suprido)\n"
                "   - H+ (acidose)\n\n"
                "c) Frutose-2,6-bisfosfato (F2,6BP):\n"
                "   - PRINCIPAL regulador da glicólise/gliconeogênese\n"
                "   - Ativador alostérico muito potente da PFK-1\n"
                "   - Inibidor da Frutose-1,6-bifosfatase (gliconeogênese)\n"
                "   - Produzido/degradado pela enzima bifuncional PFK-2/FBPase-2\n\n"
                "d) Regulação hormonal:\n"
                "   INSULINA (estado alimentado):\n"
                "   - Ativa fosfatases → desfosforila PFK-2\n"
                "   - PFK-2 ATIVA → produz F2,6BP\n"
                "   - F2,6BP ALTO → ativa PFK-1 → GLICÓLISE\n\n"
                "   GLUCAGON (estado de jejum):\n"
                "   - Ativa PKA (via cAMP) → fosforila PFK-2\n"
                "   - PFK-2 fosforilada → atividade FBPase-2\n"
                "   - F2,6BP BAIXO → PFK-1 menos ativa\n"
                "   - Favorece GLICONEOGÊNESE no fígado"
            )
            questao = {"enunciado": enunciado, "resposta": resposta}
        
        log_questao_gerada("bioquimica")
        return {
            **questao,
            "tipo": "Enzimologia",
            "materia": "bioquimica",
            "dificuldade": dificuldade
        }

    def gerar_questao(self, topico: str = "geral", dificuldade: str = "medio", observacoes: str = "") -> dict:
        """Gera uma questão de bioquímica baseada no tópico e dificuldade."""
        topico_lower = topico.lower().replace(" ", "_")
        
        mapeamento = {
            "metabolismo": self.gerar_questao_metabolismo,
            "glicolise": self.gerar_questao_metabolismo,
            "krebs": self.gerar_questao_metabolismo,
            "cetose": self.gerar_questao_metabolismo,
            "enzimas": self.gerar_questao_enzimas,
            "cinetica": self.gerar_questao_enzimas,
            "inibicao": self.gerar_questao_enzimas,
        }
        
        if topico_lower in mapeamento:
            questao = mapeamento[topico_lower](dificuldade)
        else:
            metodo = random.choice([self.gerar_questao_metabolismo, self.gerar_questao_enzimas])
            questao = metodo(dificuldade)
        
        if observacoes:
            questao["observacoes_professor"] = observacoes
        
        return questao

