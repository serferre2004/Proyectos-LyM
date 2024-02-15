import re

def tokenize(code):
    # Expresiones regulares para diferentes tipos de tokens
    token_specification = [
        ("KEYWORD", r"\b(?:defvar|move|skip|turn|pick|if|loop|repeat|defun)\b"),
        ("DIRECTION", r":(?:north|south|east|west|left|right|around)"),
        ("ACTION", r":(?:balloons|chips)"),
        ("NUMBER", r"\b\d+\b"),
        ("VARIABLE", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
        ("OPERATOR", r"[=())]"),
        ("SKIP", r"[ \t\n]"),  # Espacios, tabuladores y saltos de línea
    ]

    # Compila las expresiones regulares
    token_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    get_token = re.compile(token_regex).match

    # Tokeniza
    pos = 0
    tokens = []
    while pos < len(code):
        match = get_token(code, pos)
        if match is not None:
            type = match.lastgroup
            if type != "SKIP":
                value = match.group(type)
                tokens.append((type, value))
            pos = match.end()
        else:
            raise SyntaxError("Unknown character: %r" % code[pos])

    return tokens

# Ejemplo de uso
code = "(move 1)"
print(tokenize(code))

class SyntaxError(Exception):
    pass

def parse(tokens):
    """
    Analiza una lista de tokens basada en la gramática del lenguaje.
    
    Args:
        tokens (list): Lista de tokens para analizar.
    
    Returns:
        bool: True si la sintaxis es correcta, False si hay un error.
    """
    token_iter = iter(tokens)
    stack = []  # Pila para manejar los paréntesis

    try:
        while True:  # Continuar hasta que no haya más tokens
            token = next(token_iter)

            if token[0] == 'OPERATOR' :
                if token[1] == '(':
                    stack.append(token)
                
                elif token[1] == ')':
                    if not stack or stack[-1][1] != '(':
                        raise SyntaxError("Unmatched closing parenthesis")
                    stack.pop()
                else:
                    raise SyntaxError(f"Unexpected operator: {token[1]}")
            
            elif token[0] == 'KEYWORD' and token[1] == 'defvar':
                # Esperamos que el siguiente token sea el nombre de la variable
                name_token = next(token_iter)
                if name_token[0] != 'VARIABLE':
                    raise SyntaxError(f"Expected variable name, got {name_token[1]}")
                
                # Esperamos que el siguiente token sea un número o una constante
                value_token = next(token_iter)
                if value_token[0] not in ['NUMBER', 'CONSTANT']:
                    raise SyntaxError(f"Expected number or constant, got {value_token[1]}")
                
                # Aquí debería haber un paréntesis de cierre para terminar la instrucción 'defvar'
                close_paren_token = next(token_iter)
                if close_paren_token[0] == 'OPERATOR' and close_paren_token[1] == ')':
                    if not stack or stack[-1][1] != '(':
                        raise SyntaxError("Unmatched closing parenthesis")
                    stack.pop()
                else:
                    raise SyntaxError("Expected closing parenthesis after variable declaration")
                
            elif token[0] == 'KEYWORD' and token[1] == 'move':
                # Esperamos que el siguiente token sea un número, una variable o una constante
                n_token = next(token_iter)
                if n_token[0] not in ['NUMBER', 'VARIABLE', 'CONSTANT']:
                    raise SyntaxError(f"Expected a number, variable, or constant after 'move', got {n_token[1]}")

                # Verificamos que haya un paréntesis de cierre después del comando 'move'
                close_paren_token = next(token_iter)
                if close_paren_token[0] == 'OPERATOR' and close_paren_token[1] == ')':
                    if not stack or stack[-1][1] != '(':
                        raise SyntaxError("Unmatched closing parenthesis")
                    stack.pop()
                else:
                    raise SyntaxError("Expected closing parenthesis after variable declaration")

            elif token[0] == 'KEYWORD' and token[1] == 'skip':
                # Se espera que el token siguiente sea un número, una variable o una constante
                n_token = next(token_iter)
                if n_token[0] not in ['NUMBER', 'VARIABLE', 'CONSTANT']:
                    raise SyntaxError(f"Expected a number, variable, or constant after 'skip', got {n_token[1]}")

                close_paren_token = next(token_iter)
                if close_paren_token[0] == 'OPERATOR' and close_paren_token[1] == ')':
                    if not stack or stack[-1][1] != '(':
                        raise SyntaxError("Unmatched closing parenthesis")
                    stack.pop()
                else:
                    raise SyntaxError("Expected closing parenthesis after variable declaration")


            # Aquí se agregarían más condiciones para manejar otros tipos de tokens y estructuras
            
            else:
                raise SyntaxError(f"Unexpected token: {token[1]}")

        # Verificamos si hay paréntesis sin cerrar
        if stack:
            raise SyntaxError("Unmatched opening parenthesis")
    
    except StopIteration:
        # Hemos llegado al final de los tokens sin errores
        return not stack  # La sintaxis es correcta si no hay paréntesis sin cerrar
    
    except SyntaxError as e:
        print(f"Syntax error: {e}")
        return False

# Estructura de Token para el ejemplo
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value


# Llamada a la función de análisis
is_syntax_correct = parse(tokenize(code))
print("Syntax is correct:", is_syntax_correct)