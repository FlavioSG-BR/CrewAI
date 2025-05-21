from flask import Flask, render_template, request
from backend.agents.fisica import AgenteFisica
from backend.agents.quimica import AgenteQuimica

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        materia = request.form.get("materia")
        
        if materia == "fisica":
            questao = AgenteFisica().gerar_questao_mru()
        elif materia == "quimica":
            questao = AgenteQuimica().gerar_questao_tabela_periodica()
        
        return render_template("questao.html", questao=questao)
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
