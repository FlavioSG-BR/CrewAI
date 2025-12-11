import random
import math
from crewai import Agent
from backend.utils.logger import log_questao_gerada


class AgenteMatematica:
    """Agente especializado em questões de Matemática."""
    
    def __init__(self):
        self.agent = Agent(
            role="Professor de Matemática",
            goal="Criar questões de álgebra, geometria e funções.",
            backstory="Especialista em Matemática com experiência em olimpíadas e vestibulares.",
            allow_delegation=False
        )
        self._gerador_imagens = None
    
    def _get_gerador_imagens(self):
        """Lazy loading do gerador de imagens."""
        if self._gerador_imagens is None:
            from backend.agents.imagens import AgenteImagens
            self._gerador_imagens = AgenteImagens()
        return self._gerador_imagens

    def gerar_questao_algebra(self) -> dict:
        """
        Gera questão de álgebra (equações de 1º grau).
        
        Returns:
            Dicionário com enunciado, resposta e tipo
        """
        # Gera equação do tipo ax + b = c
        a = random.choice([2, 3, 4, 5])
        x_real = random.choice([1, 2, 3, 4, 5, 6])
        b = random.choice([1, 2, 3, 4, 5])
        c = a * x_real + b
        
        enunciado = f"Resolva a equação: {a}x + {b} = {c}"
        
        resposta = (
            f"{a}x + {b} = {c}\n"
            f"{a}x = {c} - {b}\n"
            f"{a}x = {c - b}\n"
            f"x = {c - b} / {a}\n"
            f"x = {x_real}"
        )
        
        log_questao_gerada("matematica")
        
        return {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Álgebra",
            "subtipo": "Equação 1º grau",
            "dados": {"a": a, "b": b, "c": c, "x": x_real}
        }
    
    def gerar_questao_algebra_2grau(self, com_diagrama: bool = False) -> dict:
        """
        Gera questão de equação de 2º grau.
        
        Args:
            com_diagrama: Se True, gera gráfico da parábola
        
        Returns:
            Dicionário com enunciado, resposta e tipo
        """
        # Raízes inteiras para facilitar
        x1 = random.choice([-3, -2, -1, 1, 2, 3])
        x2 = random.choice([-3, -2, -1, 1, 2, 3])
        
        # ax² + bx + c = 0 onde a(x-x1)(x-x2) = 0
        a = 1
        b = -(x1 + x2)
        c = x1 * x2
        
        # Formata a equação
        eq_str = f"x²"
        if b > 0:
            eq_str += f" + {b}x"
        elif b < 0:
            eq_str += f" - {abs(b)}x"
        if c > 0:
            eq_str += f" + {c}"
        elif c < 0:
            eq_str += f" - {abs(c)}"
        eq_str += " = 0"
        
        enunciado = f"Resolva a equação do 2º grau: {eq_str}"
        
        delta = b**2 - 4*a*c
        
        resposta = (
            f"Usando a fórmula de Bhaskara:\n"
            f"Δ = b² - 4ac = ({b})² - 4·{a}·({c}) = {delta}\n"
            f"x = (-b ± √Δ) / 2a\n"
            f"x₁ = {x1}\n"
            f"x₂ = {x2}"
        )
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Álgebra",
            "subtipo": "Equação 2º grau",
            "dados": {"a": a, "b": b, "c": c, "x1": x1, "x2": x2, "delta": delta}
        }
        
        if com_diagrama:
            try:
                gerador = self._get_gerador_imagens()
                resultado["diagrama"] = gerador.gerar_grafico_funcao(
                    tipo="quadratica",
                    params={"a": a, "b": b, "c": c}
                )
            except Exception as e:
                resultado["diagrama_erro"] = str(e)
        
        log_questao_gerada("matematica")
        return resultado
    
    def gerar_questao_geometria_plana(self, com_diagrama: bool = False) -> dict:
        """
        Gera questão de geometria plana.
        
        Args:
            com_diagrama: Se True, gera diagrama da figura
        
        Returns:
            Dicionário com enunciado, resposta e tipo
        """
        figuras = ["triangulo", "retangulo", "circulo", "quadrado"]
        figura = random.choice(figuras)
        
        if figura == "triangulo":
            base = random.choice([4, 6, 8, 10])
            altura = random.choice([3, 4, 5, 6])
            area = (base * altura) / 2
            
            enunciado = (
                f"Calcule a área de um triângulo com base {base} cm e altura {altura} cm."
            )
            resposta = f"A = (b × h) / 2 = ({base} × {altura}) / 2 = {area} cm²"
            params = {"base": base, "altura": altura}
            
        elif figura == "retangulo":
            largura = random.choice([4, 5, 6, 8])
            altura = random.choice([3, 4, 5, 6])
            area = largura * altura
            perimetro = 2 * (largura + altura)
            
            enunciado = (
                f"Calcule a área e o perímetro de um retângulo com "
                f"largura {largura} cm e altura {altura} cm."
            )
            resposta = (
                f"Área = l × h = {largura} × {altura} = {area} cm²\n"
                f"Perímetro = 2(l + h) = 2({largura} + {altura}) = {perimetro} cm"
            )
            params = {"largura": largura, "altura": altura}
            
        elif figura == "circulo":
            raio = random.choice([2, 3, 4, 5])
            area = math.pi * raio**2
            circunferencia = 2 * math.pi * raio
            
            enunciado = f"Calcule a área e a circunferência de um círculo com raio {raio} cm."
            resposta = (
                f"Área = π × r² = π × {raio}² = {area:.2f} cm²\n"
                f"Circunferência = 2πr = 2π × {raio} = {circunferencia:.2f} cm"
            )
            params = {"raio": raio}
            
        else:  # quadrado
            lado = random.choice([3, 4, 5, 6, 7])
            area = lado ** 2
            diagonal = lado * math.sqrt(2)
            
            enunciado = f"Calcule a área e a diagonal de um quadrado com lado {lado} cm."
            resposta = (
                f"Área = l² = {lado}² = {area} cm²\n"
                f"Diagonal = l√2 = {lado}√2 = {diagonal:.2f} cm"
            )
            params = {"lado": lado}
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Geometria",
            "subtipo": f"Geometria Plana - {figura.capitalize()}",
            "dados": params
        }
        
        if com_diagrama:
            try:
                gerador = self._get_gerador_imagens()
                resultado["diagrama"] = gerador.gerar_diagrama_geometrico(figura, params)
            except Exception as e:
                resultado["diagrama_erro"] = str(e)
        
        log_questao_gerada("matematica")
        return resultado
    
    def gerar_questao_funcoes(self, com_diagrama: bool = False) -> dict:
        """
        Gera questão sobre funções.
        
        Args:
            com_diagrama: Se True, gera gráfico da função
        
        Returns:
            Dicionário com enunciado, resposta e tipo
        """
        tipos = ["linear", "quadratica"]
        tipo = random.choice(tipos)
        
        if tipo == "linear":
            a = random.choice([1, 2, 3, -1, -2])
            b = random.choice([0, 1, 2, 3, -1, -2])
            x_valor = random.choice([1, 2, 3, 4])
            
            y_valor = a * x_valor + b
            
            # Formatação da função
            if b >= 0:
                func_str = f"f(x) = {a}x + {b}"
            else:
                func_str = f"f(x) = {a}x - {abs(b)}"
            
            enunciado = f"Dada a função {func_str}, calcule f({x_valor})."
            resposta = f"f({x_valor}) = {a}·{x_valor} + ({b}) = {y_valor}"
            
            params = {"a": a, "b": b}
            tipo_funcao = "linear"
            
        else:  # quadratica
            a = random.choice([1, -1])
            b = 0
            c = random.choice([-4, -1, 0, 1, 4])
            
            # Vértice
            xv = 0
            yv = c
            
            enunciado = (
                f"Dada a função f(x) = x² + ({c}), determine:\n"
                f"a) As raízes (se existirem)\n"
                f"b) O vértice da parábola"
            )
            
            if c < 0:
                raiz = math.sqrt(abs(c))
                resposta = (
                    f"a) x² + ({c}) = 0 → x² = {abs(c)} → x = ±{raiz:.2f}\n"
                    f"b) Vértice: V(0, {c})"
                )
            elif c == 0:
                resposta = (
                    f"a) x² = 0 → x = 0 (raiz dupla)\n"
                    f"b) Vértice: V(0, 0)"
                )
            else:
                resposta = (
                    f"a) x² + {c} = 0 → x² = -{c} → Não existem raízes reais\n"
                    f"b) Vértice: V(0, {c})"
                )
            
            params = {"a": a, "b": b, "c": c}
            tipo_funcao = "quadratica"
        
        resultado = {
            "enunciado": enunciado,
            "resposta": resposta,
            "tipo": "Funções",
            "subtipo": f"Função {tipo.capitalize()}",
            "dados": params
        }
        
        if com_diagrama:
            try:
                gerador = self._get_gerador_imagens()
                resultado["diagrama"] = gerador.gerar_grafico_funcao(
                    tipo=tipo_funcao,
                    params=params
                )
            except Exception as e:
                resultado["diagrama_erro"] = str(e)
        
        log_questao_gerada("matematica")
        return resultado
    
    def gerar_questao_probabilidade(self) -> dict:
        """
        Gera questão de probabilidade.
        
        Returns:
            Dicionário com enunciado, resposta e tipo
        """
        problemas = [
            {
                "enunciado": "Ao lançar um dado honesto, qual a probabilidade de obter um número par?",
                "resposta": "P(par) = 3/6 = 1/2 = 0,5 = 50%",
                "explicacao": "Números pares: {2, 4, 6} = 3 resultados favoráveis de 6 possíveis."
            },
            {
                "enunciado": "Ao lançar uma moeda 2 vezes, qual a probabilidade de obter 2 caras?",
                "resposta": "P(2 caras) = 1/4 = 0,25 = 25%",
                "explicacao": "Espaço amostral: {CC, CK, KC, KK}. Apenas CC é favorável."
            },
            {
                "enunciado": "Uma urna contém 3 bolas vermelhas e 2 azuis. Qual a probabilidade de retirar uma bola vermelha?",
                "resposta": "P(vermelha) = 3/5 = 0,6 = 60%",
                "explicacao": "3 bolas vermelhas de um total de 5 bolas."
            },
            {
                "enunciado": "Ao lançar 2 dados, qual a probabilidade de a soma ser 7?",
                "resposta": "P(soma=7) = 6/36 = 1/6 ≈ 16,67%",
                "explicacao": "Combinações: (1,6), (2,5), (3,4), (4,3), (5,2), (6,1) = 6 de 36."
            }
        ]
        
        problema = random.choice(problemas)
        
        log_questao_gerada("matematica")
        
        return {
            "enunciado": problema["enunciado"],
            "resposta": f"{problema['resposta']}\n\nExplicação: {problema['explicacao']}",
            "tipo": "Probabilidade",
            "dados": problema
        }

    def gerar_questao(self, topico: str = "algebra", com_diagrama: bool = False) -> dict:
        """
        Gera uma questão de matemática baseada no tópico.
        
        Args:
            topico: Tópico da questão
            com_diagrama: Se True, gera diagrama junto com a questão
        
        Returns:
            Dicionário com a questão gerada
        """
        topico_lower = topico.lower()
        
        if topico_lower in ["algebra", "álgebra", "equacao", "equação"]:
            return self.gerar_questao_algebra()
        elif topico_lower in ["algebra2", "2grau", "segundo_grau", "bhaskara"]:
            return self.gerar_questao_algebra_2grau(com_diagrama)
        elif topico_lower in ["geometria", "figuras", "area", "área"]:
            return self.gerar_questao_geometria_plana(com_diagrama)
        elif topico_lower in ["funcoes", "funções", "funcao", "função", "grafico", "gráfico"]:
            return self.gerar_questao_funcoes(com_diagrama)
        elif topico_lower in ["probabilidade", "prob", "estatistica"]:
            return self.gerar_questao_probabilidade()
        else:
            # Escolhe aleatoriamente
            metodos = [
                self.gerar_questao_algebra,
                lambda: self.gerar_questao_algebra_2grau(com_diagrama),
                lambda: self.gerar_questao_geometria_plana(com_diagrama),
                lambda: self.gerar_questao_funcoes(com_diagrama),
                self.gerar_questao_probabilidade
            ]
            return random.choice(metodos)()
