"""
Agente de Biologia - Gerador de questões de Biologia.

Especialização em:
- Farmacêutica: Farmacologia, Medicamentos, Interações
- Medicina: Anatomia, Fisiologia, Patologia
- Biologia Celular: Células, Organelas, Metabolismo
- Genética: DNA, Hereditariedade, Biotecnologia
- Microbiologia: Bactérias, Vírus, Imunologia
- Ecologia: Ecossistemas, Cadeias alimentares
"""

import random
from typing import Literal
from crewai import Agent
from backend.utils.logger import log_questao_gerada


# Banco de dados de medicamentos
MEDICAMENTOS = {
    "analgesicos": [
        {"nome": "Paracetamol", "classe": "Analgésico/Antipirético", "mecanismo": "Inibe COX no SNC", "indicacao": "Dor leve a moderada, febre"},
        {"nome": "Dipirona", "classe": "Analgésico/Antipirético", "mecanismo": "Inibe COX e ativa canais de potássio", "indicacao": "Dor, febre"},
        {"nome": "Ibuprofeno", "classe": "AINE", "mecanismo": "Inibe COX-1 e COX-2", "indicacao": "Dor, inflamação, febre"},
        {"nome": "Ácido Acetilsalicílico", "classe": "AINE", "mecanismo": "Inibe irreversivelmente COX", "indicacao": "Dor, febre, antiagregante plaquetário"},
    ],
    "antibioticos": [
        {"nome": "Amoxicilina", "classe": "Penicilina", "mecanismo": "Inibe síntese da parede celular", "espectro": "Gram+ e alguns Gram-"},
        {"nome": "Azitromicina", "classe": "Macrolídeo", "mecanismo": "Inibe síntese proteica (50S)", "espectro": "Gram+, atípicos"},
        {"nome": "Ciprofloxacino", "classe": "Fluoroquinolona", "mecanismo": "Inibe DNA girase", "espectro": "Amplo espectro"},
        {"nome": "Cefalexina", "classe": "Cefalosporina 1ª geração", "mecanismo": "Inibe síntese da parede celular", "espectro": "Gram+"},
    ],
    "cardiovasculares": [
        {"nome": "Atenolol", "classe": "Beta-bloqueador", "mecanismo": "Bloqueia receptores β1", "indicacao": "Hipertensão, angina"},
        {"nome": "Losartana", "classe": "BRA", "mecanismo": "Bloqueia receptor AT1 da angiotensina II", "indicacao": "Hipertensão"},
        {"nome": "Enalapril", "classe": "IECA", "mecanismo": "Inibe enzima conversora de angiotensina", "indicacao": "Hipertensão, ICC"},
        {"nome": "Hidroclorotiazida", "classe": "Diurético tiazídico", "mecanismo": "Inibe cotransportador Na-Cl", "indicacao": "Hipertensão, edema"},
    ],
    "snc": [
        {"nome": "Fluoxetina", "classe": "ISRS", "mecanismo": "Inibe recaptação de serotonina", "indicacao": "Depressão, TOC, ansiedade"},
        {"nome": "Diazepam", "classe": "Benzodiazepínico", "mecanismo": "Potencializa GABA", "indicacao": "Ansiedade, convulsões"},
        {"nome": "Carbamazepina", "classe": "Anticonvulsivante", "mecanismo": "Bloqueia canais de sódio", "indicacao": "Epilepsia, neuralgia"},
        {"nome": "Haloperidol", "classe": "Antipsicótico típico", "mecanismo": "Bloqueia receptores D2", "indicacao": "Esquizofrenia, agitação"},
    ]
}

# Sistemas do corpo humano
SISTEMAS = {
    "cardiovascular": {
        "orgaos": ["Coração", "Artérias", "Veias", "Capilares"],
        "funcao": "Transporte de sangue, nutrientes e oxigênio",
        "doencas": ["Hipertensão", "Infarto", "AVC", "Arritmias"]
    },
    "respiratorio": {
        "orgaos": ["Pulmões", "Traqueia", "Brônquios", "Alvéolos"],
        "funcao": "Trocas gasosas (O₂ e CO₂)",
        "doencas": ["Asma", "DPOC", "Pneumonia", "Bronquite"]
    },
    "digestorio": {
        "orgaos": ["Boca", "Esôfago", "Estômago", "Intestinos", "Fígado", "Pâncreas"],
        "funcao": "Digestão e absorção de nutrientes",
        "doencas": ["Gastrite", "Úlcera", "Cirrose", "Pancreatite"]
    },
    "nervoso": {
        "orgaos": ["Cérebro", "Cerebelo", "Medula espinhal", "Nervos"],
        "funcao": "Controle e coordenação do organismo",
        "doencas": ["Alzheimer", "Parkinson", "Epilepsia", "Esclerose múltipla"]
    },
    "endocrino": {
        "orgaos": ["Hipófise", "Tireoide", "Suprarrenais", "Pâncreas", "Gônadas"],
        "funcao": "Produção de hormônios",
        "doencas": ["Diabetes", "Hipotireoidismo", "Hipertireoidismo", "Cushing"]
    }
}

# Organelas celulares
ORGANELAS = {
    "mitocondria": {"funcao": "Respiração celular e produção de ATP", "membrana": "Dupla"},
    "ribossomo": {"funcao": "Síntese de proteínas", "membrana": "Sem membrana"},
    "reticulo_liso": {"funcao": "Síntese de lipídios e detoxificação", "membrana": "Simples"},
    "reticulo_rugoso": {"funcao": "Síntese de proteínas para exportação", "membrana": "Simples"},
    "golgi": {"funcao": "Modificação e empacotamento de proteínas", "membrana": "Simples"},
    "lisossomo": {"funcao": "Digestão intracelular", "membrana": "Simples"},
    "nucleo": {"funcao": "Armazenamento do DNA e controle celular", "membrana": "Dupla"},
    "cloroplasto": {"funcao": "Fotossíntese", "membrana": "Dupla", "exclusivo": "vegetais"}
}


class AgenteBiologia:
    """Agente especializado em questões de Biologia com foco em farmacêutica e medicina."""
    
    def __init__(self):
        self.agent = Agent(
            role="Professor de Biologia e Ciências Farmacêuticas",
            goal="Criar questões sobre biologia, farmacologia, anatomia e fisiologia",
            backstory="Doutor em Ciências Biológicas com especialização em Farmacologia Clínica e experiência em ensino para cursos de Medicina e Farmácia",
            verbose=False,
            allow_delegation=False
        )
        self._gerador_imagens = None
    
    def _get_gerador_imagens(self):
        """Lazy loading do gerador de imagens."""
        if self._gerador_imagens is None:
            from backend.agents.imagens import AgenteImagens
            self._gerador_imagens = AgenteImagens()
        return self._gerador_imagens

    # =========================================================================
    # FARMACOLOGIA
    # =========================================================================
    
    def gerar_questao_farmacologia(self, dificuldade: str = "medio", com_diagrama: bool = False) -> dict:
        """Gera questão sobre Farmacologia."""
        
        if dificuldade == "facil":
            categoria = random.choice(list(MEDICAMENTOS.keys()))
            med = random.choice(MEDICAMENTOS[categoria])
            
            enunciado = (
                f"O medicamento {med['nome']} pertence à classe dos {med['classe']}. "
                f"Qual é a sua principal indicação terapêutica?"
            )
            resposta = f"O {med['nome']} é indicado para: {med['indicacao']}"
            
        elif dificuldade == "medio":
            categoria = random.choice(list(MEDICAMENTOS.keys()))
            med = random.choice(MEDICAMENTOS[categoria])
            
            enunciado = (
                f"Sobre o fármaco {med['nome']}:\n"
                f"a) A qual classe farmacológica pertence?\n"
                f"b) Qual seu mecanismo de ação?\n"
                f"c) Cite uma indicação clínica."
            )
            resposta = (
                f"a) Classe: {med['classe']}\n"
                f"b) Mecanismo: {med['mecanismo']}\n"
                f"c) Indicação: {med['indicacao']}"
            )
            
        else:  # dificil
            # Interação medicamentosa
            med1 = random.choice(MEDICAMENTOS["analgesicos"])
            med2 = random.choice(MEDICAMENTOS["cardiovasculares"])
            
            enunciado = (
                f"Um paciente hipertenso em uso de {med2['nome']} ({med2['classe']}) "
                f"inicia automedicação com {med1['nome']} ({med1['classe']}) para dor. "
                f"Considerando os mecanismos de ação desses fármacos:\n"
                f"a) Explique o mecanismo de ação de cada medicamento;\n"
                f"b) Existe potencial interação entre eles? Justifique;\n"
                f"c) Qual seria a conduta farmacológica adequada?"
            )
            
            resposta = (
                f"a) Mecanismos:\n"
                f"   - {med2['nome']}: {med2['mecanismo']}\n"
                f"   - {med1['nome']}: {med1['mecanismo']}\n\n"
                f"b) Potencial interação:\n"
                f"   AINEs podem reduzir o efeito anti-hipertensivo por inibição de\n"
                f"   prostaglandinas renais, causando retenção de sódio e água.\n"
                f"   Também podem antagonizar o efeito de IECAs e BRAs.\n\n"
                f"c) Conduta adequada:\n"
                f"   - Preferir paracetamol (menor interferência renal)\n"
                f"   - Se usar AINE, monitorar PA e função renal\n"
                f"   - Uso por curto período e menor dose eficaz"
            )
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Farmacologia",
            "dificuldade": dificuldade,
            "topico": "farmaceutica"
        }
        
        log_questao_gerada("biologia")
        return resultado

    # =========================================================================
    # ANATOMIA E FISIOLOGIA
    # =========================================================================
    
    def gerar_questao_anatomia(self, dificuldade: str = "medio", com_diagrama: bool = False) -> dict:
        """Gera questão sobre Anatomia e Fisiologia."""
        
        if dificuldade == "facil":
            sistema = random.choice(list(SISTEMAS.keys()))
            info = SISTEMAS[sistema]
            
            enunciado = (
                f"Cite três órgãos que compõem o sistema {sistema} e descreva "
                f"a função principal desse sistema."
            )
            resposta = (
                f"Órgãos: {', '.join(info['orgaos'][:3])}\n"
                f"Função: {info['funcao']}"
            )
            
        elif dificuldade == "medio":
            sistema = random.choice(list(SISTEMAS.keys()))
            info = SISTEMAS[sistema]
            doenca = random.choice(info['doencas'])
            
            enunciado = (
                f"Sobre o sistema {sistema}:\n"
                f"a) Quais são os principais órgãos que o compõem?\n"
                f"b) Qual a função principal desse sistema?\n"
                f"c) A doença '{doenca}' afeta esse sistema. Explique brevemente como."
            )
            
            explicacoes_doencas = {
                "Hipertensão": "Aumento da pressão arterial por resistência vascular aumentada",
                "Infarto": "Obstrução de artéria coronária causando necrose do músculo cardíaco",
                "Asma": "Inflamação e broncoconstrição das vias aéreas",
                "Diabetes": "Deficiência de insulina ou resistência à sua ação",
                "Alzheimer": "Degeneração neuronal com perda de memória progressiva",
                "Gastrite": "Inflamação da mucosa gástrica",
            }
            explicacao = explicacoes_doencas.get(doenca, f"Alteração patológica do sistema {sistema}")
            
            resposta = (
                f"a) Órgãos: {', '.join(info['orgaos'])}\n"
                f"b) Função: {info['funcao']}\n"
                f"c) {doenca}: {explicacao}"
            )
            
        else:  # dificil
            # Caso clínico
            sistema = "cardiovascular"
            
            enunciado = (
                f"CASO CLÍNICO: Paciente de 58 anos, masculino, tabagista, diabético, "
                f"chega ao pronto-socorro com dor precordial intensa há 2 horas, "
                f"irradiando para braço esquerdo, associada a sudorese e náuseas.\n\n"
                f"a) Qual a principal hipótese diagnóstica?\n"
                f"b) Explique a fisiopatologia da doença;\n"
                f"c) Quais exames são essenciais para confirmação?\n"
                f"d) Cite três fatores de risco presentes no caso."
            )
            
            resposta = (
                f"a) Hipótese: Infarto Agudo do Miocárdio (IAM)\n\n"
                f"b) Fisiopatologia:\n"
                f"   - Ruptura de placa aterosclerótica em artéria coronária\n"
                f"   - Formação de trombo obstruindo o fluxo sanguíneo\n"
                f"   - Isquemia do músculo cardíaco\n"
                f"   - Necrose miocárdica se não houver reperfusão\n\n"
                f"c) Exames essenciais:\n"
                f"   - ECG (eletrocardiograma) - alterações de ST\n"
                f"   - Troponina - marcador de lesão miocárdica\n"
                f"   - CK-MB - enzima cardíaca\n\n"
                f"d) Fatores de risco presentes:\n"
                f"   1. Tabagismo\n"
                f"   2. Diabetes mellitus\n"
                f"   3. Sexo masculino e idade > 55 anos"
            )
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Anatomia e Fisiologia",
            "dificuldade": dificuldade,
            "topico": "medicina"
        }
        
        log_questao_gerada("biologia")
        return resultado

    # =========================================================================
    # BIOLOGIA CELULAR
    # =========================================================================
    
    def gerar_questao_celula(self, dificuldade: str = "medio", com_diagrama: bool = False) -> dict:
        """Gera questão sobre Biologia Celular."""
        
        if dificuldade == "facil":
            organela = random.choice(list(ORGANELAS.keys()))
            info = ORGANELAS[organela]
            
            nome_formatado = organela.replace("_", " ").title()
            
            enunciado = f"Qual a principal função da organela {nome_formatado}?"
            resposta = f"A {nome_formatado} é responsável por: {info['funcao']}"
            
        elif dificuldade == "medio":
            organelas = random.sample(list(ORGANELAS.keys()), 3)
            
            enunciado = (
                f"Compare as seguintes organelas celulares quanto à sua estrutura e função:\n"
                f"a) {organelas[0].replace('_', ' ').title()}\n"
                f"b) {organelas[1].replace('_', ' ').title()}\n"
                f"c) {organelas[2].replace('_', ' ').title()}"
            )
            
            resposta = ""
            for org in organelas:
                info = ORGANELAS[org]
                nome = org.replace('_', ' ').title()
                resposta += f"{nome}:\n"
                resposta += f"  - Membrana: {info['membrana']}\n"
                resposta += f"  - Função: {info['funcao']}\n\n"
            
        else:  # dificil
            enunciado = (
                f"Uma célula muscular em intensa atividade física apresenta aumento "
                f"significativo da demanda energética.\n\n"
                f"a) Qual organela é a principal responsável pela produção de ATP?\n"
                f"b) Descreva as etapas da respiração celular e onde cada uma ocorre;\n"
                f"c) Por que células musculares possuem mais dessa organela?\n"
                f"d) O que acontece quando a demanda de O₂ supera a oferta?"
            )
            
            resposta = (
                f"a) Mitocôndria - 'usina energética da célula'\n\n"
                f"b) Etapas da respiração celular:\n"
                f"   1. Glicólise (citoplasma): glicose → 2 piruvatos + 2 ATP\n"
                f"   2. Ciclo de Krebs (matriz mitocondrial): acetil-CoA → CO₂ + NADH/FADH₂\n"
                f"   3. Cadeia respiratória (cristas mitocondriais): NADH/FADH₂ → 32-34 ATP\n\n"
                f"c) Células musculares têm alta demanda energética para contração,\n"
                f"   por isso possuem mais mitocôndrias (até milhares por célula).\n\n"
                f"d) Quando falta O₂ (anaerobiose):\n"
                f"   - Ocorre fermentação lática (músculo): piruvato → lactato\n"
                f"   - Produz apenas 2 ATP por glicose (vs 36-38 na aerobiose)\n"
                f"   - Acúmulo de lactato causa fadiga muscular"
            )
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Biologia Celular",
            "dificuldade": dificuldade,
            "topico": "celular"
        }
        
        log_questao_gerada("biologia")
        return resultado

    # =========================================================================
    # GENÉTICA
    # =========================================================================
    
    def gerar_questao_genetica(self, dificuldade: str = "medio", com_diagrama: bool = False) -> dict:
        """Gera questão sobre Genética."""
        
        if dificuldade == "facil":
            # Dominância simples
            caracteristicas = [
                ("olhos castanhos", "C", "olhos azuis", "c"),
                ("cabelo crespo", "A", "cabelo liso", "a"),
                ("lobo da orelha solto", "L", "lobo da orelha preso", "l"),
            ]
            carac = random.choice(caracteristicas)
            
            enunciado = (
                f"Em uma espécie, o gene para {carac[0]} ({carac[1]}) é dominante sobre "
                f"{carac[2]} ({carac[3]}). Se cruzarmos dois indivíduos heterozigotos ({carac[1]}{carac[3]}), "
                f"qual a proporção fenotípica esperada na prole?"
            )
            
            resposta = (
                f"Cruzamento: {carac[1]}{carac[3]} × {carac[1]}{carac[3]}\n\n"
                f"Quadro de Punnett:\n"
                f"        {carac[1]}      {carac[3]}\n"
                f"  {carac[1]}   {carac[1]}{carac[1]}    {carac[1]}{carac[3]}\n"
                f"  {carac[3]}   {carac[1]}{carac[3]}    {carac[3]}{carac[3]}\n\n"
                f"Proporção genotípica: 1 {carac[1]}{carac[1]} : 2 {carac[1]}{carac[3]} : 1 {carac[3]}{carac[3]}\n"
                f"Proporção fenotípica: 3 {carac[0]} : 1 {carac[2]} (75% : 25%)"
            )
            
        elif dificuldade == "medio":
            # Segunda Lei de Mendel (diibridismo)
            enunciado = (
                f"Em ervilhas, a cor amarela (V) domina sobre verde (v) e a textura lisa (R) "
                f"domina sobre rugosa (r). Cruzando-se plantas duplo-heterozigotas (VvRr × VvRr):\n"
                f"a) Qual a proporção fenotípica esperada?\n"
                f"b) Qual a probabilidade de nascer uma ervilha verde e lisa?\n"
                f"c) Quantos genótipos diferentes são possíveis?"
            )
            
            resposta = (
                f"a) Proporção fenotípica (9:3:3:1):\n"
                f"   - 9/16 amarelas e lisas (V_R_)\n"
                f"   - 3/16 amarelas e rugosas (V_rr)\n"
                f"   - 3/16 verdes e lisas (vvR_)\n"
                f"   - 1/16 verdes e rugosas (vvrr)\n\n"
                f"b) Verde e lisa (vvR_):\n"
                f"   P(vv) × P(R_) = 1/4 × 3/4 = 3/16\n\n"
                f"c) Genótipos possíveis: 9\n"
                f"   VV ou Vv ou vv (3) × RR ou Rr ou rr (3) = 9 combinações"
            )
            
        else:  # dificil
            # Herança ligada ao sexo ou problema de heredograma
            enunciado = (
                f"A hemofilia é uma doença recessiva ligada ao cromossomo X. "
                f"Considere o seguinte heredograma:\n\n"
                f"Geração I:   Pai normal (I-1) × Mãe portadora (I-2)\n"
                f"Geração II:  Filho hemofílico (II-1), Filha normal (II-2)\n\n"
                f"a) Quais os genótipos de todos os indivíduos?\n"
                f"b) Se II-2 casar com um homem normal, qual a probabilidade de ter:\n"
                f"   - Um filho hemofílico?\n"
                f"   - Uma filha portadora?\n"
                f"c) Por que a hemofilia é mais comum em homens?"
            )
            
            resposta = (
                f"a) Genótipos:\n"
                f"   I-1 (pai normal): XᴴY\n"
                f"   I-2 (mãe portadora): XᴴXʰ\n"
                f"   II-1 (filho hemofílico): XʰY\n"
                f"   II-2 (filha normal): XᴴXᴴ ou XᴴXʰ (50% de chance cada)\n\n"
                f"b) Se II-2 for portadora (XᴴXʰ) × homem normal (XᴴY):\n"
                f"   - Filho hemofílico (XʰY): 1/4 dos filhos = 25%\n"
                f"     Considerando 50% de II-2 ser portadora: 1/2 × 1/4 = 1/8 = 12,5%\n"
                f"   - Filha portadora (XᴴXʰ): 1/4 das filhas = 25%\n"
                f"     Total: 1/2 × 1/4 = 12,5%\n\n"
                f"c) A hemofilia é mais comum em homens porque:\n"
                f"   - Homens têm apenas 1 cromossomo X (XY)\n"
                f"   - Basta 1 alelo recessivo para manifestar a doença\n"
                f"   - Mulheres precisam de 2 alelos (XʰXʰ), muito mais raro"
            )
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Genética",
            "dificuldade": dificuldade,
            "topico": "genetica"
        }
        
        log_questao_gerada("biologia")
        return resultado

    # =========================================================================
    # MICROBIOLOGIA E IMUNOLOGIA
    # =========================================================================
    
    def gerar_questao_microbiologia(self, dificuldade: str = "medio", com_diagrama: bool = False) -> dict:
        """Gera questão sobre Microbiologia e Imunologia."""
        
        if dificuldade == "facil":
            microorganismos = [
                ("Bactérias", "procariontes", "parede celular de peptidoglicano", "antibióticos"),
                ("Vírus", "acelulares", "cápsula proteica e ácido nucleico", "antivirais"),
                ("Fungos", "eucariontes", "parede celular de quitina", "antifúngicos"),
            ]
            micro = random.choice(microorganismos)
            
            enunciado = (
                f"Os {micro[0]} são microrganismos classificados como {micro[1]}. "
                f"Qual a principal característica estrutural desse grupo e qual classe "
                f"de medicamentos é usada no seu tratamento?"
            )
            resposta = (
                f"Característica: {micro[2]}\n"
                f"Tratamento: {micro[3]}"
            )
            
        elif dificuldade == "medio":
            enunciado = (
                f"Sobre o sistema imunológico, compare:\n"
                f"a) Imunidade inata vs. imunidade adaptativa;\n"
                f"b) Resposta humoral vs. resposta celular;\n"
                f"c) Qual o papel dos linfócitos T e B?"
            )
            
            resposta = (
                f"a) Imunidade inata vs. adaptativa:\n"
                f"   Inata: rápida, inespecífica, sem memória (barreiras, fagócitos)\n"
                f"   Adaptativa: lenta, específica, com memória (linfócitos)\n\n"
                f"b) Resposta humoral vs. celular:\n"
                f"   Humoral: mediada por anticorpos (linfócitos B)\n"
                f"   Celular: mediada por células T citotóxicas\n\n"
                f"c) Papel dos linfócitos:\n"
                f"   Linfócitos B: produzem anticorpos, memória humoral\n"
                f"   Linfócitos T: T helper (coordenam), T citotóxicos (destroem células infectadas)"
            )
            
        else:  # dificil
            enunciado = (
                f"Um paciente apresenta infecção bacteriana recorrente. O antibiograma mostra "
                f"resistência a múltiplos antibióticos.\n\n"
                f"a) Explique os mecanismos de resistência bacteriana;\n"
                f"b) O que é transferência horizontal de genes e sua importância?\n"
                f"c) Quais medidas podem prevenir a resistência antimicrobiana?\n"
                f"d) O que são 'superbactérias' e cite um exemplo?"
            )
            
            resposta = (
                f"a) Mecanismos de resistência:\n"
                f"   - Produção de enzimas (β-lactamases) que inativam o antibiótico\n"
                f"   - Alteração do sítio de ligação do fármaco\n"
                f"   - Bombas de efluxo que expulsam o antibiótico\n"
                f"   - Redução da permeabilidade da membrana\n\n"
                f"b) Transferência horizontal de genes:\n"
                f"   - Conjugação: transferência de plasmídeos entre bactérias\n"
                f"   - Transformação: captação de DNA livre do ambiente\n"
                f"   - Transdução: transferência via bacteriófagos\n"
                f"   Importância: dissemina rapidamente genes de resistência\n\n"
                f"c) Prevenção da resistência:\n"
                f"   - Uso racional de antibióticos (indicação correta)\n"
                f"   - Completar o tratamento prescrito\n"
                f"   - Higiene das mãos e controle de infecção\n"
                f"   - Vacinação para reduzir infecções\n\n"
                f"d) Superbactérias: bactérias multirresistentes\n"
                f"   Exemplos: MRSA (Staphylococcus aureus resistente à meticilina),\n"
                f"   KPC (Klebsiella produtora de carbapenemase)"
            )
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Microbiologia",
            "dificuldade": dificuldade,
            "topico": "microbiologia"
        }
        
        log_questao_gerada("biologia")
        return resultado

    # =========================================================================
    # ECOLOGIA
    # =========================================================================
    
    def gerar_questao_ecologia(self, dificuldade: str = "medio", com_diagrama: bool = False) -> dict:
        """Gera questão sobre Ecologia."""
        
        if dificuldade == "facil":
            conceitos = [
                ("cadeia alimentar", "sequência linear de transferência de energia entre organismos"),
                ("ecossistema", "conjunto formado pelos seres vivos e o ambiente físico"),
                ("nicho ecológico", "papel funcional de uma espécie no ecossistema"),
                ("habitat", "local onde uma espécie vive"),
            ]
            conceito = random.choice(conceitos)
            
            enunciado = f"Defina o conceito de {conceito[0]} em ecologia."
            resposta = f"{conceito[0].title()}: {conceito[1]}"
            
        elif dificuldade == "medio":
            enunciado = (
                f"Considere a seguinte cadeia alimentar:\n"
                f"Capim → Gafanhoto → Sapo → Cobra → Gavião\n\n"
                f"a) Classifique cada organismo quanto ao nível trófico;\n"
                f"b) Qual organismo é produtor e quais são consumidores?\n"
                f"c) Se houver contaminação por mercúrio, qual organismo será mais afetado? Justifique."
            )
            
            resposta = (
                f"a) Níveis tróficos:\n"
                f"   Capim: 1º nível (produtor)\n"
                f"   Gafanhoto: 2º nível (consumidor primário)\n"
                f"   Sapo: 3º nível (consumidor secundário)\n"
                f"   Cobra: 4º nível (consumidor terciário)\n"
                f"   Gavião: 5º nível (consumidor quaternário)\n\n"
                f"b) Produtor: Capim (realiza fotossíntese)\n"
                f"   Consumidores: todos os animais da cadeia\n\n"
                f"c) O Gavião será mais afetado devido à bioacumulação:\n"
                f"   - O mercúrio não é excretado e se acumula nos tecidos\n"
                f"   - Cada nível trófico concentra mais o poluente\n"
                f"   - Predadores de topo acumulam as maiores concentrações"
            )
            
        else:  # dificil
            enunciado = (
                f"Uma área de floresta tropical foi desmatada para agricultura. "
                f"Após 20 anos, a área foi abandonada.\n\n"
                f"a) Descreva o processo de sucessão ecológica que ocorrerá;\n"
                f"b) Diferencie sucessão primária de secundária. Qual ocorre nesse caso?\n"
                f"c) O que é comunidade clímax?\n"
                f"d) Quais serviços ecossistêmicos foram perdidos com o desmatamento?"
            )
            
            resposta = (
                f"a) Sucessão ecológica:\n"
                f"   1. Estágio pioneiro: gramíneas e herbáceas colonizam\n"
                f"   2. Estágio intermediário: arbustos e árvores de crescimento rápido\n"
                f"   3. Estágio tardio: árvores de grande porte, maior biodiversidade\n"
                f"   4. Clímax: floresta madura estável (pode levar décadas/séculos)\n\n"
                f"b) Primária: ocorre em área sem vida anterior (rocha nua)\n"
                f"   Secundária: ocorre em área já colonizada anteriormente\n"
                f"   Neste caso: SECUNDÁRIA (solo e banco de sementes existem)\n\n"
                f"c) Comunidade clímax:\n"
                f"   - Estágio final e estável da sucessão\n"
                f"   - Máxima biodiversidade e complexidade\n"
                f"   - Produção ≈ Consumo (equilíbrio dinâmico)\n\n"
                f"d) Serviços ecossistêmicos perdidos:\n"
                f"   - Sequestro de carbono\n"
                f"   - Regulação do ciclo hidrológico\n"
                f"   - Manutenção da biodiversidade\n"
                f"   - Controle de erosão\n"
                f"   - Polinização e dispersão de sementes"
            )
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Ecologia",
            "dificuldade": dificuldade,
            "topico": "ecologia"
        }
        
        log_questao_gerada("biologia")
        return resultado

    # =========================================================================
    # MÉTODO PRINCIPAL - Roteador de tópicos
    # =========================================================================
    
    def gerar_questao(self, topico: str = "farmacologia", dificuldade: str = "medio", 
                      com_diagrama: bool = False) -> dict:
        """
        Gera uma questão de biologia baseada no tópico e dificuldade.
        
        Args:
            topico: Tópico da questão
            dificuldade: facil, medio ou dificil
            com_diagrama: Se True, gera diagrama junto com a questão
        
        Returns:
            Dicionário com a questão gerada
        """
        topico_lower = topico.lower().replace("_", " ").replace("-", " ")
        
        # Farmacêutica
        if topico_lower in ["farmacologia", "farmaceutica", "medicamentos", "farmacos", "drogas"]:
            return self.gerar_questao_farmacologia(dificuldade, com_diagrama)
        
        # Medicina
        elif topico_lower in ["anatomia", "fisiologia", "medicina", "corpo humano", "sistemas"]:
            return self.gerar_questao_anatomia(dificuldade, com_diagrama)
        
        # Biologia Celular
        elif topico_lower in ["celula", "celular", "organelas", "citologia"]:
            return self.gerar_questao_celula(dificuldade, com_diagrama)
        
        # Genética
        elif topico_lower in ["genetica", "dna", "hereditariedade", "genes", "cromossomos"]:
            return self.gerar_questao_genetica(dificuldade, com_diagrama)
        
        # Microbiologia
        elif topico_lower in ["microbiologia", "bacterias", "virus", "fungos", "imunologia"]:
            return self.gerar_questao_microbiologia(dificuldade, com_diagrama)
        
        # Ecologia
        elif topico_lower in ["ecologia", "ecossistema", "meio ambiente", "cadeia alimentar"]:
            return self.gerar_questao_ecologia(dificuldade, com_diagrama)
        
        # Padrão: escolhe aleatoriamente
        else:
            metodos = [
                self.gerar_questao_farmacologia,
                self.gerar_questao_anatomia,
                self.gerar_questao_celula,
                self.gerar_questao_genetica,
                self.gerar_questao_microbiologia,
                self.gerar_questao_ecologia
            ]
            metodo = random.choice(metodos)
            return metodo(dificuldade, com_diagrama)

