"""
Gerador de Provas - Aplicação Flask Principal.

Este módulo define as rotas e a lógica principal da aplicação web.
Suporta geração de questões via templates OU via IA real (Ollama/OpenAI).
"""

import os
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from config import settings
from backend.main_crewai import (
    gerar_questao_simples,
    gerar_prova_completa,
    gerar_multiplas_questoes,
    gerar_questao_com_diagrama
)
from backend.services.prova_service import ProvaService, ConfiguracaoProva

# Tenta importar o gerador de IA (pode falhar se LLM não configurado)
try:
    from backend.gerador_ia import gerar_questao_ia, gerar_multiplas_ia
    IA_DISPONIVEL = True
except Exception as e:
    print(f"[INFO] Gerador de IA não disponível: {e}")
    IA_DISPONIVEL = False

# Verifica se deve usar IA
USE_AI = os.getenv("USE_AI_GENERATION", "false").lower() == "true" and IA_DISPONIVEL

# Inicialização do Flask
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = settings.SECRET_KEY

# Criar diretórios necessários
DIAGRAMAS_DIR = os.path.join(app.static_folder, settings.DIAGRAMAS_DIR.replace('static/', ''))
os.makedirs(DIAGRAMAS_DIR, exist_ok=True)
os.makedirs(settings.LOG_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
os.makedirs(settings.PDF_OUTPUT_DIR, exist_ok=True)

# Serviço de provas
prova_service = ProvaService()


# =============================================================================
# ROTAS PRINCIPAIS
# =============================================================================

@app.route("/", methods=["GET", "POST"])
def index():
    """Página inicial com formulário de geração de questões."""
    if request.method == "POST":
        # Obtém dados do formulário
        materia = request.form.get("materia", "fisica")
        topico = request.form.get("topico", "")
        dificuldade = request.form.get("dificuldade", "medio")
        modo = request.form.get("modo", "simples")
        quantidade = int(request.form.get("quantidade", 1))
        com_diagrama = request.form.get("com_diagrama") == "on"
        observacoes = request.form.get("observacoes", "").strip()
        
        try:
            if modo == "simples":
                # Geração simples (template-based)
                questao = gerar_questao_simples(materia, topico, dificuldade, com_diagrama)
                if observacoes:
                    questao["observacoes_professor"] = observacoes
                questao["gerado_por_ia"] = False
                return render_template("questao.html", questao=questao, modo="simples")
            
            elif modo == "ia":
                # Geração com IA real (Ollama/OpenAI)
                if not IA_DISPONIVEL:
                    return render_template("index.html", erro="IA não disponível. Configure o Ollama ou API key.")
                questao = gerar_questao_ia(materia, topico, dificuldade, observacoes)
                return render_template("questao.html", questao=questao, modo="ia")
            
            elif modo == "completo":
                # Geração completa (com CrewAI + revisão)
                requisitos = {
                    "materia": materia,
                    "topico": topico or "geral",
                    "num_questoes": 1,
                    "dificuldade": dificuldade,
                    "com_diagrama": com_diagrama,
                    "observacoes": observacoes
                }
                questao = gerar_prova_completa(requisitos)
                if observacoes:
                    questao["observacoes_professor"] = observacoes
                return render_template("questao.html", questao=questao, modo="completo")
            
            elif modo == "multiplas":
                # Geração de múltiplas questões
                questoes = gerar_multiplas_questoes(
                    materia=materia,
                    topico=topico or "geral",
                    quantidade=quantidade,
                    dificuldade=dificuldade,
                    com_diagrama=com_diagrama
                )
                # Adiciona observações a todas as questões
                if observacoes:
                    for q in questoes:
                        q["observacoes_professor"] = observacoes
                return render_template("resultado.html", questoes=questoes, total=len(questoes))
        
        except Exception as e:
            return render_template("index.html", erro=str(e))
    
    return render_template("index.html")


@app.route("/prova", methods=["GET", "POST"])
def gerar_prova_view():
    """Página para geração de provas completas com PDF."""
    # Listar tópicos disponíveis
    topicos_disponiveis = prova_service.listar_topicos_disponiveis()
    
    if request.method == "POST":
        try:
            # Obter dados do formulário
            titulo = request.form.get("titulo", "Prova")
            materia = request.form.get("materia", "matematica")
            topicos = request.form.getlist("topicos")  # Lista de tópicos selecionados
            num_questoes = int(request.form.get("num_questoes", 10))
            tipo_questao = request.form.get("tipo_questao", "dissertativa")
            dificuldade = request.form.get("dificuldade", "medio")
            tempo_limite = request.form.get("tempo_limite")
            instituicao = request.form.get("instituicao", "")
            com_diagramas = request.form.get("com_diagramas") == "on"
            
            # Instruções customizadas
            instrucoes_text = request.form.get("instrucoes", "")
            instrucoes = [i.strip() for i in instrucoes_text.split("\n") if i.strip()] if instrucoes_text else None
            
            # Configurar e gerar prova
            config = ConfiguracaoProva(
                titulo=titulo,
                materia=materia,
                topicos=topicos if topicos else ["geral"],
                num_questoes=num_questoes,
                tipo_questao=tipo_questao,
                dificuldade=dificuldade,
                tempo_limite_min=int(tempo_limite) if tempo_limite else None,
                com_diagramas=com_diagramas,
                instituicao=instituicao if instituicao else None,
                instrucoes=instrucoes,
                gerar_pdf=True,
                gerar_gabarito=True
            )
            
            prova = prova_service.criar_prova(config)
            
            return render_template("prova_gerada.html", prova=prova)
            
        except Exception as e:
            return render_template(
                "prova_form.html", 
                topicos=topicos_disponiveis,
                erro=str(e)
            )
    
    return render_template("prova_form.html", topicos=topicos_disponiveis)


@app.route("/download/<tipo>/<path:filename>")
def download_pdf(tipo, filename):
    """Rota para download dos PDFs gerados."""
    try:
        directory = settings.PDF_OUTPUT_DIR
        return send_from_directory(
            directory, 
            filename, 
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"erro": str(e)}), 404


@app.route("/sobre")
def sobre():
    """Página sobre o projeto."""
    info = {
        "versao": "1.0.0",
        "ambiente": settings.FLASK_ENV if hasattr(settings, 'FLASK_ENV') else 'development',
        "diagramas_dir": settings.DIAGRAMAS_DIR
    }
    return render_template("sobre.html", info=info)


# =============================================================================
# ROTAS DE ARQUIVOS ESTÁTICOS
# =============================================================================

@app.route("/diagrama/<path:filename>")
def servir_diagrama(filename):
    """Serve arquivos de diagramas gerados."""
    return send_from_directory(DIAGRAMAS_DIR, filename)


# =============================================================================
# API REST
# =============================================================================

@app.route("/api/questao", methods=["POST"])
def api_gerar_questao():
    """
    API para geração de questão via JSON.
    
    Request Body:
        {
            "materia": "fisica",
            "topico": "mru",
            "dificuldade": "medio",
            "modo": "simples",
            "com_diagrama": false
        }
    
    Response:
        {
            "enunciado": "...",
            "resposta": "...",
            "tipo": "...",
            "diagrama": "path/to/image.png" (opcional)
        }
    """
    dados = request.get_json()
    
    if not dados:
        return jsonify({"erro": "Dados não fornecidos"}), 400
    
    materia = dados.get("materia", "fisica")
    topico = dados.get("topico", "")
    dificuldade = dados.get("dificuldade", "medio")
    modo = dados.get("modo", "simples")
    com_diagrama = dados.get("com_diagrama", False)
    
    try:
        if modo == "simples":
            questao = gerar_questao_simples(materia, topico, com_diagrama)
        else:
            requisitos = {
                "materia": materia,
                "topico": topico or "geral",
                "num_questoes": 1,
                "dificuldade": dificuldade,
                "com_diagrama": com_diagrama
            }
            questao = gerar_prova_completa(requisitos)
        
        return jsonify(questao)
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/api/prova", methods=["POST"])
def api_gerar_prova():
    """
    API para geração de prova completa com PDF.
    
    Request Body:
        {
            "titulo": "Prova de Álgebra",
            "materia": "matematica",
            "topicos": ["equacao_1_grau", "logaritmo"],
            "num_questoes": 10,
            "tipo_questao": "multipla_escolha",
            "dificuldade": "medio",
            "tempo_limite_min": 120,
            "instituicao": "Escola XYZ",
            "com_diagramas": false,
            "gerar_pdf": true,
            "gerar_gabarito": true
        }
    
    Response:
        {
            "id": "...",
            "titulo": "...",
            "questoes": [...],
            "pdfs": {
                "prova": "path/to/prova.pdf",
                "gabarito": "path/to/gabarito.pdf"
            }
        }
    """
    dados = request.get_json()
    
    if not dados:
        return jsonify({"erro": "Dados não fornecidos"}), 400
    
    try:
        config = ConfiguracaoProva(
            titulo=dados.get("titulo", "Prova"),
            materia=dados.get("materia", "matematica"),
            topicos=dados.get("topicos", ["geral"]),
            num_questoes=dados.get("num_questoes", 10),
            tipo_questao=dados.get("tipo_questao", "dissertativa"),
            dificuldade=dados.get("dificuldade", "medio"),
            tempo_limite_min=dados.get("tempo_limite_min"),
            com_diagramas=dados.get("com_diagramas", False),
            instituicao=dados.get("instituicao"),
            instrucoes=dados.get("instrucoes"),
            gerar_pdf=dados.get("gerar_pdf", True),
            gerar_gabarito=dados.get("gerar_gabarito", True)
        )
        
        prova = prova_service.criar_prova(config)
        
        return jsonify(prova)
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/api/prova/topicos", methods=["GET"])
def api_listar_topicos():
    """
    API para listar tópicos disponíveis por matéria.
    
    Query params:
        materia: (opcional) Filtrar por matéria específica
    
    Response:
        {
            "matematica": {
                "algebra": ["equacao_1_grau", ...],
                ...
            },
            ...
        }
    """
    materia = request.args.get("materia")
    topicos = prova_service.listar_topicos_disponiveis(materia)
    return jsonify(topicos)


@app.route("/api/prova/<prova_id>", methods=["GET"])
def api_buscar_prova(prova_id):
    """API para buscar uma prova pelo ID."""
    prova = prova_service.buscar_prova(prova_id)
    if prova:
        return jsonify(prova)
    return jsonify({"erro": "Prova não encontrada"}), 404


@app.route("/api/provas", methods=["GET"])
def api_listar_provas():
    """
    API para listar provas.
    
    Query params:
        materia: Filtrar por matéria
        status: Filtrar por status
        limite: Número máximo de resultados
    """
    materia = request.args.get("materia")
    status = request.args.get("status")
    limite = int(request.args.get("limite", 50))
    
    provas = prova_service.listar_provas(
        materia=materia,
        status=status,
        limite=limite
    )
    
    return jsonify({"provas": provas, "total": len(provas)})


@app.route("/api/diagrama", methods=["POST"])
def api_gerar_diagrama():
    """
    API para geração apenas do diagrama.
    
    Request Body:
        {
            "materia": "fisica",
            "topico": "mru"
        }
    
    Response:
        {
            "sucesso": true,
            "diagrama": "path/to/image.png",
            "questao": {...}
        }
    """
    dados = request.get_json()
    
    if not dados:
        return jsonify({"erro": "Dados não fornecidos"}), 400
    
    materia = dados.get("materia", "fisica")
    topico = dados.get("topico", "")
    
    try:
        questao = gerar_questao_com_diagrama(materia, topico)
        
        if "diagrama" in questao:
            return jsonify({
                "sucesso": True,
                "diagrama": questao["diagrama"],
                "questao": questao
            })
        else:
            return jsonify({
                "sucesso": False,
                "erro": questao.get("diagrama_erro", "Não foi possível gerar o diagrama")
            }), 500
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/api/health")
def health_check():
    """Endpoint de verificação de saúde da aplicação."""
    return jsonify({
        "status": "healthy",
        "ambiente": settings.FLASK_ENV if hasattr(settings, 'FLASK_ENV') else 'development'
    })


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    debug = getattr(settings, 'DEBUG', True)
    app.run(
        debug=debug,
        host=settings.HOST,
        port=settings.PORT
    )
