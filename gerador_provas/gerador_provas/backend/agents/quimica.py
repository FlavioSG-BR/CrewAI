import random
from crewai import Agent
from backend.utils.logger import log_questao_gerada

# Dados dos elementos químicos
ELEMENTOS = {
    "H": {"nome": "Hidrogênio", "num_atomico": 1, "massa": 1.008, "eletrons": 1},
    "He": {"nome": "Hélio", "num_atomico": 2, "massa": 4.003, "eletrons": 2},
    "Li": {"nome": "Lítio", "num_atomico": 3, "massa": 6.941, "eletrons": 3},
    "Be": {"nome": "Berílio", "num_atomico": 4, "massa": 9.012, "eletrons": 4},
    "B": {"nome": "Boro", "num_atomico": 5, "massa": 10.81, "eletrons": 5},
    "C": {"nome": "Carbono", "num_atomico": 6, "massa": 12.01, "eletrons": 6},
    "N": {"nome": "Nitrogênio", "num_atomico": 7, "massa": 14.01, "eletrons": 7},
    "O": {"nome": "Oxigênio", "num_atomico": 8, "massa": 16.00, "eletrons": 8},
    "F": {"nome": "Flúor", "num_atomico": 9, "massa": 19.00, "eletrons": 9},
    "Ne": {"nome": "Neônio", "num_atomico": 10, "massa": 20.18, "eletrons": 10},
    "Na": {"nome": "Sódio", "num_atomico": 11, "massa": 22.99, "eletrons": 11},
    "Mg": {"nome": "Magnésio", "num_atomico": 12, "massa": 24.31, "eletrons": 12},
    "Al": {"nome": "Alumínio", "num_atomico": 13, "massa": 26.98, "eletrons": 13},
    "Si": {"nome": "Silício", "num_atomico": 14, "massa": 28.09, "eletrons": 14},
    "P": {"nome": "Fósforo", "num_atomico": 15, "massa": 30.97, "eletrons": 15},
    "S": {"nome": "Enxofre", "num_atomico": 16, "massa": 32.07, "eletrons": 16},
    "Cl": {"nome": "Cloro", "num_atomico": 17, "massa": 35.45, "eletrons": 17},
    "Ar": {"nome": "Argônio", "num_atomico": 18, "massa": 39.95, "eletrons": 18},
    "K": {"nome": "Potássio", "num_atomico": 19, "massa": 39.10, "eletrons": 19},
    "Ca": {"nome": "Cálcio", "num_atomico": 20, "massa": 40.08, "eletrons": 20},
    "Fe": {"nome": "Ferro", "num_atomico": 26, "massa": 55.85, "eletrons": 26},
    "Cu": {"nome": "Cobre", "num_atomico": 29, "massa": 63.55, "eletrons": 29},
    "Zn": {"nome": "Zinco", "num_atomico": 30, "massa": 65.38, "eletrons": 30},
    "Ag": {"nome": "Prata", "num_atomico": 47, "massa": 107.87, "eletrons": 47},
    "Au": {"nome": "Ouro", "num_atomico": 79, "massa": 196.97, "eletrons": 79},
}


class AgenteQuimica:
    """Agente especializado em questões de Química."""
    
    def __init__(self):
        self.agent = Agent(
            role="Professor de Química",
            goal="Elaborar questões sobre tabela periódica, ligações e reações",
            backstory="Especialista em Química com 10 anos de experiência em ensino",
            allow_delegation=False
        )
        self._gerador_imagens = None
    
    def _get_gerador_imagens(self):
        """Lazy loading do gerador de imagens."""
        if self._gerador_imagens is None:
            from backend.agents.imagens import AgenteImagens
            self._gerador_imagens = AgenteImagens()
        return self._gerador_imagens

    def gerar_questao_tabela_periodica(self, com_diagrama: bool = False) -> dict:
        """
        Gera questão sobre elementos da tabela periódica.
        
        Args:
            com_diagrama: Se True, gera diagrama do elemento
        
        Returns:
            Dicionário com enunciado, resposta, tipo e opcionalmente diagrama
        """
        # Escolhe um elemento aleatório
        simbolo = random.choice(list(ELEMENTOS.keys()))
        elemento = ELEMENTOS[simbolo]
        
        # Tipos de pergunta
        tipo_pergunta = random.choice(["num_atomico", "massa", "nome", "eletrons"])
        
        if tipo_pergunta == "num_atomico":
            enunciado = f"Qual é o número atômico do elemento {elemento['nome']} ({simbolo})?"
            resposta = f"O número atômico do {elemento['nome']} é {elemento['num_atomico']}."
        
        elif tipo_pergunta == "massa":
            enunciado = f"Qual é a massa atômica aproximada do {elemento['nome']}?"
            resposta = f"A massa atômica do {elemento['nome']} é aproximadamente {elemento['massa']} u."
        
        elif tipo_pergunta == "nome":
            enunciado = f"Qual elemento químico tem o símbolo {simbolo}?"
            resposta = f"O símbolo {simbolo} representa o elemento {elemento['nome']}."
        
        else:  # eletrons
            enunciado = f"Quantos elétrons possui um átomo neutro de {elemento['nome']}?"
            resposta = f"Um átomo neutro de {elemento['nome']} possui {elemento['eletrons']} elétrons."
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Tabela Periódica",
            "dados": {
                "simbolo": simbolo,
                "elemento": elemento
            }
        }
        
        if com_diagrama:
            try:
                gerador = self._get_gerador_imagens()
                resultado["diagrama"] = gerador.gerar_tabela_periodica_elemento(
                    simbolo=simbolo,
                    num_atomico=elemento['num_atomico'],
                    massa_atomica=elemento['massa'],
                    nome=elemento['nome']
                )
            except Exception as e:
                resultado["diagrama_erro"] = str(e)
        
        log_questao_gerada("quimica")
        return resultado
    
    def gerar_questao_modelo_atomico(self, com_diagrama: bool = False) -> dict:
        """
        Gera questão sobre modelo atômico.
        
        Args:
            com_diagrama: Se True, gera diagrama do átomo
        
        Returns:
            Dicionário com enunciado, resposta, tipo e opcionalmente diagrama
        """
        # Elementos mais simples para visualização
        elementos_simples = ["H", "He", "Li", "Be", "B", "C", "N", "O", "Ne", "Na"]
        simbolo = random.choice(elementos_simples)
        elemento = ELEMENTOS[simbolo]
        
        enunciado = (
            f"Desenhe o modelo atômico simplificado (modelo de Bohr) para o átomo de "
            f"{elemento['nome']} ({simbolo}), indicando o número de elétrons em cada camada."
        )
        
        # Calcular distribuição eletrônica
        eletrons = elemento['eletrons']
        camadas = []
        restante = eletrons
        max_por_camada = [2, 8, 8, 18]
        
        for max_e in max_por_camada:
            if restante <= 0:
                break
            n = min(restante, max_e)
            camadas.append(n)
            restante -= n
        
        distribuicao = ", ".join([f"K={camadas[0]}" if len(camadas) > 0 else ""] + 
                                  [f"L={camadas[1]}" if len(camadas) > 1 else ""] +
                                  [f"M={camadas[2]}" if len(camadas) > 2 else ""] +
                                  [f"N={camadas[3]}" if len(camadas) > 3 else ""])
        distribuicao = ", ".join([x for x in distribuicao.split(", ") if x])
        
        resposta = (
            f"O átomo de {elemento['nome']} possui {eletrons} elétrons.\n"
            f"Distribuição eletrônica: {distribuicao}"
        )
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Modelo Atômico",
            "dados": {
                "simbolo": simbolo,
                "elemento": elemento,
                "distribuicao": camadas
            }
        }
        
        if com_diagrama:
            try:
                gerador = self._get_gerador_imagens()
                resultado["diagrama"] = gerador.gerar_diagrama_atomo(simbolo, eletrons)
            except Exception as e:
                resultado["diagrama_erro"] = str(e)
        
        log_questao_gerada("quimica")
        return resultado
    
    def gerar_questao_ligacoes(self) -> dict:
        """
        Gera questão sobre ligações químicas.
        
        Returns:
            Dicionário com enunciado, resposta e tipo
        """
        ligacoes = [
            {
                "composto": "NaCl",
                "nome": "Cloreto de Sódio",
                "tipo_ligacao": "iônica",
                "explicacao": "Ocorre transferência de elétrons do Na (metal) para o Cl (não-metal)."
            },
            {
                "composto": "H₂O",
                "nome": "Água",
                "tipo_ligacao": "covalente",
                "explicacao": "Ocorre compartilhamento de elétrons entre H e O (ambos não-metais)."
            },
            {
                "composto": "O₂",
                "nome": "Gás Oxigênio",
                "tipo_ligacao": "covalente",
                "explicacao": "Ocorre compartilhamento de elétrons entre dois átomos de oxigênio."
            },
            {
                "composto": "Fe",
                "nome": "Ferro metálico",
                "tipo_ligacao": "metálica",
                "explicacao": "Os elétrons são compartilhados entre todos os átomos (mar de elétrons)."
            },
            {
                "composto": "CO₂",
                "nome": "Dióxido de Carbono",
                "tipo_ligacao": "covalente",
                "explicacao": "Ocorre compartilhamento de elétrons entre C e O (não-metais)."
            }
        ]
        
        ligacao = random.choice(ligacoes)
        
        enunciado = (
            f"Qual o tipo de ligação química presente no composto {ligacao['composto']} "
            f"({ligacao['nome']})? Justifique sua resposta."
        )
        
        resposta = (
            f"O tipo de ligação é {ligacao['tipo_ligacao'].upper()}.\n"
            f"Justificativa: {ligacao['explicacao']}"
        )
        
        log_questao_gerada("quimica")
        
        return {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Ligações Químicas",
            "dados": ligacao
        }
    
    def gerar_questao_estequiometria(self) -> dict:
        """
        Gera questão sobre estequiometria.
        
        Returns:
            Dicionário com enunciado, resposta e tipo
        """
        reacoes = [
            {
                "equacao": "2H₂ + O₂ → 2H₂O",
                "pergunta": "Quantos mols de água são formados a partir de 4 mols de H₂?",
                "resposta": "4 mols de H₂O",
                "explicacao": "Proporção 2:2, então 4 mols de H₂ produzem 4 mols de H₂O."
            },
            {
                "equacao": "N₂ + 3H₂ → 2NH₃",
                "pergunta": "Quantos mols de NH₃ são produzidos a partir de 6 mols de H₂?",
                "resposta": "4 mols de NH₃",
                "explicacao": "Proporção 3:2, então 6 mols de H₂ produzem 4 mols de NH₃."
            },
            {
                "equacao": "2Na + Cl₂ → 2NaCl",
                "pergunta": "Quantos mols de NaCl são formados a partir de 1 mol de Cl₂?",
                "resposta": "2 mols de NaCl",
                "explicacao": "Proporção 1:2, então 1 mol de Cl₂ produz 2 mols de NaCl."
            }
        ]
        
        reacao = random.choice(reacoes)
        
        enunciado = (
            f"Considere a reação: {reacao['equacao']}\n\n"
            f"{reacao['pergunta']}"
        )
        
        resposta = f"{reacao['resposta']}\n\nExplicação: {reacao['explicacao']}"
        
        log_questao_gerada("quimica")
        
        return {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Estequiometria",
            "dados": reacao
        }
    
    def gerar_questao(self, topico: str = "tabela_periodica", com_diagrama: bool = False) -> dict:
        """
        Gera uma questão de química baseada no tópico.
        
        Args:
            topico: Tópico da questão
            com_diagrama: Se True, gera diagrama junto com a questão
        
        Returns:
            Dicionário com a questão gerada
        """
        topico_lower = topico.lower().replace(" ", "_")
        
        if topico_lower in ["tabela_periodica", "tabela", "elementos"]:
            return self.gerar_questao_tabela_periodica(com_diagrama)
        elif topico_lower in ["modelo_atomico", "atomo", "átomo", "bohr"]:
            return self.gerar_questao_modelo_atomico(com_diagrama)
        elif topico_lower in ["ligacoes", "ligações", "ligacao", "ligação"]:
            return self.gerar_questao_ligacoes()
        elif topico_lower in ["estequiometria", "reacoes", "reações"]:
            return self.gerar_questao_estequiometria()
        else:
            return self.gerar_questao_tabela_periodica(com_diagrama)
