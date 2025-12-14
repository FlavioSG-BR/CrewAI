"""
Gerador de Provas - Aplicação Flask Principal.

Este módulo define as rotas e a lógica principal da aplicação web.
Suporta geração de questões via templates OU via IA real (Ollama/OpenAI).

Fluxo de Negócio (Versão Piloto):
1. Professor solicita geração de questões
2. Professor revisa, comenta e propõe melhorias
3. Professor aprova questão (salva no banco)
4. Professor seleciona questões do banco para montar prova
5. Professor define número de alunos
6. Sistema gera N provas únicas com embaralhamento
"""

import os
import json
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file, redirect, url_for
from config import settings
from backend.main_crewai import (
    gerar_questao_simples,
    gerar_prova_completa,
    gerar_multiplas_questoes,
    gerar_questao_com_diagrama
)
from backend.services.prova_service import ProvaService, ConfiguracaoProva
from backend.services.revisao_service import RevisaoService, RevisaoQuestao, FonteBibliografica
from backend.services.prova_individual_service import ProvaIndividualService, ConfiguracaoProvaIndividual

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

# Serviços
prova_service = ProvaService()
revisao_service = RevisaoService()
prova_individual_service = ProvaIndividualService()


# Filtro Jinja2 customizado para obter basename de path
@app.template_filter('basename')
def basename_filter(path):
    """Retorna o nome base de um caminho de arquivo."""
    if path:
        return os.path.basename(path)
    return ''


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
        modo = request.form.get("modo", "simples")  # "simples" ou "ia"
        multiplas = request.form.get("multiplas", "false") == "true"
        quantidade = int(request.form.get("quantidade", 5))
        com_diagrama = request.form.get("com_diagrama") == "on"
        verificar_bibliografia = request.form.get("verificar_bibliografia") == "on"
        observacoes = request.form.get("observacoes", "").strip()
        
        try:
            # Geração de MÚLTIPLAS questões
            if multiplas:
                if modo == "ia" and IA_DISPONIVEL:
                    # Múltiplas com IA
                    questoes = gerar_multiplas_ia(materia, quantidade, topico, dificuldade)
                else:
                    # Múltiplas com templates
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
            
            # Geração de UMA questão
            else:
                if modo == "ia":
                    # Geração com IA real
                    if not IA_DISPONIVEL:
                        return render_template("index.html", erro="IA não disponível. Configure a API key no arquivo .env")
                    questao = gerar_questao_ia(
                        materia, topico, dificuldade, observacoes,
                        verificar_bibliografia=verificar_bibliografia
                    )
                else:
                    # Geração com templates (simples)
                    questao = gerar_questao_simples(materia, topico, dificuldade, com_diagrama)
                    questao["gerado_por_ia"] = False
                    
                    # Verificação bibliográfica também funciona com templates
                    if verificar_bibliografia and IA_DISPONIVEL:
                        from backend.agents.verificador_bibliografico import verificar_questao_com_ia
                        questao = verificar_questao_com_ia(questao)
                
                if observacoes:
                    questao["observacoes_professor"] = observacoes
                
                return render_template("questao.html", questao=questao, modo=modo)
        
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
        "versao": "2.0.0",
        "ambiente": settings.FLASK_ENV if hasattr(settings, 'FLASK_ENV') else 'development',
        "diagramas_dir": settings.DIAGRAMAS_DIR
    }
    return render_template("sobre.html", info=info)


# =============================================================================
# NOVAS ROTAS - FLUXO DE REVISÃO
# =============================================================================

@app.route("/banco-questoes")
def banco_questoes():
    """Página do banco de questões do professor."""
    tab = request.args.get("tab", "todas")
    materia = request.args.get("materia")
    
    # Obter questões conforme a tab
    if tab == "pendentes":
        questoes = revisao_service.obter_questoes_pendentes(materia=materia)
    elif tab == "aprovadas":
        questoes = revisao_service.obter_questoes_aprovadas(materia=materia)
    else:
        # Todas as questões
        pendentes = revisao_service.obter_questoes_pendentes(materia=materia)
        aprovadas = revisao_service.obter_questoes_aprovadas(materia=materia)
        questoes = pendentes + aprovadas
    
    # Estatísticas
    estatisticas = revisao_service.obter_estatisticas()
    
    return render_template(
        "banco_questoes.html",
        questoes=questoes,
        estatisticas=estatisticas,
        tab=tab
    )


@app.route("/revisar/<questao_id>")
def revisar_questao(questao_id):
    """Página de revisão de uma questão específica."""
    questao = revisao_service.obter_questao(questao_id)
    
    if not questao:
        return redirect(url_for('banco_questoes'))
    
    revisoes = revisao_service.obter_revisoes(questao_id)
    
    return render_template(
        "revisao_questao.html",
        questao=questao,
        revisoes=revisoes
    )


@app.route("/revisar/<questao_id>/salvar", methods=["POST"])
def salvar_revisao(questao_id):
    """Salva a revisão de uma questão."""
    acao = request.form.get("acao")
    comentarios = request.form.get("comentarios", "")
    sugestoes = request.form.get("sugestoes", "")
    nota_qualidade = request.form.get("nota_qualidade")
    
    # Checklist de avaliação
    precisao_cientifica = request.form.get("precisao_cientifica") == "true"
    clareza_enunciado = request.form.get("clareza_enunciado") == "true"
    adequacao_nivel = request.form.get("adequacao_nivel") == "true"
    
    # Fontes bibliográficas
    fontes_raw = request.form.getlist("fontes[]")
    fontes = []
    for fonte_json in fontes_raw:
        try:
            fonte = json.loads(fonte_json)
            fontes.append(fonte)
        except:
            pass
    
    if acao == "aprovar":
        resultado = revisao_service.aprovar_questao(
            questao_id=questao_id,
            comentarios=comentarios,
            fontes=fontes
        )
    elif acao == "rejeitar":
        resultado = revisao_service.rejeitar_questao(
            questao_id=questao_id,
            motivo=comentarios,
            sugestoes=sugestoes
        )
    elif acao == "corrigir":
        resultado = revisao_service.solicitar_correcoes(
            questao_id=questao_id,
            correcoes=sugestoes,
            comentarios=comentarios
        )
    else:
        return redirect(url_for('revisar_questao', questao_id=questao_id))
    
    return redirect(url_for('banco_questoes'))


@app.route("/questao/gerar-e-revisar", methods=["POST"])
def gerar_e_revisar():
    """Gera uma questão e redireciona para revisão."""
    # Obtém dados do formulário
    materia = request.form.get("materia", "fisica")
    topico = request.form.get("topico", "")
    dificuldade = request.form.get("dificuldade", "medio")
    modo = request.form.get("modo", "simples")
    com_diagrama = request.form.get("com_diagrama") == "on"
    observacoes = request.form.get("observacoes", "").strip()
    
    try:
        # Gerar questão
        if modo == "ia" and IA_DISPONIVEL:
            from backend.gerador_ia import gerar_questao_ia
            questao = gerar_questao_ia(materia, topico, dificuldade, observacoes)
        else:
            questao = gerar_questao_simples(materia, topico, dificuldade, com_diagrama)
        
        # Adicionar metadados
        questao["materia"] = materia
        questao["topico"] = topico
        questao["dificuldade"] = dificuldade
        questao["observacoes_professor"] = observacoes
        
        # Adicionar ao fluxo de revisão
        questao_id = revisao_service.adicionar_questao_para_revisao(questao)
        
        # Redirecionar para página de revisão
        return redirect(url_for('revisar_questao', questao_id=questao_id))
        
    except Exception as e:
        return render_template("index.html", erro=str(e))


# =============================================================================
# NOVAS ROTAS - MONTAGEM DE PROVAS INDIVIDUAIS
# =============================================================================

@app.route("/montar-prova")
def montar_prova():
    """Página para montar uma prova a partir de questões selecionadas."""
    # Obter IDs das questões da query string (vindas do banco de questões)
    questoes_ids = request.args.get("questoes", "").split(",")
    questoes_ids = [q.strip() for q in questoes_ids if q.strip()]
    
    # Buscar as questões
    questoes = []
    for questao_id in questoes_ids:
        questao = revisao_service.obter_questao(questao_id)
        if questao:
            questoes.append(questao)
    
    return render_template("montar_prova.html", questoes=questoes)


@app.route("/gerar-provas-individuais", methods=["POST"])
def gerar_provas_individuais():
    """Gera provas individuais para cada aluno."""
    # Obter dados do formulário
    titulo = request.form.get("titulo", "Prova")
    instituicao = request.form.get("instituicao", "")
    tempo_limite = request.form.get("tempo_limite")
    quantidade_alunos = int(request.form.get("quantidade_alunos", 30))
    
    # Questões selecionadas
    questoes_ids = request.form.getlist("questoes[]")
    
    # Opções de embaralhamento
    embaralhar_questoes = request.form.get("embaralhar_questoes") == "on"
    embaralhar_alternativas = request.form.get("embaralhar_alternativas") == "on"
    incluir_campo_nome = request.form.get("incluir_campo_nome") == "on"
    incluir_campo_matricula = request.form.get("incluir_campo_matricula") == "on"
    
    # Instruções
    instrucoes_text = request.form.get("instrucoes", "")
    instrucoes = [i.strip() for i in instrucoes_text.split("\n") if i.strip()] if instrucoes_text else None
    
    try:
        # Configurar geração
        config = ConfiguracaoProvaIndividual(
            titulo=titulo,
            questoes_ids=questoes_ids,
            quantidade_alunos=quantidade_alunos,
            embaralhar_questoes=embaralhar_questoes,
            embaralhar_alternativas=embaralhar_alternativas,
            instituicao=instituicao if instituicao else None,
            instrucoes=instrucoes,
            tempo_limite_min=int(tempo_limite) if tempo_limite else None,
            incluir_campo_nome=incluir_campo_nome,
            incluir_campo_matricula=incluir_campo_matricula,
            gerar_pdf=True,
            gerar_zip=True
        )
        
        # Gerar provas
        resultado = prova_individual_service.gerar_provas_individuais(config)
        
        if resultado.status == "erro":
            return render_template(
                "montar_prova.html",
                questoes=[],
                erro=resultado.erro
            )
        
        return render_template("provas_individuais.html", resultado=resultado)
        
    except Exception as e:
        return render_template(
            "montar_prova.html",
            questoes=[],
            erro=str(e)
        )


@app.route("/download/zip/<path:filename>")
def download_zip(filename):
    """Rota para download de arquivos ZIP."""
    try:
        directory = os.path.join(settings.OUTPUT_DIR, "provas_individuais")
        return send_from_directory(
            directory,
            filename,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"erro": str(e)}), 404


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
# NOVAS APIs - FLUXO DE REVISÃO E PROVAS INDIVIDUAIS
# =============================================================================

@app.route("/api/questoes/pendentes", methods=["GET"])
def api_questoes_pendentes():
    """API para listar questões pendentes de revisão."""
    materia = request.args.get("materia")
    limite = int(request.args.get("limite", 50))
    
    questoes = revisao_service.obter_questoes_pendentes(materia=materia, limite=limite)
    
    return jsonify({
        "questoes": questoes,
        "total": len(questoes)
    })


@app.route("/api/questoes/aprovadas", methods=["GET"])
def api_questoes_aprovadas():
    """API para listar questões aprovadas."""
    materia = request.args.get("materia")
    limite = int(request.args.get("limite", 100))
    
    questoes = revisao_service.obter_questoes_aprovadas(materia=materia, limite=limite)
    
    return jsonify({
        "questoes": questoes,
        "total": len(questoes)
    })


@app.route("/api/questao/<questao_id>", methods=["GET"])
def api_obter_questao(questao_id):
    """API para obter uma questão específica."""
    questao = revisao_service.obter_questao(questao_id)
    
    if not questao:
        return jsonify({"erro": "Questão não encontrada"}), 404
    
    return jsonify(questao)


@app.route("/api/questao/<questao_id>", methods=["DELETE"])
def api_excluir_questao(questao_id):
    """API para excluir uma questão."""
    # Por enquanto apenas remove do cache
    if questao_id in revisao_service._questoes_cache:
        del revisao_service._questoes_cache[questao_id]
        return jsonify({"sucesso": True})
    
    return jsonify({"erro": "Questão não encontrada"}), 404


@app.route("/api/questao/<questao_id>/aprovar", methods=["POST"])
def api_aprovar_questao(questao_id):
    """API para aprovar uma questão."""
    dados = request.get_json() or {}
    
    resultado = revisao_service.aprovar_questao(
        questao_id=questao_id,
        comentarios=dados.get("comentarios"),
        fontes=dados.get("fontes")
    )
    
    if resultado.get("sucesso"):
        return jsonify(resultado)
    return jsonify(resultado), 400


@app.route("/api/questao/<questao_id>/rejeitar", methods=["POST"])
def api_rejeitar_questao(questao_id):
    """API para rejeitar uma questão."""
    dados = request.get_json() or {}
    
    motivo = dados.get("motivo", "")
    if not motivo:
        return jsonify({"erro": "Motivo é obrigatório"}), 400
    
    resultado = revisao_service.rejeitar_questao(
        questao_id=questao_id,
        motivo=motivo,
        sugestoes=dados.get("sugestoes")
    )
    
    return jsonify(resultado)


@app.route("/api/provas-individuais", methods=["POST"])
def api_gerar_provas_individuais():
    """
    API para geração de provas individuais.
    
    Request Body:
        {
            "titulo": "Prova de Física",
            "questoes_ids": ["id1", "id2", ...],
            "quantidade_alunos": 30,
            "embaralhar_questoes": true,
            "embaralhar_alternativas": true,
            "instituicao": "Escola XYZ"
        }
    
    Response:
        {
            "lote_id": "...",
            "provas_geradas": 30,
            "caminho_zip": "...",
            "gabarito_consolidado": {...}
        }
    """
    dados = request.get_json()
    
    if not dados:
        return jsonify({"erro": "Dados não fornecidos"}), 400
    
    if not dados.get("questoes_ids"):
        return jsonify({"erro": "Nenhuma questão selecionada"}), 400
    
    try:
        config = ConfiguracaoProvaIndividual(
            titulo=dados.get("titulo", "Prova"),
            questoes_ids=dados["questoes_ids"],
            quantidade_alunos=dados.get("quantidade_alunos", 30),
            embaralhar_questoes=dados.get("embaralhar_questoes", True),
            embaralhar_alternativas=dados.get("embaralhar_alternativas", True),
            instituicao=dados.get("instituicao"),
            instrucoes=dados.get("instrucoes"),
            tempo_limite_min=dados.get("tempo_limite_min"),
            gerar_pdf=dados.get("gerar_pdf", True),
            gerar_zip=dados.get("gerar_zip", True)
        )
        
        resultado = prova_individual_service.gerar_provas_individuais(config)
        
        return jsonify({
            "lote_id": resultado.lote_id,
            "titulo": resultado.titulo,
            "provas_geradas": resultado.provas_geradas,
            "tempo_geracao_seg": resultado.tempo_geracao_seg,
            "caminho_zip": resultado.caminho_zip,
            "gabarito_consolidado": resultado.gabarito_consolidado,
            "status": resultado.status,
            "erro": resultado.erro
        })
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/api/lotes-provas", methods=["GET"])
def api_listar_lotes():
    """API para listar lotes de provas gerados."""
    limite = int(request.args.get("limite", 20))
    lotes = prova_individual_service.listar_lotes(limite=limite)
    
    return jsonify({
        "lotes": lotes,
        "total": len(lotes)
    })


@app.route("/api/estatisticas/revisao", methods=["GET"])
def api_estatisticas_revisao():
    """API para obter estatísticas do fluxo de revisão."""
    estatisticas = revisao_service.obter_estatisticas()
    return jsonify(estatisticas)


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
