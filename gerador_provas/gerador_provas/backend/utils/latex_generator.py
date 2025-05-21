from pylatex import Document, Section, Itemize

def gerar_pdf(questoes, caminho_saida="output/prova.pdf"):
    doc = Document()
    with doc.create(Section("Prova Gerada")):
        with doc.create(Itemize()) as lista:
            for q in questoes:
                lista.add_item(q["enunciado"])
    doc.generate_pdf(caminho_saida, clean_tex=True)
