import random
from crewai import Agent, Task
from sympy import symbols, Eq, solve
from backend.utils.logger import log_questao_gerada


class AgenteFisica:
    """Agente especializado em questões de Física."""
    
    def __init__(self):
        self.agent = Agent(
            role="Professor de Física",
            goal="Criar questões sobre mecânica, termodinâmica e ondulatória",
            backstory="Doutor em Física com experiência em Olimpíadas Científicas",
            allow_delegation=False
        )
        self._gerador_imagens = None
    
    def _get_gerador_imagens(self):
        """Lazy loading do gerador de imagens para evitar imports circulares."""
        if self._gerador_imagens is None:
            from backend.agents.imagens import AgenteImagens
            self._gerador_imagens = AgenteImagens()
        return self._gerador_imagens

    def gerar_questao_mru(self, com_diagrama: bool = False) -> dict:
        """
        Gera questão sobre Movimento Retilíneo Uniforme.
        
        Args:
            com_diagrama: Se True, gera um diagrama junto com a questão
        
        Returns:
            Dicionário com enunciado, resposta, tipo e opcionalmente diagrama
        """
        # Valores aleatórios para variar as questões
        velocidade = random.choice([5, 10, 15, 20, 25, 30])
        tempo = random.choice([2, 3, 4, 5, 6, 8, 10])
        
        distancia = velocidade * tempo
        
        enunciado = (
            f"Um carro se move em linha reta com velocidade constante de {velocidade} m/s. "
            f"Calcule a distância percorrida pelo carro em {tempo} segundos."
        )
        
        resposta = f"d = v × t = {velocidade} × {tempo} = {distancia} metros"
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "MRU",
            "formula": "d = v × t",
            "dados": {
                "velocidade": velocidade,
                "tempo": tempo,
                "distancia": distancia
            }
        }
        
        # Gerar diagrama se solicitado
        if com_diagrama:
            try:
                gerador = self._get_gerador_imagens()
                resultado["diagrama"] = gerador.gerar_diagrama_mru(velocidade, tempo)
            except Exception as e:
                resultado["diagrama_erro"] = str(e)
        
        log_questao_gerada("fisica")
        return resultado
    
    def gerar_questao_mruv(self, com_diagrama: bool = False) -> dict:
        """
        Gera questão sobre Movimento Retilíneo Uniformemente Variado.
        
        Args:
            com_diagrama: Se True, gera um diagrama junto com a questão
        
        Returns:
            Dicionário com enunciado, resposta, tipo e opcionalmente diagrama
        """
        v0 = random.choice([0, 5, 10])
        aceleracao = random.choice([2, 3, 4, 5])
        tempo = random.choice([3, 4, 5, 6])
        
        # Velocidade final: v = v0 + a*t
        velocidade_final = v0 + aceleracao * tempo
        
        # Distância: d = v0*t + (a*t²)/2
        distancia = v0 * tempo + (aceleracao * tempo**2) / 2
        
        enunciado = (
            f"Um objeto parte do repouso com velocidade inicial de {v0} m/s "
            f"e acelera uniformemente a {aceleracao} m/s². "
            f"Determine a velocidade final e a distância percorrida após {tempo} segundos."
        )
        
        resposta = (
            f"Velocidade final: v = v₀ + a×t = {v0} + {aceleracao}×{tempo} = {velocidade_final} m/s\n"
            f"Distância: d = v₀×t + (a×t²)/2 = {v0}×{tempo} + ({aceleracao}×{tempo}²)/2 = {distancia} m"
        )
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "MRUV",
            "formulas": ["v = v₀ + a×t", "d = v₀×t + (a×t²)/2"],
            "dados": {
                "v0": v0,
                "aceleracao": aceleracao,
                "tempo": tempo,
                "velocidade_final": velocidade_final,
                "distancia": distancia
            }
        }
        
        if com_diagrama:
            try:
                gerador = self._get_gerador_imagens()
                resultado["diagrama"] = gerador.gerar_diagrama_mruv(v0, aceleracao, tempo)
            except Exception as e:
                resultado["diagrama_erro"] = str(e)
        
        log_questao_gerada("fisica")
        return resultado
    
    def gerar_questao_forca(self, com_diagrama: bool = False) -> dict:
        """
        Gera questão sobre Forças (Segunda Lei de Newton).
        
        Args:
            com_diagrama: Se True, gera um diagrama de forças
        
        Returns:
            Dicionário com enunciado, resposta, tipo e opcionalmente diagrama
        """
        massa = random.choice([2, 5, 10, 15, 20])
        aceleracao = random.choice([2, 3, 4, 5])
        
        forca = massa * aceleracao
        
        enunciado = (
            f"Um bloco de massa {massa} kg está sobre uma superfície sem atrito. "
            f"Determine a força necessária para acelerá-lo a {aceleracao} m/s²."
        )
        
        resposta = f"F = m × a = {massa} × {aceleracao} = {forca} N"
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Forças",
            "formula": "F = m × a",
            "dados": {
                "massa": massa,
                "aceleracao": aceleracao,
                "forca": forca
            }
        }
        
        if com_diagrama:
            try:
                gerador = self._get_gerador_imagens()
                forcas = [
                    ("Peso (P)", massa * 10, 270),
                    ("Normal (N)", massa * 10, 90),
                    ("Força (F)", forca, 0)
                ]
                resultado["diagrama"] = gerador.gerar_diagrama_forcas(forcas)
            except Exception as e:
                resultado["diagrama_erro"] = str(e)
        
        log_questao_gerada("fisica")
        return resultado
    
    def gerar_questao_circuito(self, com_diagrama: bool = False) -> dict:
        """
        Gera questão sobre Circuitos Elétricos (Lei de Ohm).
        
        Args:
            com_diagrama: Se True, gera um diagrama do circuito
        
        Returns:
            Dicionário com enunciado, resposta, tipo e opcionalmente diagrama
        """
        tensao = random.choice([6, 9, 12, 24])
        resistencia = random.choice([2, 4, 6, 8, 10, 12])
        
        corrente = tensao / resistencia
        
        enunciado = (
            f"Um circuito elétrico simples possui uma fonte de tensão de {tensao} V "
            f"e um resistor de {resistencia} Ω. Calcule a corrente elétrica no circuito."
        )
        
        resposta = f"I = V / R = {tensao} / {resistencia} = {corrente:.2f} A"
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Circuitos Elétricos",
            "formula": "V = R × I (Lei de Ohm)",
            "dados": {
                "tensao": tensao,
                "resistencia": resistencia,
                "corrente": corrente
            }
        }
        
        if com_diagrama:
            try:
                gerador = self._get_gerador_imagens()
                resultado["diagrama"] = gerador.gerar_diagrama_circuito_simples(resistencia, tensao)
            except Exception as e:
                resultado["diagrama_erro"] = str(e)
        
        log_questao_gerada("fisica")
        return resultado
    
    def gerar_questao(self, topico: str = "mru", com_diagrama: bool = False) -> dict:
        """
        Gera uma questão de física baseada no tópico.
        
        Args:
            topico: Tópico da questão (mru, mruv, forca, circuito)
            com_diagrama: Se True, gera diagrama junto com a questão
        
        Returns:
            Dicionário com a questão gerada
        """
        topico_lower = topico.lower()
        
        if topico_lower in ["mru", "movimento uniforme"]:
            return self.gerar_questao_mru(com_diagrama)
        elif topico_lower in ["mruv", "movimento variado"]:
            return self.gerar_questao_mruv(com_diagrama)
        elif topico_lower in ["forca", "força", "forcas", "forças"]:
            return self.gerar_questao_forca(com_diagrama)
        elif topico_lower in ["circuito", "eletricidade", "ohm"]:
            return self.gerar_questao_circuito(com_diagrama)
        else:
            # Padrão: MRU
            return self.gerar_questao_mru(com_diagrama)
