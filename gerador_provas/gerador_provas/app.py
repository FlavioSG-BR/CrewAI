import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from backend.main_crewai import (
    gerar_questao_simples,
    gerar_prova_completa,
    gerar_multiplas_questoes,
    gerar_questao_com_diagrama
)

app = Flask(__name__, static_folder='static')

# Criar diretório de diagramas se não existir
DIAGRAMAS_DIR = os.path.join(app.static_folder, 'diagramas')
os.makedirs(DIAGRAMAS_DIR, exist_ok=True)


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
        
        try:
            if modo == "simples":
                # Geração simples (direto do agente)
                questao = gerar_questao_simples(materia, topico, com_diagrama)
                return render_template("questao.html", questao=questao, modo="simples")
            
            elif modo == "completo":
                # Geração completa (com CrewAI + revisão)
                requisitos = {
                    "materia": materia,
                    "topico": topico or "geral",
                    "num_questoes": 1,
                    "dificuldade": dificuldade,
                    "com_diagrama": com_diagrama
                }
                questao = gerar_prova_completa(requisitos)
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
                return render_template("resultado.html", questoes=questoes, total=len(questoes))
        
        except Exception as e:
            return render_template("index.html", erro=str(e))
    
    return render_template("index.html")


@app.route("/diagrama/<path:filename>")
def servir_diagrama(filename):
    """Serve arquivos de diagramas gerados."""
    return send_from_directory(DIAGRAMAS_DIR, filename)


@app.route("/api/questao", methods=["POST"])
def api_gerar_questao():
    """API para geração de questão via JSON."""
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
    """API para geração de múltiplas questões via JSON."""
    dados = request.get_json()
    
    if not dados:
        return jsonify({"erro": "Dados não fornecidos"}), 400
    
    materia = dados.get("materia", "fisica")
    topico = dados.get("topico", "geral")
    quantidade = dados.get("quantidade", 5)
    dificuldade = dados.get("dificuldade", "medio")
    com_diagrama = dados.get("com_diagrama", False)
    
    try:
        questoes = gerar_multiplas_questoes(
            materia=materia,
            topico=topico,
            quantidade=quantidade,
            dificuldade=dificuldade,
            com_diagrama=com_diagrama
        )
        
        return jsonify({
            "questoes": questoes,
            "total": len(questoes),
            "materia": materia,
            "topico": topico
        })
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/api/diagrama", methods=["POST"])
def api_gerar_diagrama():
    """API para geração apenas do diagrama."""
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


@app.route("/sobre")
def sobre():
    """Página sobre o projeto."""
    return render_template("sobre.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
