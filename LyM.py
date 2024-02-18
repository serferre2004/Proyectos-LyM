import re
#Bugs actuales:
"""
No se están identificando los tokens dentro de la categoria CONSTANT y en su lugar se asignan como VARIABLE, aunque esta asignacion para estos tokens sea incorrecta
en la gran mayoria de los casos es irrelevante para decidir si el codigo esta bien o mal pues una variable puede ser una constante y el bug se arregla al pedirle que busque dentro de VARIABLES
sin embargo en = name n esto no funciona al usar una de las constantes pues esta esperando un numero o especificamente una de dichas constantes, por lo que no es posible emplear la categoria VARIABLE.-ARREGLADO


"""
def tokenize(code):
    # Expresiones regulares para diferentes tipos de tokens
    token_specification = [
        ("KEYWORD", r"\b(?:move-face|run-dirs|move-dir|defvar|move|skip|turn|face|put|pick|if|loop|repeat|defun|null)\b"),
        ("CONSTANT", r"\b(?:Dim|myXpos|myYpos|myChips|myBalloons|balloonsHere|ChipsHere|Spaces)\b"),
        ("CONDITIONS", r"(?:can-move\?|can-pick\?|isZero\?|not|facing\?|blocked\?|can-put\?)"),
        ("DIRECTION", r":(?:north|south|east|west|left|right|around|front|back|up|down)"),
        ("ACTION", r":(?:balloons|chips)"),
        ("NUMBER", r"\b\d+\b"),
        ("VARIABLE", r"\b[a-zA-Z_](?<!:)[a-zA-Z0-9_]*\b"),
        ("OPERATOR", r"[=()]"),
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

class SyntaxError(Exception):
    pass

constants = ["Dim", "myXpos", "myYpos", "myChips", "myBalloons", "balloonsHere", "ChipsHere", "Spaces"]
stack = []  # Pila para manejar los paréntesis
def verify_parenthesis(token_iter):
    close_paren_token = next(token_iter)
    if close_paren_token[0] == 'OPERATOR' and close_paren_token[1] == ')':
        if not stack or stack[-1][1] != '(':
            raise SyntaxError("Unmatched closing parenthesis")
        stack.pop()
    else:
        raise SyntaxError("Expected closing parenthesis after variable declaration")
def parse_commands(token_iter, token):
    """
    Analiza una lista de tokens basada en la gramática del lenguaje.
    
    Args:
        token_iter : Iterador de tokens a parsear.
    
    Returns:
        bool: True si la sintaxis es correcta, False si hay un error.
    """
    
    if token[0] == 'OPERATOR' :
        if token[1] == '(':
            stack.append(token)
        elif token[1] == ')':
            if not stack or stack[-1][1] != '(':
                raise SyntaxError("Unmatched closing parenthesis")
            stack.pop()
    else:
        raise SyntaxError("Expected '('")
    token = next(token_iter)
            
    if token[1] == '=':
        # Se espera que el siguiente token sea el nombre de la variable
        name_token = next(token_iter)
        if name_token[0] != 'VARIABLE':
            raise SyntaxError(f"Expected a variable name after '=', got {name_token[1]}")

        # Se espera que el siguiente token sea un número o una constante
        value_token = next(token_iter)
        if value_token[0] not in ['NUMBER'] and value_token[0] not in ['CONSTANT']:
            raise SyntaxError(f"Expected a number or a constant after variable name, got {value_token[1]}")

        # Se espera un paréntesis de cierre después de la asignación
        verify_parenthesis(token_iter)
        
#Defvar
    elif token[0] == 'KEYWORD' and token[1] == 'defvar':
        # Esperamos que el siguiente token sea el nombre de la variable
        name_token = next(token_iter)
        if name_token[0] != 'VARIABLE':
            raise SyntaxError(f"Expected variable name, got {name_token[1]}")
        
        # Esperamos que el siguiente token sea un número o una constante
        value_token = next(token_iter)
        if value_token[0] not in ['NUMBER', 'CONSTANT']:
            raise SyntaxError(f"Expected number or constant, got {value_token[1]}")
        
        # Se espera un paréntesis de cierre después de la asignación
        verify_parenthesis(token_iter)
        
#Move      
    elif token[0] == 'KEYWORD' and token[1] == 'move':
        # Se espera que el token siguiente sea un número, una variable o una constante
        n_token = next(token_iter)
        if n_token[0] not in ['NUMBER', 'VARIABLE', 'CONSTANT']:
            raise SyntaxError(f"Expected a number, variable, or constant after 'move', got {n_token[1]}")

        # Se espera un paréntesis de cierre después de la asignación
        verify_parenthesis(token_iter)

#Skip
    elif token[0] == 'KEYWORD' and token[1] == 'skip':
        # Se espera que el token siguiente sea un número, una variable o una constante
        n_token = next(token_iter)
        if n_token[0] not in ['NUMBER', 'VARIABLE', 'CONSTANT']:
            raise SyntaxError(f"Expected a number, variable, or constant after 'skip', got {n_token[1]}")
        
        # Se espera un paréntesis de cierre después de la asignación
        verify_parenthesis(token_iter)
#Turn
    elif token[0] == 'KEYWORD' and token[1] == 'turn':
        # Se espera que el token siguiente sea una de las direcciones válidas
        direction_token = next(token_iter)
        if direction_token[1] not in [':left', ':right', ':around']:
            raise SyntaxError(f"Expected :left, :right, or :around after 'turn', got {direction_token[1]}")

        # Se espera un paréntesis de cierre después de la asignación
        verify_parenthesis(token_iter)
#Face 
    elif token[0] == 'KEYWORD' and token[1] == 'face':
        # Se espera que el token siguiente sea una de las direcciones válidas
        direction_token = next(token_iter)
        if direction_token[1] not in [':north', ':south', ':east', ':west']:
            raise SyntaxError(f"Expected :north, :south, :east, or :west after 'face', got {direction_token[1]}")

        # Se espera un paréntesis de cierre después de la asignación
        verify_parenthesis(token_iter)
#Put
    elif token[0] == 'KEYWORD' and token[1] == 'put':
        # Se espera que el token siguiente sea :balloons o :chips
        item_token = next(token_iter)
        if item_token[0] != 'ACTION' or item_token[1] not in [':balloons', ':chips']:
            raise SyntaxError(f"Expected :balloons or :chips after 'put', got {item_token[1]}")

        # Se espera que el siguiente token sea un número o una variable
        quantity_token = next(token_iter)
        if quantity_token[0] not in ['NUMBER', 'VARIABLE']:
            raise SyntaxError(f"Expected a number or variable after {item_token[1]}, got {quantity_token[1]}")

        # Se espera un paréntesis de cierre después de la asignación
        verify_parenthesis(token_iter)
#Pick
    elif token[0] == 'KEYWORD' and token[1] == 'pick':
        # Se espera que el token siguiente sea :balloons o :chips
        item_token = next(token_iter)
        if item_token[0] != 'ACTION' or item_token[1] not in [':balloons', ':chips']:
            raise SyntaxError(f"Expected :balloons or :chips after 'pick', got {item_token[1]}")

        # Se espera que el siguiente token sea un número o una variable
        quantity_token = next(token_iter)
        if quantity_token[0] not in ['NUMBER', 'VARIABLE']:
            raise SyntaxError(f"Expected a number or variable after {item_token[1]}, got {quantity_token[1]}")

        # Se espera un paréntesis de cierre después de la asignación
        verify_parenthesis(token_iter)
#move-dir
    elif token[0] == 'KEYWORD' and token[1] == 'move-dir':
        # Se espera que el siguiente token sea un número o una variable que represente la cantidad de pasos
        steps_token = next(token_iter)
        if steps_token[0] not in ['NUMBER', 'VARIABLE']:
            raise SyntaxError(f"Expected a number or variable for steps, got {steps_token[1]}")

        # Se espera que el siguiente token sea una de las direcciones válidas
        direction_token = next(token_iter)
        if direction_token[1] not in [':front', ':right', ':left', ':back']:
            raise SyntaxError(f"Expected a direction (:front, :right, :left, :back) after steps, got {direction_token[1]}")

        # Se espera un paréntesis de cierre después de la asignación
        verify_parenthesis(token_iter)

#Run-dirs
    elif token[0] == 'KEYWORD' and token[1] == 'run-dirs':
        # Se espera que el token siguiente sea un paréntesis abierto '('
        open_paren_token = next(token_iter)
        if open_paren_token[0] != 'OPERATOR' or open_paren_token[1] != '(':
            raise SyntaxError("Expected '(' after 'run-dirs' keyword")

        # Recopilar las direcciones hasta que encontremos el paréntesis de cierre ')'
        directions = []
        while True:
            direction_token = next(token_iter)
            if direction_token[0] == 'OPERATOR' and direction_token[1] == ')':
                break
            elif direction_token[0] == 'DIRECTION' and direction_token[1] in [':front', ':right', ':left', ':back']:
                directions.append(direction_token[1])
            else:
                # Si el token no es una dirección válida, lanzar un error
                raise SyntaxError(f"Expected a direction, got {direction_token[1]}")
        
        # Verificar que se haya recogido al menos una dirección
        if not directions:
            raise SyntaxError("No directions provided for 'run-dirs' command")
        verify_parenthesis(token_iter)
#Move-face
    elif token[0] == 'KEYWORD' and token[1] == 'move-face':
        # Se espera que el siguiente token sea un número o una variable que represente la cantidad de pasos
        steps_token = next(token_iter)
        if steps_token[0] not in ['NUMBER', 'VARIABLE']:
            raise SyntaxError(f"Expected a number or variable for steps, got {steps_token[1]}")

        # Se espera que el siguiente token sea una de las direcciones válidas
        direction_token = next(token_iter)
        if direction_token[0] != 'DIRECTION' or direction_token[1] not in [':north', ':south', ':west', ':east']:
            raise SyntaxError(f"Expected a direction (:north, :south, :west, :east) after steps, got {direction_token[1]}")
        
        # Se espera un paréntesis de cierre después de la asignación
        verify_parenthesis(token_iter)
        
#Null
    elif token[0] == 'KEYWORD' and token[1] == 'null':
        # Se espera un paréntesis de cierre después del token null
        verify_parenthesis(token_iter)
    # Aquí se agregarían más condiciones para manejar otros tipos de tokens y estructuras
    elif token[0] == 'KEYWORD':
        parse_controlstructs(token_iter, token)
    token = next(token_iter)
    # Verificamos si hay paréntesis sin cerrar
    
def parse_controlstructs(token_iter, token):

        
#If 
    if token[0] == 'KEYWORD' and token[1] == 'if':
        # Se espera que el siguiente token sea una condición válida
        open_paren_token = next(token_iter)
        if open_paren_token[0] != 'OPERATOR' or open_paren_token[1] != '(':
            raise SyntaxError("Expected '(' after 'if' keyword")
        stack.append(open_paren_token)
        #Se Recorre el parentesis hasta que encontremos el paréntesis de cierre ')'
        condition_token = next(token_iter)
        token_siguiente = next(token_iter)[1] # token siguiente a condition_token
        if condition_token[0] == 'OPERATOR' and condition_token[1] == ')':
            raise SyntaxError('No condition provided')
        elif condition_token[0] == 'CONDITIONS' and condition_token[1] in ["can-move?", "can-pick?", "isZero?", "not", "facing?", "blocked?", "can-put?"]:
            if condition_token[1] == 'facing?' and token_siguiente not in [':north', ':south', ':west', ':east']:
                raise SyntaxError(f"Expected :north, :south, :west, :east, got {token_siguiente}")
            if condition_token[1] == 'can-move?' and token_siguiente not in [':north', ':south', ':west', ':east']:
                raise SyntaxError(f"Expected :north, :south, :west, :east, got {token_siguiente}")
            else:
                verify_parenthesis(token_iter)     
        else:
            # Si el token no es una dirección válida, lanzar un error
            raise SyntaxError(f"Expected a condition, got {condition_token[1]}") 
        token = next(token_iter)
        parse_commands(token_iter, token)
        parse_commands(token_iter, token)
        print(token)
        verify_parenthesis(token_iter)
    # Aquí se agregarían más condiciones para manejar otros tipos de tokens y estructuras
    
    else:
        raise SyntaxError(f"Unexpected token: {token[1]}")
    token = next(token_iter)

# Verificamos si hay paréntesis sin cerrar
    if stack:
        raise SyntaxError("Unmatched opening parenthesis")


# Estructura de Token
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value


# Llamada a la función de análisis

