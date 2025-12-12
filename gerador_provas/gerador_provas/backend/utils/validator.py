"""
Validador de respostas matemáticas.

Usa SymPy para comparar expressões matemáticas de forma simbólica.
"""

from sympy import sympify, Eq, simplify, S


def validar_resposta(resposta_aluno: str, resposta_correta: str) -> bool:
    """
    Valida se a resposta do aluno é equivalente à resposta correta.
    
    Args:
        resposta_aluno: Resposta fornecida pelo aluno
        resposta_correta: Resposta esperada (correta)
    
    Returns:
        True se as respostas são equivalentes, False caso contrário
    
    Exemplos:
        >>> validar_resposta("5", "5")
        True
        >>> validar_resposta("x**2", "x^2")
        True
        >>> validar_resposta("2+3", "5")
        True
        >>> validar_resposta("5", "10")
        False
    """
    try:
        # Converter strings para expressões SymPy
        expr_aluno = sympify(resposta_aluno)
        expr_correta = sympify(resposta_correta)
        
        # Verificar igualdade direta
        if expr_aluno == expr_correta:
            return True
        
        # Tentar simplificar a diferença
        diferenca = simplify(expr_aluno - expr_correta)
        if diferenca == 0:
            return True
        
        # Tentar com Eq e simplify
        resultado = simplify(Eq(expr_aluno, expr_correta))
        
        # Converter resultado SymPy para booleano Python
        if resultado == S.true or resultado is S.true:
            return True
        if resultado == S.false or resultado is S.false:
            return False
        
        # Se não conseguiu determinar, comparar numericamente se possível
        try:
            val_aluno = float(expr_aluno.evalf())
            val_correta = float(expr_correta.evalf())
            return abs(val_aluno - val_correta) < 1e-9
        except:
            pass
        
        return False
        
    except Exception:
        # Se não conseguir parsear as expressões, retorna False
        return False
