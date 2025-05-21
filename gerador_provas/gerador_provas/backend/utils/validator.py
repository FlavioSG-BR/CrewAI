from sympy import sympify, Eq, simplify

def validar_resposta(resposta_aluno: str, resposta_correta: str) -> bool:
    try:
        return simplify(Eq(sympify(resposta_aluno), sympify(resposta_correta)))
    except:
        return False

# Exemplo de uso:
# validar_resposta("x^2", "x**2")  # Retorna True
