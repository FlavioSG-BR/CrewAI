"""
Agente de Física - Gerador de questões de Física.

Tópicos disponíveis:
- Mecânica: MRU, MRUV, Queda Livre, Lançamento
- Dinâmica: Força, Leis de Newton, Atrito, Trabalho e Energia
- Ondulatória: Ondas, Som, Luz
- Eletricidade: Circuitos, Lei de Ohm
- Termodinâmica: Calor, Temperatura, Dilatação
"""

import random
import math
from typing import Literal
from crewai import Agent
from backend.utils.logger import log_questao_gerada


class AgenteFisica:
    """Agente especializado em questões de Física."""
    
    # Constantes físicas
    G = 10  # Gravidade (m/s²)
    C_AGUA = 1  # Calor específico da água (cal/g°C)
    C_GELO = 0.5  # Calor específico do gelo (cal/g°C)
    L_FUSAO = 80  # Calor latente de fusão do gelo (cal/g)
    VELOCIDADE_SOM = 340  # Velocidade do som no ar (m/s)
    VELOCIDADE_LUZ = 3e8  # Velocidade da luz (m/s)
    
    def __init__(self):
        self.agent = Agent(
            role="Professor de Física",
            goal="Criar questões sobre mecânica, termodinâmica, ondulatória e eletricidade",
            backstory="Doutor em Física com experiência em Olimpíadas Científicas e vestibulares",
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
    # MECÂNICA - MRU
    # =========================================================================
    
    def gerar_questao_mru(self, dificuldade: str = "medio", com_diagrama: bool = False) -> dict:
        """Gera questão sobre Movimento Retilíneo Uniforme."""
        
        if dificuldade == "facil":
            velocidade = random.choice([10, 20, 30])
            tempo = random.choice([2, 5, 10])
            distancia = velocidade * tempo
            
            enunciado = (
                f"Um carro se move com velocidade constante de {velocidade} m/s. "
                f"Qual a distância percorrida em {tempo} segundos?"
            )
            resposta = f"d = v × t = {velocidade} × {tempo} = {distancia} m"
            
        elif dificuldade == "medio":
            v1 = random.choice([40, 60, 80])  # km/h
            tempo = random.choice([2, 3, 4])  # horas
            distancia = v1 * tempo
            
            enunciado = (
                f"Um veículo percorre uma estrada com velocidade constante de {v1} km/h. "
                f"Após {tempo} horas de viagem, qual a distância total percorrida? "
                f"Expresse também em metros."
            )
            resposta = (
                f"d = v × t = {v1} × {tempo} = {distancia} km\n"
                f"Em metros: {distancia} × 1000 = {distancia * 1000} m"
            )
            
        else:  # dificil
            v1 = random.choice([60, 72, 90])  # km/h
            v1_ms = v1 / 3.6
            d1 = random.choice([100, 150, 200])  # km primeira parte
            d2 = random.choice([80, 120, 160])  # km segunda parte
            v2 = random.choice([80, 100, 120])  # km/h segunda parte
            
            t1 = d1 / v1
            t2 = d2 / v2
            total_dist = d1 + d2
            total_tempo = t1 + t2
            vm = total_dist / total_tempo
            
            enunciado = (
                f"Um motorista viaja de uma cidade A até B percorrendo {d1} km a {v1} km/h. "
                f"Em seguida, viaja de B até C percorrendo mais {d2} km a {v2} km/h. "
                f"Calcule: a) O tempo total de viagem; b) A velocidade média no percurso A-C."
            )
            resposta = (
                f"a) Tempo A→B: t₁ = d₁/v₁ = {d1}/{v1} = {t1:.2f} h\n"
                f"   Tempo B→C: t₂ = d₂/v₂ = {d2}/{v2} = {t2:.2f} h\n"
                f"   Tempo total: t = t₁ + t₂ = {t1:.2f} + {t2:.2f} = {total_tempo:.2f} h\n\n"
                f"b) Velocidade média: Vm = Δs/Δt = {total_dist}/{total_tempo:.2f} = {vm:.2f} km/h"
            )
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "MRU",
            "dificuldade": dificuldade,
            "topico": "mecanica"
        }
        
        if com_diagrama:
            try:
                gerador = self._get_gerador_imagens()
                resultado["diagrama"] = gerador.gerar_diagrama_mru(30, 5)
            except Exception as e:
                resultado["diagrama_erro"] = str(e)
        
        log_questao_gerada("fisica")
        return resultado

    # =========================================================================
    # MECÂNICA - MRUV
    # =========================================================================
    
    def gerar_questao_mruv(self, dificuldade: str = "medio", com_diagrama: bool = False) -> dict:
        """Gera questão sobre Movimento Retilíneo Uniformemente Variado."""
        
        if dificuldade == "facil":
            v0 = 0
            a = random.choice([2, 4, 5])
            t = random.choice([4, 5, 6])
            vf = v0 + a * t
            
            enunciado = (
                f"Um carro parte do repouso e acelera a {a} m/s². "
                f"Qual sua velocidade após {t} segundos?"
            )
            resposta = f"v = v₀ + a×t = 0 + {a}×{t} = {vf} m/s"
            
        elif dificuldade == "medio":
            v0 = random.choice([10, 15, 20])
            a = random.choice([2, 3, 4])
            t = random.choice([5, 6, 8])
            vf = v0 + a * t
            d = v0 * t + (a * t**2) / 2
            
            enunciado = (
                f"Um veículo com velocidade inicial de {v0} m/s acelera uniformemente a {a} m/s². "
                f"Após {t} segundos, determine: a) A velocidade final; b) A distância percorrida."
            )
            resposta = (
                f"a) v = v₀ + a×t = {v0} + {a}×{t} = {vf} m/s\n"
                f"b) d = v₀×t + (a×t²)/2 = {v0}×{t} + ({a}×{t}²)/2 = {d:.1f} m"
            )
            
        else:  # dificil
            v0 = random.choice([72, 90, 108])  # km/h
            v0_ms = v0 / 3.6
            vf = 0  # Para até parar
            d = random.choice([50, 100, 150])
            
            # v² = v₀² + 2ad → a = (v² - v₀²) / 2d
            a = (vf**2 - v0_ms**2) / (2 * d)
            t = (vf - v0_ms) / a
            
            enunciado = (
                f"Um carro a {v0} km/h aciona os freios e para após percorrer {d} m. "
                f"Considerando o movimento uniformemente variado, calcule:\n"
                f"a) A aceleração (desaceleração) do veículo;\n"
                f"b) O tempo de frenagem;\n"
                f"c) A velocidade quando faltavam {d//2} m para parar."
            )
            
            v_meio = math.sqrt(v0_ms**2 + 2 * a * (d/2))
            
            resposta = (
                f"Dados: v₀ = {v0} km/h = {v0_ms:.1f} m/s, v = 0, d = {d} m\n\n"
                f"a) Usando v² = v₀² + 2ad:\n"
                f"   0 = {v0_ms:.1f}² + 2×a×{d}\n"
                f"   a = -{v0_ms:.1f}²/(2×{d}) = {a:.2f} m/s²\n\n"
                f"b) Usando v = v₀ + at:\n"
                f"   0 = {v0_ms:.1f} + ({a:.2f})×t\n"
                f"   t = {abs(t):.2f} s\n\n"
                f"c) Quando faltam {d//2} m, percorreu {d//2} m:\n"
                f"   v² = {v0_ms:.1f}² + 2×({a:.2f})×{d//2}\n"
                f"   v = {v_meio:.2f} m/s = {v_meio*3.6:.1f} km/h"
            )
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "MRUV",
            "dificuldade": dificuldade,
            "topico": "mecanica"
        }
        
        if com_diagrama:
            try:
                gerador = self._get_gerador_imagens()
                resultado["diagrama"] = gerador.gerar_diagrama_mruv(10, 2, 5)
            except Exception as e:
                resultado["diagrama_erro"] = str(e)
        
        log_questao_gerada("fisica")
        return resultado

    # =========================================================================
    # MECÂNICA - Queda Livre
    # =========================================================================
    
    def gerar_questao_queda_livre(self, dificuldade: str = "medio", com_diagrama: bool = False) -> dict:
        """Gera questão sobre Queda Livre."""
        
        if dificuldade == "facil":
            t = random.choice([2, 3, 4])
            h = (self.G * t**2) / 2
            v = self.G * t
            
            enunciado = (
                f"Um objeto é abandonado do repouso. Considerando g = {self.G} m/s², "
                f"qual a velocidade e a altura de queda após {t} segundos?"
            )
            resposta = (
                f"v = g×t = {self.G}×{t} = {v} m/s\n"
                f"h = g×t²/2 = {self.G}×{t}²/2 = {h} m"
            )
            
        elif dificuldade == "medio":
            h = random.choice([45, 80, 125, 180])
            t = math.sqrt(2 * h / self.G)
            v = self.G * t
            
            enunciado = (
                f"Uma pedra é solta do topo de um prédio de {h} m de altura. "
                f"Considerando g = {self.G} m/s² e desprezando a resistência do ar, calcule:\n"
                f"a) O tempo de queda;\n"
                f"b) A velocidade ao atingir o solo."
            )
            resposta = (
                f"a) h = g×t²/2 → t = √(2h/g) = √(2×{h}/{self.G}) = {t:.2f} s\n"
                f"b) v = g×t = {self.G}×{t:.2f} = {v:.1f} m/s"
            )
            
        else:  # dificil
            h_total = random.choice([100, 125, 180])
            t_total = math.sqrt(2 * h_total / self.G)
            t1 = t_total / 2  # Meio do percurso em tempo
            h1 = (self.G * t1**2) / 2
            h2 = h_total - h1
            
            enunciado = (
                f"Um objeto é abandonado de uma altura de {h_total} m. "
                f"Considerando g = {self.G} m/s², determine:\n"
                f"a) O tempo total de queda;\n"
                f"b) A velocidade ao atingir o solo;\n"
                f"c) A que altura o objeto estava quando atingiu metade do tempo de queda;\n"
                f"d) Qual distância ele percorreu na segunda metade do tempo?"
            )
            
            v_final = self.G * t_total
            
            resposta = (
                f"a) t = √(2h/g) = √(2×{h_total}/{self.G}) = {t_total:.2f} s\n\n"
                f"b) v = g×t = {self.G}×{t_total:.2f} = {v_final:.1f} m/s\n\n"
                f"c) Na metade do tempo (t = {t1:.2f} s):\n"
                f"   h₁ = g×t₁²/2 = {self.G}×{t1:.2f}²/2 = {h1:.1f} m (distância percorrida)\n"
                f"   Altura restante: {h_total} - {h1:.1f} = {h2:.1f} m\n\n"
                f"d) Segunda metade: h₂ = {h_total} - {h1:.1f} = {h2:.1f} m\n"
                f"   Note: Na queda livre, percorre-se 3× mais na 2ª metade do tempo!"
            )
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Queda Livre",
            "dificuldade": dificuldade,
            "topico": "mecanica"
        }
        
        log_questao_gerada("fisica")
        return resultado

    # =========================================================================
    # DINÂMICA - Forças
    # =========================================================================
    
    def gerar_questao_forca(self, dificuldade: str = "medio", com_diagrama: bool = False) -> dict:
        """Gera questão sobre Forças e Leis de Newton."""
        
        if dificuldade == "facil":
            m = random.choice([2, 5, 10])
            a = random.choice([2, 3, 4])
            F = m * a
            
            enunciado = (
                f"Uma força é aplicada a um bloco de {m} kg, produzindo aceleração de {a} m/s². "
                f"Qual o valor da força?"
            )
            resposta = f"F = m×a = {m}×{a} = {F} N"
            
        elif dificuldade == "medio":
            m = random.choice([5, 10, 20])
            F = random.choice([30, 50, 80])
            mu = random.choice([0.2, 0.3, 0.4])
            
            peso = m * self.G
            fat = mu * peso
            Fr = F - fat
            a = Fr / m
            
            enunciado = (
                f"Um bloco de {m} kg é puxado por uma força horizontal de {F} N "
                f"sobre uma superfície com coeficiente de atrito μ = {mu}. "
                f"Considerando g = {self.G} m/s², calcule a aceleração do bloco."
            )
            resposta = (
                f"Peso: P = m×g = {m}×{self.G} = {peso} N\n"
                f"Normal: N = P = {peso} N\n"
                f"Atrito: Fat = μ×N = {mu}×{peso} = {fat} N\n"
                f"Força resultante: Fr = F - Fat = {F} - {fat} = {Fr} N\n"
                f"Aceleração: a = Fr/m = {Fr}/{m} = {a:.1f} m/s²"
            )
            
        else:  # dificil
            m1 = random.choice([3, 4, 5])
            m2 = random.choice([2, 3, 4])
            theta = random.choice([30, 45, 60])
            theta_rad = math.radians(theta)
            
            # Sistema de dois blocos com plano inclinado
            # m1 no plano inclinado, m2 pendurado
            g = self.G
            
            # Aceleração do sistema: a = (m2×g - m1×g×sin(θ)) / (m1 + m2)
            a = (m2 * g - m1 * g * math.sin(theta_rad)) / (m1 + m2)
            
            # Tensão: T = m2×(g - a)
            T = m2 * (g - a)
            
            enunciado = (
                f"Dois blocos estão conectados por um fio ideal passando por uma polia sem atrito. "
                f"O bloco de massa m₁ = {m1} kg está sobre um plano inclinado de {theta}° (sem atrito) "
                f"e o bloco de massa m₂ = {m2} kg está pendurado verticalmente. "
                f"Dados: g = {self.G} m/s², sen({theta}°) = {math.sin(theta_rad):.2f}. "
                f"Calcule:\na) A aceleração do sistema;\nb) A tensão no fio."
            )
            resposta = (
                f"Analisando as forças:\n"
                f"- Bloco m₁: T - m₁×g×sen(θ) = m₁×a\n"
                f"- Bloco m₂: m₂×g - T = m₂×a\n\n"
                f"Somando as equações:\n"
                f"m₂×g - m₁×g×sen(θ) = (m₁ + m₂)×a\n"
                f"a = ({m2}×{g} - {m1}×{g}×{math.sin(theta_rad):.2f}) / ({m1} + {m2})\n"
                f"a = {a:.2f} m/s²\n\n"
                f"Tensão: T = m₂×(g - a) = {m2}×({g} - {a:.2f}) = {T:.2f} N"
            )
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Forças",
            "dificuldade": dificuldade,
            "topico": "dinamica"
        }
        
        if com_diagrama:
            try:
                gerador = self._get_gerador_imagens()
                resultado["diagrama"] = gerador.gerar_diagrama_forcas([("F", 50, 0)])
            except Exception as e:
                resultado["diagrama_erro"] = str(e)
        
        log_questao_gerada("fisica")
        return resultado

    # =========================================================================
    # TERMODINÂMICA - Calor
    # =========================================================================
    
    def gerar_questao_calor(self, dificuldade: str = "medio", com_diagrama: bool = False) -> dict:
        """Gera questão sobre Calorimetria."""
        
        if dificuldade == "facil":
            m = random.choice([100, 200, 500])  # gramas
            delta_t = random.choice([10, 20, 30])  # °C
            c = 1  # cal/g°C (água)
            Q = m * c * delta_t
            
            enunciado = (
                f"Calcule a quantidade de calor necessária para aquecer {m} g de água "
                f"em {delta_t}°C. (c_água = 1 cal/g°C)"
            )
            resposta = f"Q = m×c×ΔT = {m}×{c}×{delta_t} = {Q} cal"
            
        elif dificuldade == "medio":
            m1 = random.choice([200, 300, 400])  # g água quente
            t1 = random.choice([70, 80, 90])  # °C
            m2 = random.choice([100, 200, 300])  # g água fria
            t2 = random.choice([10, 20, 25])  # °C
            
            # Equilíbrio térmico: m1×c×(t1-Tf) = m2×c×(Tf-t2)
            tf = (m1 * t1 + m2 * t2) / (m1 + m2)
            
            enunciado = (
                f"Em um calorímetro ideal, misturam-se {m1} g de água a {t1}°C "
                f"com {m2} g de água a {t2}°C. "
                f"Qual a temperatura final de equilíbrio?"
            )
            resposta = (
                f"Pelo equilíbrio térmico: Q_cedido = Q_recebido\n"
                f"m₁×c×(T₁-Tf) = m₂×c×(Tf-T₂)\n"
                f"{m1}×(T₁-Tf) = {m2}×(Tf-T₂)\n"
                f"{m1}×({t1}-Tf) = {m2}×(Tf-{t2})\n"
                f"Tf = (m₁×T₁ + m₂×T₂)/(m₁+m₂)\n"
                f"Tf = ({m1}×{t1} + {m2}×{t2})/({m1}+{m2}) = {tf:.1f}°C"
            )
            
        else:  # dificil
            m_gelo = random.choice([100, 200, 300])  # g de gelo
            t_gelo = random.choice([-10, -15, -20])  # °C inicial do gelo
            m_agua = random.choice([400, 500, 600])  # g de água
            t_agua = random.choice([60, 70, 80])  # °C inicial da água
            
            # Calor para aquecer gelo até 0°C
            Q1 = m_gelo * self.C_GELO * (0 - t_gelo)
            
            # Calor para derreter o gelo
            Q2 = m_gelo * self.L_FUSAO
            
            # Calor disponível da água para esfriar até 0°C
            Q_agua_max = m_agua * self.C_AGUA * t_agua
            
            # Verificar se todo gelo derrete
            if Q_agua_max > Q1 + Q2:
                # Sobra calor, calcular temperatura final
                Q_restante = Q_agua_max - Q1 - Q2
                tf = Q_restante / ((m_gelo + m_agua) * self.C_AGUA)
                estado_final = f"Todo o gelo derrete. Temperatura final: {tf:.1f}°C"
            else:
                tf = 0
                estado_final = "Nem todo o gelo derrete. Temperatura final: 0°C (equilíbrio água-gelo)"
            
            enunciado = (
                f"Um bloco de gelo de {m_gelo} g a {t_gelo}°C é colocado em {m_agua} g de água a {t_agua}°C "
                f"em um calorímetro ideal. Dados: c_gelo = {self.C_GELO} cal/g°C, "
                f"c_água = {self.C_AGUA} cal/g°C, L_fusão = {self.L_FUSAO} cal/g.\n"
                f"Determine a temperatura final de equilíbrio e o estado físico final."
            )
            resposta = (
                f"Etapas do gelo:\n"
                f"1) Aquecer gelo de {t_gelo}°C a 0°C:\n"
                f"   Q₁ = m×c_gelo×ΔT = {m_gelo}×{self.C_GELO}×{abs(t_gelo)} = {Q1} cal\n\n"
                f"2) Derreter o gelo a 0°C:\n"
                f"   Q₂ = m×L = {m_gelo}×{self.L_FUSAO} = {Q2} cal\n\n"
                f"Calor total necessário: Q_total = {Q1} + {Q2} = {Q1+Q2} cal\n\n"
                f"Calor disponível da água (até 0°C):\n"
                f"Q_água = {m_agua}×{self.C_AGUA}×{t_agua} = {Q_agua_max} cal\n\n"
                f"Conclusão: {estado_final}"
            )
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Calorimetria",
            "dificuldade": dificuldade,
            "topico": "termodinamica"
        }
        
        log_questao_gerada("fisica")
        return resultado

    # =========================================================================
    # TERMODINÂMICA - Dilatação
    # =========================================================================
    
    def gerar_questao_dilatacao(self, dificuldade: str = "medio", com_diagrama: bool = False) -> dict:
        """Gera questão sobre Dilatação Térmica."""
        
        if dificuldade == "facil":
            L0 = random.choice([100, 200, 500])  # cm
            alpha = random.choice([11, 17, 23]) * 1e-6  # coeficiente linear
            delta_t = random.choice([50, 100, 150])  # °C
            
            delta_L = L0 * alpha * delta_t
            
            enunciado = (
                f"Uma barra metálica de {L0} cm é aquecida em {delta_t}°C. "
                f"Sabendo que o coeficiente de dilatação linear é α = {alpha:.0e} °C⁻¹, "
                f"calcule a variação no comprimento da barra."
            )
            resposta = (
                f"ΔL = L₀×α×ΔT = {L0}×{alpha:.0e}×{delta_t}\n"
                f"ΔL = {delta_L:.4f} cm = {delta_L*10:.3f} mm"
            )
            
        elif dificuldade == "medio":
            # Bimetalico / lâminas diferentes
            L0 = random.choice([1, 2, 5])  # metros
            alpha1 = 12e-6  # aço
            alpha2 = 23e-6  # alumínio
            delta_t = random.choice([100, 150, 200])
            
            L1 = L0 * (1 + alpha1 * delta_t)
            L2 = L0 * (1 + alpha2 * delta_t)
            diferenca = (L2 - L1) * 1000  # mm
            
            enunciado = (
                f"Duas barras, uma de aço (α = {alpha1:.0e} °C⁻¹) e outra de alumínio "
                f"(α = {alpha2:.0e} °C⁻¹), têm o mesmo comprimento de {L0} m a 20°C. "
                f"Qual será a diferença entre seus comprimentos quando aquecidas a {20+delta_t}°C?"
            )
            resposta = (
                f"Comprimento final do aço:\n"
                f"L₁ = L₀(1 + α₁×ΔT) = {L0}×(1 + {alpha1:.0e}×{delta_t}) = {L1:.6f} m\n\n"
                f"Comprimento final do alumínio:\n"
                f"L₂ = L₀(1 + α₂×ΔT) = {L0}×(1 + {alpha2:.0e}×{delta_t}) = {L2:.6f} m\n\n"
                f"Diferença: ΔL = L₂ - L₁ = {diferenca:.3f} mm"
            )
            
        else:  # dificil
            # Anel e esfera
            d_anel = 10  # cm diâmetro do anel
            d_esfera = 10.05  # cm diâmetro da esfera
            alpha = 17e-6  # latão
            
            # Precisamos que d_anel_final = d_esfera
            # d_anel × (1 + α×ΔT) = d_esfera
            delta_t = (d_esfera / d_anel - 1) / alpha
            
            enunciado = (
                f"Um anel de latão (α = {alpha:.0e} °C⁻¹) tem diâmetro interno de {d_anel:.2f} cm a 20°C. "
                f"Uma esfera de mesmo material tem diâmetro de {d_esfera:.2f} cm. "
                f"A que temperatura devemos aquecer o anel para que a esfera passe por ele?"
            )
            resposta = (
                f"Para a esfera passar: d_anel_final ≥ d_esfera\n"
                f"d_anel × (1 + α×ΔT) = d_esfera\n"
                f"{d_anel} × (1 + {alpha:.0e}×ΔT) = {d_esfera}\n"
                f"1 + {alpha:.0e}×ΔT = {d_esfera/d_anel:.5f}\n"
                f"ΔT = ({d_esfera/d_anel:.5f} - 1) / {alpha:.0e}\n"
                f"ΔT ≈ {delta_t:.1f}°C\n\n"
                f"Temperatura final: T = 20 + {delta_t:.1f} ≈ {20+delta_t:.0f}°C"
            )
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Dilatação Térmica",
            "dificuldade": dificuldade,
            "topico": "termodinamica"
        }
        
        log_questao_gerada("fisica")
        return resultado

    # =========================================================================
    # ONDULATÓRIA - Ondas
    # =========================================================================
    
    def gerar_questao_ondas(self, dificuldade: str = "medio", com_diagrama: bool = False) -> dict:
        """Gera questão sobre Ondas."""
        
        if dificuldade == "facil":
            f = random.choice([50, 100, 200, 500])  # Hz
            lam = random.choice([2, 4, 5, 10])  # metros
            v = f * lam
            
            enunciado = (
                f"Uma onda tem frequência de {f} Hz e comprimento de onda de {lam} m. "
                f"Qual a velocidade de propagação dessa onda?"
            )
            resposta = f"v = f × λ = {f} × {lam} = {v} m/s"
            
        elif dificuldade == "medio":
            # Ondas estacionárias
            L = random.choice([1, 1.5, 2])  # metros
            n = random.choice([2, 3, 4])  # número de ventres
            v = self.VELOCIDADE_SOM
            
            lam = 2 * L / n
            f = v / lam
            
            enunciado = (
                f"Uma corda de {L} m de comprimento está fixa nas duas extremidades. "
                f"Ao vibrar, forma-se uma onda estacionária com {n} ventres. "
                f"Considerando a velocidade da onda na corda como {v} m/s, calcule:\n"
                f"a) O comprimento de onda;\n"
                f"b) A frequência de vibração."
            )
            resposta = (
                f"Para onda estacionária com extremidades fixas:\n"
                f"L = n × λ/2\n\n"
                f"a) λ = 2L/n = 2×{L}/{n} = {lam:.2f} m\n\n"
                f"b) f = v/λ = {v}/{lam:.2f} = {f:.1f} Hz"
            )
            
        else:  # dificil
            # Efeito Doppler
            v_som = self.VELOCIDADE_SOM
            f_fonte = random.choice([400, 500, 600])  # Hz
            v_fonte = random.choice([20, 30, 40])  # m/s (ambulância)
            
            # Aproximação
            f_aprox = f_fonte * v_som / (v_som - v_fonte)
            # Afastamento
            f_afast = f_fonte * v_som / (v_som + v_fonte)
            
            enunciado = (
                f"Uma ambulância emite som com frequência de {f_fonte} Hz e se move a {v_fonte} m/s. "
                f"Considerando a velocidade do som = {v_som} m/s, calcule a frequência percebida "
                f"por um observador parado quando a ambulância:\n"
                f"a) Se aproxima;\n"
                f"b) Se afasta."
            )
            resposta = (
                f"Efeito Doppler (observador parado, fonte móvel):\n"
                f"f' = f × v/(v ∓ vf)\n\n"
                f"a) Aproximação (-):\n"
                f"   f' = {f_fonte} × {v_som}/({v_som} - {v_fonte})\n"
                f"   f' = {f_fonte} × {v_som}/{v_som - v_fonte} = {f_aprox:.1f} Hz\n\n"
                f"b) Afastamento (+):\n"
                f"   f' = {f_fonte} × {v_som}/({v_som} + {v_fonte})\n"
                f"   f' = {f_fonte} × {v_som}/{v_som + v_fonte} = {f_afast:.1f} Hz"
            )
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Ondas",
            "dificuldade": dificuldade,
            "topico": "ondulatoria"
        }
        
        log_questao_gerada("fisica")
        return resultado

    # =========================================================================
    # ELETRICIDADE - Circuitos
    # =========================================================================
    
    def gerar_questao_circuito(self, dificuldade: str = "medio", com_diagrama: bool = False) -> dict:
        """Gera questão sobre Circuitos Elétricos."""
        
        if dificuldade == "facil":
            V = random.choice([6, 9, 12])
            R = random.choice([2, 3, 4, 6])
            I = V / R
            
            enunciado = (
                f"Um circuito possui uma fonte de {V} V e um resistor de {R} Ω. "
                f"Qual a corrente elétrica?"
            )
            resposta = f"I = V/R = {V}/{R} = {I:.2f} A"
            
        elif dificuldade == "medio":
            R1 = random.choice([4, 6, 8])
            R2 = random.choice([3, 6, 12])
            V = random.choice([12, 24, 36])
            
            # Resistores em paralelo
            Req = (R1 * R2) / (R1 + R2)
            I_total = V / Req
            I1 = V / R1
            I2 = V / R2
            
            enunciado = (
                f"Dois resistores de {R1} Ω e {R2} Ω estão ligados em paralelo "
                f"a uma fonte de {V} V. Calcule:\n"
                f"a) A resistência equivalente;\n"
                f"b) A corrente total;\n"
                f"c) A corrente em cada resistor."
            )
            resposta = (
                f"a) Paralelo: 1/Req = 1/R₁ + 1/R₂\n"
                f"   Req = R₁×R₂/(R₁+R₂) = {R1}×{R2}/({R1}+{R2}) = {Req:.2f} Ω\n\n"
                f"b) I_total = V/Req = {V}/{Req:.2f} = {I_total:.2f} A\n\n"
                f"c) I₁ = V/R₁ = {V}/{R1} = {I1:.2f} A\n"
                f"   I₂ = V/R₂ = {V}/{R2} = {I2:.2f} A"
            )
            
        else:  # dificil
            # Circuito misto
            R1 = 6  # em série com o paralelo
            R2 = 4
            R3 = 12  # R2 e R3 em paralelo
            V = 24
            
            R_paralelo = (R2 * R3) / (R2 + R3)
            R_total = R1 + R_paralelo
            I_total = V / R_total
            V1 = I_total * R1
            V_paralelo = I_total * R_paralelo
            I2 = V_paralelo / R2
            I3 = V_paralelo / R3
            P_total = V * I_total
            
            enunciado = (
                f"No circuito abaixo, R₁ = {R1} Ω está em série com a associação em paralelo "
                f"de R₂ = {R2} Ω e R₃ = {R3} Ω. A fonte tem tensão de {V} V. Calcule:\n"
                f"a) A resistência equivalente total;\n"
                f"b) A corrente fornecida pela fonte;\n"
                f"c) A tensão em cada resistor;\n"
                f"d) A potência total dissipada."
            )
            resposta = (
                f"a) Paralelo R₂//R₃:\n"
                f"   R_p = R₂×R₃/(R₂+R₃) = {R2}×{R3}/({R2}+{R3}) = {R_paralelo:.2f} Ω\n"
                f"   R_total = R₁ + R_p = {R1} + {R_paralelo:.2f} = {R_total:.2f} Ω\n\n"
                f"b) I = V/R_total = {V}/{R_total:.2f} = {I_total:.2f} A\n\n"
                f"c) V₁ = I×R₁ = {I_total:.2f}×{R1} = {V1:.2f} V\n"
                f"   V₂ = V₃ = I×R_p = {I_total:.2f}×{R_paralelo:.2f} = {V_paralelo:.2f} V\n"
                f"   (Verificação: V₁ + V₂ = {V1:.2f} + {V_paralelo:.2f} = {V1+V_paralelo:.2f} V ≈ {V} V ✓)\n\n"
                f"d) P = V×I = {V}×{I_total:.2f} = {P_total:.2f} W"
            )
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Circuitos Elétricos",
            "dificuldade": dificuldade,
            "topico": "eletricidade"
        }
        
        if com_diagrama:
            try:
                gerador = self._get_gerador_imagens()
                resultado["diagrama"] = gerador.gerar_diagrama_circuito_simples(6, 12)
            except Exception as e:
                resultado["diagrama_erro"] = str(e)
        
        log_questao_gerada("fisica")
        return resultado

    # =========================================================================
    # MÉTODO PRINCIPAL - Roteador de tópicos
    # =========================================================================
    
    def gerar_questao(self, topico: str = "mru", dificuldade: str = "medio", 
                      com_diagrama: bool = False) -> dict:
        """
        Gera uma questão de física baseada no tópico e dificuldade.
        
        Args:
            topico: Tópico da questão
            dificuldade: facil, medio ou dificil
            com_diagrama: Se True, gera diagrama junto com a questão
        
        Returns:
            Dicionário com a questão gerada
        """
        topico_lower = topico.lower().replace("_", " ").replace("-", " ")
        
        # Mecânica
        if topico_lower in ["mru", "movimento uniforme", "movimento retilineo uniforme"]:
            return self.gerar_questao_mru(dificuldade, com_diagrama)
        elif topico_lower in ["mruv", "movimento variado", "movimento uniformemente variado"]:
            return self.gerar_questao_mruv(dificuldade, com_diagrama)
        elif topico_lower in ["queda livre", "queda", "lancamento vertical"]:
            return self.gerar_questao_queda_livre(dificuldade, com_diagrama)
        
        # Dinâmica
        elif topico_lower in ["forca", "força", "forcas", "forças", "leis newton", "dinamica"]:
            return self.gerar_questao_forca(dificuldade, com_diagrama)
        
        # Termodinâmica
        elif topico_lower in ["calor", "calorimetria", "temperatura", "termodinamica"]:
            return self.gerar_questao_calor(dificuldade, com_diagrama)
        elif topico_lower in ["dilatacao", "dilatação", "dilatacao termica"]:
            return self.gerar_questao_dilatacao(dificuldade, com_diagrama)
        
        # Ondulatória
        elif topico_lower in ["ondas", "ondulatoria", "som", "luz"]:
            return self.gerar_questao_ondas(dificuldade, com_diagrama)
        
        # Eletricidade
        elif topico_lower in ["circuito", "circuitos", "eletricidade", "ohm", "lei ohm", "resistencia"]:
            return self.gerar_questao_circuito(dificuldade, com_diagrama)
        
        # Padrão: escolhe aleatoriamente
        else:
            metodos = [
                self.gerar_questao_mru,
                self.gerar_questao_mruv,
                self.gerar_questao_queda_livre,
                self.gerar_questao_forca,
                self.gerar_questao_calor,
                self.gerar_questao_ondas,
                self.gerar_questao_circuito
            ]
            metodo = random.choice(metodos)
            return metodo(dificuldade, com_diagrama)
