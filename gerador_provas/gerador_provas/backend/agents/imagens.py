import os
import uuid
import math
from typing import Optional, Tuple
from crewai import Agent

# Configuração para não exibir janelas do matplotlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle
import numpy as np


class AgenteImagens:
    """Agente responsável pela geração de diagramas científicos."""
    
    # Diretório para salvar as imagens
    OUTPUT_DIR = "static/diagramas"
    
    def __init__(self):
        # Criar diretório de output se não existir
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        
        self.agent = Agent(
            role="Gerador de Diagramas",
            goal="Criar imagens para questões de Física/Química/Matemática",
            backstory="Especialista em visualização científica com experiência em educação",
            verbose=False,
            allow_delegation=False
        )
    
    def _gerar_nome_arquivo(self) -> str:
        """Gera um nome único para o arquivo de imagem."""
        return f"{uuid.uuid4().hex[:8]}.png"
    
    def _salvar_figura(self, fig, nome: str = None) -> str:
        """Salva a figura e retorna o caminho."""
        if nome is None:
            nome = self._gerar_nome_arquivo()
        
        caminho = os.path.join(self.OUTPUT_DIR, nome)
        fig.savefig(caminho, dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close(fig)
        return caminho

    # =========================================================================
    # DIAGRAMAS DE FÍSICA
    # =========================================================================
    
    def gerar_diagrama_mru(self, velocidade: float = 10, tempo: float = 5) -> str:
        """
        Gera diagrama de Movimento Retilíneo Uniforme.
        
        Args:
            velocidade: Velocidade em m/s
            tempo: Tempo em segundos
        
        Returns:
            Caminho para o arquivo de imagem
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Gráfico posição x tempo
        t = np.linspace(0, tempo, 100)
        x = velocidade * t
        
        ax1.plot(t, x, 'b-', linewidth=2, label=f'v = {velocidade} m/s')
        ax1.set_xlabel('Tempo (s)', fontsize=12)
        ax1.set_ylabel('Posição (m)', fontsize=12)
        ax1.set_title('Posição × Tempo (MRU)', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_xlim(0, tempo)
        ax1.set_ylim(0, velocidade * tempo * 1.1)
        
        # Gráfico velocidade x tempo
        ax2.axhline(y=velocidade, color='r', linewidth=2, label=f'v = {velocidade} m/s')
        ax2.fill_between([0, tempo], 0, velocidade, alpha=0.3, color='red')
        ax2.set_xlabel('Tempo (s)', fontsize=12)
        ax2.set_ylabel('Velocidade (m/s)', fontsize=12)
        ax2.set_title('Velocidade × Tempo (MRU)', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.set_xlim(0, tempo)
        ax2.set_ylim(0, velocidade * 1.3)
        ax2.text(tempo/2, velocidade/2, f'Área = {velocidade * tempo} m\n(distância)', 
                ha='center', va='center', fontsize=10)
        
        plt.tight_layout()
        return self._salvar_figura(fig, f"mru_{self._gerar_nome_arquivo()}")
    
    def gerar_diagrama_mruv(self, v0: float = 0, a: float = 2, tempo: float = 5) -> str:
        """
        Gera diagrama de Movimento Retilíneo Uniformemente Variado.
        
        Args:
            v0: Velocidade inicial em m/s
            a: Aceleração em m/s²
            tempo: Tempo em segundos
        
        Returns:
            Caminho para o arquivo de imagem
        """
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
        
        t = np.linspace(0, tempo, 100)
        v = v0 + a * t
        x = v0 * t + 0.5 * a * t**2
        
        # Gráfico posição x tempo (parábola)
        ax1.plot(t, x, 'b-', linewidth=2)
        ax1.set_xlabel('Tempo (s)', fontsize=12)
        ax1.set_ylabel('Posição (m)', fontsize=12)
        ax1.set_title('Posição × Tempo (MRUV)', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Gráfico velocidade x tempo (reta)
        ax2.plot(t, v, 'r-', linewidth=2)
        ax2.fill_between(t, 0, v, alpha=0.3, color='red')
        ax2.set_xlabel('Tempo (s)', fontsize=12)
        ax2.set_ylabel('Velocidade (m/s)', fontsize=12)
        ax2.set_title('Velocidade × Tempo (MRUV)', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Gráfico aceleração x tempo (constante)
        ax3.axhline(y=a, color='g', linewidth=2)
        ax3.set_xlabel('Tempo (s)', fontsize=12)
        ax3.set_ylabel('Aceleração (m/s²)', fontsize=12)
        ax3.set_title('Aceleração × Tempo (MRUV)', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.set_xlim(0, tempo)
        ax3.set_ylim(0, a * 1.5)
        
        plt.tight_layout()
        return self._salvar_figura(fig, f"mruv_{self._gerar_nome_arquivo()}")
    
    def gerar_diagrama_forcas(self, forcas: list = None) -> str:
        """
        Gera diagrama de forças em um corpo.
        
        Args:
            forcas: Lista de tuplas (nome, magnitude, angulo_graus)
                   Ex: [("Peso", 100, 270), ("Normal", 100, 90)]
        
        Returns:
            Caminho para o arquivo de imagem
        """
        if forcas is None:
            forcas = [
                ("Peso (P)", 100, 270),
                ("Normal (N)", 100, 90),
                ("Atrito (f)", 50, 180),
                ("Força Aplicada (F)", 80, 0)
            ]
        
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Desenhar o corpo (retângulo)
        corpo = Rectangle((-0.5, -0.5), 1, 1, fill=True, 
                         facecolor='lightblue', edgecolor='black', linewidth=2)
        ax.add_patch(corpo)
        
        # Cores para as forças
        cores = ['red', 'green', 'orange', 'purple', 'brown', 'pink']
        
        # Desenhar as forças
        escala = 0.02
        for i, (nome, mag, angulo) in enumerate(forcas):
            rad = math.radians(angulo)
            dx = mag * escala * math.cos(rad)
            dy = mag * escala * math.sin(rad)
            
            cor = cores[i % len(cores)]
            ax.annotate('', xy=(dx, dy), xytext=(0, 0),
                       arrowprops=dict(arrowstyle='->', color=cor, lw=2))
            
            # Label da força
            label_x = dx * 1.3
            label_y = dy * 1.3
            ax.text(label_x, label_y, f'{nome}\n{mag} N', 
                   ha='center', va='center', fontsize=10, color=cor,
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_xlim(-4, 4)
        ax.set_ylim(-4, 4)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='k', linewidth=0.5)
        ax.axvline(x=0, color='k', linewidth=0.5)
        ax.set_title('Diagrama de Forças', fontsize=16, fontweight='bold')
        ax.set_xlabel('x', fontsize=12)
        ax.set_ylabel('y', fontsize=12)
        
        return self._salvar_figura(fig, f"forcas_{self._gerar_nome_arquivo()}")
    
    def gerar_diagrama_circuito_simples(self, resistencia: float = 10, tensao: float = 12) -> str:
        """
        Gera diagrama de circuito elétrico simples (série).
        
        Args:
            resistencia: Resistência em Ohms
            tensao: Tensão em Volts
        
        Returns:
            Caminho para o arquivo de imagem
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Desenhar o circuito
        # Bateria
        ax.plot([1, 1], [1, 3], 'k-', linewidth=2)
        ax.plot([0.7, 1.3], [3, 3], 'k-', linewidth=3)  # Polo +
        ax.plot([0.85, 1.15], [3.3, 3.3], 'k-', linewidth=2)  # Polo -
        ax.text(0.3, 3.15, f'+\n{tensao}V', fontsize=12, ha='center')
        
        # Fios
        ax.plot([1, 1], [3.3, 4], 'k-', linewidth=2)
        ax.plot([1, 4], [4, 4], 'k-', linewidth=2)
        ax.plot([4, 4], [4, 2.5], 'k-', linewidth=2)
        
        # Resistor (símbolo em zigue-zague)
        x_res = np.array([4, 4.2, 3.8, 4.2, 3.8, 4.2, 3.8, 4])
        y_res = np.array([2.5, 2.3, 2.1, 1.9, 1.7, 1.5, 1.3, 1.1])
        ax.plot(x_res, y_res, 'k-', linewidth=2)
        ax.text(4.8, 1.8, f'R = {resistencia}Ω', fontsize=12)
        
        # Mais fios
        ax.plot([4, 4], [1.1, 0.5], 'k-', linewidth=2)
        ax.plot([1, 4], [0.5, 0.5], 'k-', linewidth=2)
        ax.plot([1, 1], [0.5, 1], 'k-', linewidth=2)
        
        # Corrente calculada
        corrente = tensao / resistencia
        ax.annotate('', xy=(2.5, 4.3), xytext=(1.5, 4.3),
                   arrowprops=dict(arrowstyle='->', color='blue', lw=2))
        ax.text(2, 4.6, f'I = {corrente:.2f} A', fontsize=11, color='blue')
        
        ax.set_xlim(-0.5, 6)
        ax.set_ylim(-0.5, 5.5)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('Circuito Elétrico Simples', fontsize=16, fontweight='bold')
        
        # Legenda com Lei de Ohm
        ax.text(0.5, -0.2, f'Lei de Ohm: V = R × I → {tensao} = {resistencia} × {corrente:.2f}', 
               fontsize=11, style='italic')
        
        return self._salvar_figura(fig, f"circuito_{self._gerar_nome_arquivo()}")

    # =========================================================================
    # DIAGRAMAS DE MATEMÁTICA
    # =========================================================================
    
    def gerar_grafico_funcao(self, tipo: str = "linear", params: dict = None) -> str:
        """
        Gera gráfico de função matemática.
        
        Args:
            tipo: Tipo da função ("linear", "quadratica", "exponencial", "seno")
            params: Parâmetros da função
        
        Returns:
            Caminho para o arquivo de imagem
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        x = np.linspace(-5, 5, 200)
        
        if tipo == "linear":
            a = params.get('a', 2) if params else 2
            b = params.get('b', 1) if params else 1
            y = a * x + b
            titulo = f'Função Linear: f(x) = {a}x + {b}'
            
        elif tipo == "quadratica":
            a = params.get('a', 1) if params else 1
            b = params.get('b', 0) if params else 0
            c = params.get('c', -4) if params else -4
            y = a * x**2 + b * x + c
            titulo = f'Função Quadrática: f(x) = {a}x² + {b}x + {c}'
            
        elif tipo == "exponencial":
            base = params.get('base', 2) if params else 2
            y = base ** x
            titulo = f'Função Exponencial: f(x) = {base}^x'
            
        elif tipo == "seno":
            amplitude = params.get('amplitude', 1) if params else 1
            y = amplitude * np.sin(x)
            titulo = f'Função Seno: f(x) = {amplitude}·sen(x)'
            
        else:
            y = x
            titulo = 'Função Identidade: f(x) = x'
        
        ax.plot(x, y, 'b-', linewidth=2, label='f(x)')
        ax.axhline(y=0, color='k', linewidth=0.8)
        ax.axvline(x=0, color='k', linewidth=0.8)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('x', fontsize=12)
        ax.set_ylabel('f(x)', fontsize=12)
        ax.set_title(titulo, fontsize=14, fontweight='bold')
        ax.legend()
        
        # Limitar y para visualização
        y_min, y_max = ax.get_ylim()
        ax.set_ylim(max(y_min, -20), min(y_max, 20))
        
        return self._salvar_figura(fig, f"funcao_{tipo}_{self._gerar_nome_arquivo()}")
    
    def gerar_diagrama_geometrico(self, figura: str = "triangulo", params: dict = None) -> str:
        """
        Gera diagrama de figura geométrica.
        
        Args:
            figura: Tipo da figura ("triangulo", "retangulo", "circulo", "quadrado")
            params: Parâmetros da figura
        
        Returns:
            Caminho para o arquivo de imagem
        """
        fig, ax = plt.subplots(figsize=(10, 10))
        
        if figura == "triangulo":
            # Triângulo com medidas
            base = params.get('base', 6) if params else 6
            altura = params.get('altura', 4) if params else 4
            
            triangulo = plt.Polygon([(0, 0), (base, 0), (base/2, altura)], 
                                   fill=True, facecolor='lightblue', 
                                   edgecolor='blue', linewidth=2)
            ax.add_patch(triangulo)
            
            # Medidas
            ax.annotate(f'base = {base}', xy=(base/2, -0.5), ha='center', fontsize=12)
            ax.annotate(f'altura = {altura}', xy=(base/2 + 0.5, altura/2), fontsize=12)
            ax.plot([base/2, base/2], [0, altura], 'r--', linewidth=1)
            
            # Área
            area = (base * altura) / 2
            ax.text(base/2, altura/3, f'Área = {area}', ha='center', fontsize=14, 
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
            
            ax.set_xlim(-1, base + 1)
            ax.set_ylim(-1, altura + 1)
            titulo = 'Triângulo'
            
        elif figura == "retangulo":
            largura = params.get('largura', 6) if params else 6
            altura = params.get('altura', 4) if params else 4
            
            retangulo = Rectangle((0, 0), largura, altura, fill=True,
                                  facecolor='lightgreen', edgecolor='green', linewidth=2)
            ax.add_patch(retangulo)
            
            ax.annotate(f'largura = {largura}', xy=(largura/2, -0.5), ha='center', fontsize=12)
            ax.annotate(f'altura = {altura}', xy=(largura + 0.5, altura/2), fontsize=12)
            
            area = largura * altura
            perimetro = 2 * (largura + altura)
            ax.text(largura/2, altura/2, f'Área = {area}\nPerímetro = {perimetro}', 
                   ha='center', fontsize=12,
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
            
            ax.set_xlim(-1, largura + 2)
            ax.set_ylim(-1, altura + 1)
            titulo = 'Retângulo'
            
        elif figura == "circulo":
            raio = params.get('raio', 3) if params else 3
            
            circulo = Circle((0, 0), raio, fill=True,
                            facecolor='lightyellow', edgecolor='orange', linewidth=2)
            ax.add_patch(circulo)
            
            # Raio
            ax.plot([0, raio], [0, 0], 'r-', linewidth=2)
            ax.annotate(f'r = {raio}', xy=(raio/2, 0.3), fontsize=12, color='red')
            
            # Centro
            ax.plot(0, 0, 'ko', markersize=5)
            
            area = math.pi * raio**2
            circunferencia = 2 * math.pi * raio
            ax.text(0, -raio - 1, f'Área = π·r² = {area:.2f}\nCircunferência = 2πr = {circunferencia:.2f}', 
                   ha='center', fontsize=11,
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            ax.set_xlim(-raio - 2, raio + 2)
            ax.set_ylim(-raio - 2, raio + 2)
            titulo = 'Círculo'
            
        else:  # quadrado
            lado = params.get('lado', 5) if params else 5
            
            quadrado = Rectangle((0, 0), lado, lado, fill=True,
                                 facecolor='lightcoral', edgecolor='red', linewidth=2)
            ax.add_patch(quadrado)
            
            ax.annotate(f'lado = {lado}', xy=(lado/2, -0.5), ha='center', fontsize=12)
            
            area = lado ** 2
            diagonal = lado * math.sqrt(2)
            ax.text(lado/2, lado/2, f'Área = {area}\nDiagonal = {diagonal:.2f}', 
                   ha='center', fontsize=12,
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
            
            # Diagonal
            ax.plot([0, lado], [0, lado], 'b--', linewidth=1, alpha=0.7)
            
            ax.set_xlim(-1, lado + 1)
            ax.set_ylim(-1, lado + 1)
            titulo = 'Quadrado'
        
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title(titulo, fontsize=16, fontweight='bold')
        
        return self._salvar_figura(fig, f"geometria_{figura}_{self._gerar_nome_arquivo()}")

    # =========================================================================
    # DIAGRAMAS DE QUÍMICA
    # =========================================================================
    
    def gerar_diagrama_atomo(self, elemento: str = "C", num_eletrons: int = 6) -> str:
        """
        Gera representação simplificada de um átomo.
        
        Args:
            elemento: Símbolo do elemento
            num_eletrons: Número de elétrons
        
        Returns:
            Caminho para o arquivo de imagem
        """
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Núcleo
        nucleo = Circle((0, 0), 0.5, fill=True, facecolor='red', edgecolor='darkred', linewidth=2)
        ax.add_patch(nucleo)
        ax.text(0, 0, elemento, ha='center', va='center', fontsize=20, fontweight='bold', color='white')
        
        # Camadas de elétrons (modelo de Bohr simplificado)
        camadas = []
        eletrons_restantes = num_eletrons
        max_por_camada = [2, 8, 8, 18, 18, 32]  # Simplificado
        
        raio = 1.5
        for i, max_e in enumerate(max_por_camada):
            if eletrons_restantes <= 0:
                break
            n_eletrons_camada = min(eletrons_restantes, max_e)
            camadas.append((raio, n_eletrons_camada))
            eletrons_restantes -= n_eletrons_camada
            raio += 1
        
        # Desenhar camadas e elétrons
        cores_camadas = ['blue', 'green', 'orange', 'purple', 'brown']
        for i, (r, n_e) in enumerate(camadas):
            # Órbita
            orbita = Circle((0, 0), r, fill=False, edgecolor='gray', 
                           linewidth=1, linestyle='--', alpha=0.5)
            ax.add_patch(orbita)
            
            # Elétrons
            for j in range(n_e):
                angulo = 2 * math.pi * j / n_e
                x = r * math.cos(angulo)
                y = r * math.sin(angulo)
                eletron = Circle((x, y), 0.15, fill=True, 
                                facecolor=cores_camadas[i % len(cores_camadas)], 
                                edgecolor='black', linewidth=1)
                ax.add_patch(eletron)
        
        # Legenda
        ax.text(0, -raio - 1, f'Elemento: {elemento}\nElétrons: {num_eletrons}', 
               ha='center', fontsize=12,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_xlim(-raio - 1, raio + 1)
        ax.set_ylim(-raio - 2, raio + 1)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f'Modelo Atômico de {elemento}', fontsize=16, fontweight='bold')
        
        return self._salvar_figura(fig, f"atomo_{elemento}_{self._gerar_nome_arquivo()}")
    
    def gerar_tabela_periodica_elemento(self, simbolo: str = "O", 
                                         num_atomico: int = 8,
                                         massa_atomica: float = 15.999,
                                         nome: str = "Oxigênio") -> str:
        """
        Gera representação de um elemento da tabela periódica.
        
        Args:
            simbolo: Símbolo do elemento
            num_atomico: Número atômico
            massa_atomica: Massa atômica
            nome: Nome do elemento
        
        Returns:
            Caminho para o arquivo de imagem
        """
        fig, ax = plt.subplots(figsize=(6, 8))
        
        # Caixa do elemento
        caixa = Rectangle((0, 0), 4, 5, fill=True,
                         facecolor='#87CEEB', edgecolor='navy', linewidth=3)
        ax.add_patch(caixa)
        
        # Número atômico
        ax.text(0.3, 4.5, str(num_atomico), fontsize=16, fontweight='bold')
        
        # Símbolo
        ax.text(2, 2.8, simbolo, ha='center', va='center', 
               fontsize=48, fontweight='bold', color='navy')
        
        # Nome
        ax.text(2, 1.5, nome, ha='center', fontsize=14)
        
        # Massa atômica
        ax.text(2, 0.5, f'{massa_atomica}', ha='center', fontsize=12)
        
        ax.set_xlim(-0.5, 4.5)
        ax.set_ylim(-0.5, 5.5)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('Elemento da Tabela Periódica', fontsize=14, fontweight='bold')
        
        return self._salvar_figura(fig, f"elemento_{simbolo}_{self._gerar_nome_arquivo()}")

    # =========================================================================
    # MÉTODO PRINCIPAL DE GERAÇÃO
    # =========================================================================
    
    def gerar_diagrama(self, descricao: str, tipo: str = None, **kwargs) -> str:
        """
        Gera um diagrama baseado na descrição ou tipo especificado.
        
        Args:
            descricao: Descrição textual do diagrama desejado
            tipo: Tipo específico do diagrama (opcional)
            **kwargs: Parâmetros adicionais para o diagrama
        
        Returns:
            Caminho para o arquivo de imagem gerado
        """
        descricao_lower = descricao.lower()
        
        # Detectar tipo de diagrama pela descrição
        if tipo == "mru" or "mru" in descricao_lower or "movimento uniforme" in descricao_lower:
            return self.gerar_diagrama_mru(**kwargs)
        
        elif tipo == "mruv" or "mruv" in descricao_lower or "uniformemente variado" in descricao_lower:
            return self.gerar_diagrama_mruv(**kwargs)
        
        elif tipo == "forcas" or "força" in descricao_lower or "forças" in descricao_lower:
            return self.gerar_diagrama_forcas(**kwargs)
        
        elif tipo == "circuito" or "circuito" in descricao_lower or "elétrico" in descricao_lower:
            return self.gerar_diagrama_circuito_simples(**kwargs)
        
        elif tipo == "funcao" or "função" in descricao_lower or "gráfico" in descricao_lower:
            tipo_funcao = kwargs.get('tipo_funcao', 'linear')
            return self.gerar_grafico_funcao(tipo=tipo_funcao, params=kwargs)
        
        elif tipo == "geometria" or any(fig in descricao_lower for fig in 
                                        ['triângulo', 'retângulo', 'círculo', 'quadrado']):
            figura = 'triangulo'
            if 'retângulo' in descricao_lower:
                figura = 'retangulo'
            elif 'círculo' in descricao_lower:
                figura = 'circulo'
            elif 'quadrado' in descricao_lower:
                figura = 'quadrado'
            return self.gerar_diagrama_geometrico(figura=figura, params=kwargs)
        
        elif tipo == "atomo" or "átomo" in descricao_lower or "modelo atômico" in descricao_lower:
            return self.gerar_diagrama_atomo(**kwargs)
        
        elif tipo == "elemento" or "tabela periódica" in descricao_lower:
            return self.gerar_tabela_periodica_elemento(**kwargs)
        
        # Fallback: gera um diagrama de MRU como padrão
        return self.gerar_diagrama_mru()
