"""
Gerador de Alternativas para Questões de Múltipla Escolha.

Gera alternativas incorretas (distratores) plausíveis baseadas na resposta correta.
"""

import random
import re
import math
from typing import List, Dict, Tuple, Any
from decimal import Decimal


class AlternativasGenerator:
    """
    Gera alternativas para questões de múltipla escolha.
    
    Estratégias:
    1. Para respostas numéricas: variações matemáticas
    2. Para fórmulas: erros comuns
    3. Para texto: alternativas relacionadas mas incorretas
    """
    
    LETRAS = ['A', 'B', 'C', 'D', 'E']
    
    def __init__(self, num_alternativas: int = 5):
        self.num_alternativas = num_alternativas
    
    def gerar_alternativas(
        self,
        resposta_correta: str,
        tipo_questao: str = "numerica",
        contexto: Dict = None
    ) -> List[Dict]:
        """
        Gera alternativas para uma questão.
        
        Args:
            resposta_correta: A resposta correta da questão
            tipo_questao: Tipo da questão (numerica, formula, texto, unidade)
            contexto: Dados adicionais da questão para gerar distratores melhores
        
        Returns:
            Lista de alternativas com letra, texto e se é correta
        """
        contexto = contexto or {}
        
        if tipo_questao == "numerica":
            distratores = self._gerar_distratores_numericos(resposta_correta, contexto)
        elif tipo_questao == "formula":
            distratores = self._gerar_distratores_formula(resposta_correta, contexto)
        elif tipo_questao == "unidade":
            distratores = self._gerar_distratores_unidade(resposta_correta, contexto)
        elif tipo_questao == "elemento":
            distratores = self._gerar_distratores_elemento(resposta_correta, contexto)
        else:
            distratores = self._gerar_distratores_genericos(resposta_correta, contexto)
        
        # Montar alternativas
        alternativas = self._montar_alternativas(resposta_correta, distratores)
        
        return alternativas
    
    def _extrair_numero(self, texto: str) -> Tuple[float, str]:
        """Extrai o valor numérico e a unidade de uma string."""
        # Padrões comuns
        match = re.search(r'(-?\d+\.?\d*)\s*([a-zA-Z²³/]+)?', str(texto))
        if match:
            valor = float(match.group(1))
            unidade = match.group(2) or ""
            return valor, unidade
        return None, ""
    
    def _gerar_distratores_numericos(self, resposta: str, contexto: Dict) -> List[str]:
        """Gera distratores para respostas numéricas."""
        distratores = []
        
        valor, unidade = self._extrair_numero(resposta)
        if valor is None:
            return self._gerar_distratores_genericos(resposta, contexto)
        
        # Estratégias de erro comum
        estrategias = [
            lambda v: v * 2,           # Dobro
            lambda v: v / 2,           # Metade
            lambda v: v + v * 0.1,     # 10% a mais
            lambda v: v - v * 0.1,     # 10% a menos
            lambda v: v * 10,          # Erro de magnitude
            lambda v: v / 10,          # Erro de magnitude
            lambda v: -v,              # Sinal trocado
            lambda v: v + 1,           # Off by one
            lambda v: v - 1,           # Off by one
            lambda v: v * 1.5,         # 50% a mais
            lambda v: round(v),        # Arredondamento
            lambda v: math.sqrt(abs(v)) if v > 0 else v,  # Raiz quadrada
            lambda v: v ** 2 if abs(v) < 100 else v,      # Quadrado
        ]
        
        random.shuffle(estrategias)
        
        usados = {valor}
        for estrategia in estrategias:
            if len(distratores) >= self.num_alternativas - 1:
                break
            
            try:
                novo_valor = estrategia(valor)
                # Arredondar para evitar números muito feios
                if abs(novo_valor) >= 1:
                    novo_valor = round(novo_valor, 2)
                else:
                    novo_valor = round(novo_valor, 4)
                
                if novo_valor not in usados and novo_valor != 0:
                    usados.add(novo_valor)
                    if unidade:
                        distratores.append(f"{novo_valor} {unidade}")
                    else:
                        distratores.append(str(novo_valor))
            except:
                continue
        
        return distratores
    
    def _gerar_distratores_formula(self, resposta: str, contexto: Dict) -> List[str]:
        """Gera distratores para fórmulas."""
        distratores = []
        
        # Erros comuns em fórmulas de física
        formulas_erradas = {
            "v = d/t": ["v = d × t", "v = t/d", "d = v/t", "t = v × d"],
            "d = v × t": ["d = v/t", "d = t/v", "v = d × t", "t = d × v"],
            "F = m × a": ["F = m/a", "F = a/m", "a = m × F", "m = F × a"],
            "E = m × c²": ["E = m × c", "E = m/c²", "E = m² × c", "E = c²/m"],
            "v² = v₀² + 2aΔs": ["v = v₀ + 2aΔs", "v² = v₀ + 2aΔs", "v² = v₀² - 2aΔs"],
            "A = π × r²": ["A = 2π × r", "A = π × r", "A = 2π × r²", "A = π × d"],
            "V = R × I": ["V = R/I", "V = I/R", "R = V × I", "I = V × R"],
        }
        
        for formula, erros in formulas_erradas.items():
            if formula.lower() in resposta.lower() or resposta.lower() in formula.lower():
                distratores.extend(erros[:self.num_alternativas - 1])
                break
        
        if not distratores:
            # Gerar variações genéricas
            distratores = self._gerar_distratores_genericos(resposta, contexto)
        
        return distratores[:self.num_alternativas - 1]
    
    def _gerar_distratores_unidade(self, resposta: str, contexto: Dict) -> List[str]:
        """Gera distratores com unidades erradas."""
        valor, unidade = self._extrair_numero(resposta)
        
        if valor is None:
            return self._gerar_distratores_genericos(resposta, contexto)
        
        # Unidades relacionadas
        unidades_relacionadas = {
            "m/s": ["km/h", "m/s²", "km/s", "cm/s"],
            "km/h": ["m/s", "km/s", "m/h", "cm/s"],
            "m": ["cm", "km", "mm", "m²"],
            "m²": ["m", "cm²", "km²", "m³"],
            "m³": ["m²", "L", "cm³", "dm³"],
            "N": ["kg", "kN", "J", "Pa"],
            "J": ["N", "W", "kJ", "cal"],
            "W": ["J", "kW", "V", "A"],
            "V": ["A", "W", "Ω", "C"],
            "A": ["V", "W", "Ω", "mA"],
            "Ω": ["V", "A", "W", "kΩ"],
            "kg": ["g", "N", "mg", "t"],
            "s": ["min", "h", "ms", "s²"],
        }
        
        distratores = []
        
        if unidade in unidades_relacionadas:
            for unidade_errada in unidades_relacionadas[unidade]:
                distratores.append(f"{valor} {unidade_errada}")
        else:
            # Variar o valor mantendo a unidade
            distratores = self._gerar_distratores_numericos(resposta, contexto)
        
        return distratores[:self.num_alternativas - 1]
    
    def _gerar_distratores_elemento(self, resposta: str, contexto: Dict) -> List[str]:
        """Gera distratores para elementos químicos."""
        elementos = {
            "Oxigênio": ["Nitrogênio", "Carbono", "Hidrogênio", "Enxofre"],
            "Carbono": ["Nitrogênio", "Oxigênio", "Silício", "Fósforo"],
            "Hidrogênio": ["Hélio", "Lítio", "Oxigênio", "Nitrogênio"],
            "Nitrogênio": ["Oxigênio", "Carbono", "Fósforo", "Argônio"],
            "Sódio": ["Potássio", "Lítio", "Magnésio", "Cálcio"],
            "Cloro": ["Bromo", "Iodo", "Flúor", "Enxofre"],
            "Ferro": ["Cobre", "Zinco", "Níquel", "Cobalto"],
            "Ouro": ["Prata", "Cobre", "Platina", "Bronze"],
        }
        
        # Procurar elemento correspondente
        for elemento, alternativas in elementos.items():
            if elemento.lower() in resposta.lower():
                return alternativas[:self.num_alternativas - 1]
        
        return self._gerar_distratores_genericos(resposta, contexto)
    
    def _gerar_distratores_genericos(self, resposta: str, contexto: Dict) -> List[str]:
        """Gera distratores genéricos quando não há estratégia específica."""
        distratores = []
        
        # Se houver dados no contexto, usar para gerar distratores
        if "dados" in contexto:
            dados = contexto["dados"]
            for key, value in dados.items():
                if str(value) != str(resposta):
                    distratores.append(str(value))
        
        # Completar com variações da resposta
        while len(distratores) < self.num_alternativas - 1:
            # Adicionar "Nenhuma das alternativas" ou similar
            opcoes_genericas = [
                "Nenhuma das alternativas anteriores",
                "Não é possível determinar",
                "Faltam dados para resolver",
                "Todas as alternativas estão corretas",
            ]
            for opcao in opcoes_genericas:
                if opcao not in distratores:
                    distratores.append(opcao)
                    break
            else:
                break
        
        return distratores[:self.num_alternativas - 1]
    
    def _montar_alternativas(self, correta: str, distratores: List[str]) -> List[Dict]:
        """Monta a lista final de alternativas embaralhadas."""
        # Garantir que temos distratores suficientes
        while len(distratores) < self.num_alternativas - 1:
            distratores.append(f"Alternativa {len(distratores) + 2}")
        
        # Criar lista com todas as alternativas
        todas = [correta] + distratores[:self.num_alternativas - 1]
        
        # Embaralhar
        random.shuffle(todas)
        
        # Montar com letras
        alternativas = []
        for i, texto in enumerate(todas):
            alternativas.append({
                "letra": self.LETRAS[i],
                "texto": texto,
                "correta": texto == correta
            })
        
        return alternativas
    
    def identificar_tipo_resposta(self, resposta: str, questao: Dict = None) -> str:
        """Identifica automaticamente o tipo de resposta."""
        # Verificar se é numérico
        valor, unidade = self._extrair_numero(resposta)
        
        if valor is not None:
            if unidade:
                return "unidade"
            return "numerica"
        
        # Verificar se é fórmula
        if any(op in resposta for op in ["=", "×", "/", "²", "³", "π"]):
            return "formula"
        
        # Verificar se é elemento químico
        elementos_conhecidos = ["hidrogênio", "carbono", "oxigênio", "nitrogênio", 
                                "sódio", "cloro", "ferro", "ouro", "prata"]
        if any(elem in resposta.lower() for elem in elementos_conhecidos):
            return "elemento"
        
        return "texto"

