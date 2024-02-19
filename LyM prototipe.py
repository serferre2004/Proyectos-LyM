import re
#Bugs actuales:
"""
No se están identificando los tokens dentro de la categoria CONSTANT y en su lugar se asignan como VARIABLE, aunque esta asignacion para estos tokens sea incorrecta
en la gran mayoria de los casos es irrelevante para decidir si el codigo esta bien o mal pues una variable puede ser una constante y el bug se arregla al pedirle que busque dentro de VARIABLES
sin embargo en = name n esto no funciona al usar una de las constantes pues esta esperando un numero o especificamente una de dichas constantes, por lo que no es posible emplear la categoria VARIABLE.-ARREGLADO


"""
class function :
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters  #List of tuples (parameter name, parameter type)
        
class variable :
    def __init__(self, name, value):
        self.name = name
        self.value = value
        
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

# Pruebas, se inserta la linea de codigo a probar, se sugiere ir agregando en cascada el nuevo comando a implementar
code =  "(defvar name 10) (= name Dim) (move Dim) (skip 2) (move 10) (turn :right) (face :east) (put :chips n) (pick :balloons n) (move-dir n :front) (run-dirs (:left :left :right)) (move-face n :north) (null) (if (not(can-put? chips)) (move 5) (null)) (loop (not(can-put? chips)) (move 5)) (repeat n (null) (defun foo (a b) (move name) (skip 4)))"
code = "(defvar bar 5) (= bar 10) (defun foo (a b) (move bar) (null)) (foo 5 10)"
print(tokenize(code))

class SyntaxError(Exception):
    pass

def parse_comands(tokens):
    """
    Analiza una lista de tokens basada en la gramática del lenguaje.
    
    Args:
        tokens (list): Lista de tokens para analizar.
    
    Returns:
        bool: True si la sintaxis es correcta, False si hay un error.
    """
    constants = ["Dim", "myXpos", "myYpos", "myChips", "myBalloons", "balloonsHere", "ChipsHere", "Spaces"]
    functions = {}
    variables = {}
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
                    
                elif token[1] == '=':
                    # Se espera que el siguiente token sea el nombre de la variable
                    name_token = next(token_iter)
                    if name_token[0] != 'VARIABLE':
                        raise SyntaxError(f"Expected a variable name after '=', got {name_token[1]}")
                    if name_token[1] not in variables:
                        raise SyntaxError(f"Variable {name_token[1]} not exist")
                    # Se espera que el siguiente token sea un número o una constante
                    value_token = next(token_iter)
                    if value_token[0] not in ['NUMBER'] and value_token[0] not in ['CONSTANT']:
                        raise SyntaxError(f"Expected a number or a constant after variable name, got {value_token[1]}")

                    # Se espera un paréntesis de cierre después de la asignación
                    close_paren_token = next(token_iter)
                    if close_paren_token[0] == 'OPERATOR' and close_paren_token[1] == ')':
                        if not stack or stack[-1][1] != '(':
                            raise SyntaxError("Unmatched closing parenthesis")
                        stack.pop()
                    else:
                        raise SyntaxError("Expected closing parenthesis after variable declaration")
                    variables[name_token[1]].value = value_token[1]
                else:
                    raise SyntaxError(f"Unexpected operator: {token[1]}")
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
                close_paren_token = next(token_iter)
                if close_paren_token[0] == 'OPERATOR' and close_paren_token[1] == ')':
                    if not stack or stack[-1][1] != '(':
                        raise SyntaxError("Unmatched closing parenthesis")
                    stack.pop()
                else:
                    raise SyntaxError("Expected closing parenthesis after variable declaration")
                
                exec(f"var_{name_token[1]} = variable(name_token[1], value_token[1])") 
                exec(f"variables[name_token[1]] = var_{name_token[1]}")
#Move      
            elif token[0] == 'KEYWORD' and token[1] == 'move':
                # Se espera que el token siguiente sea un número, una variable o una constante
                n_token = next(token_iter)
                if n_token[0] not in ['NUMBER', 'CONSTANT'] and n_token[1] not in variables:
                    raise SyntaxError(f"Expected a number, variable, or constant after 'move', got {n_token[1]}")

                # Se espera un paréntesis de cierre después de la asignación
                close_paren_token = next(token_iter)
                if close_paren_token[0] == 'OPERATOR' and close_paren_token[1] == ')':
                    if not stack or stack[-1][1] != '(':
                        raise SyntaxError("Unmatched closing parenthesis")
                    stack.pop()
                else:
                    raise SyntaxError("Expected closing parenthesis after variable declaration")

#Skip
            elif token[0] == 'KEYWORD' and token[1] == 'skip':
                # Se espera que el token siguiente sea un número, una variable o una constante
                n_token = next(token_iter)
                if n_token[0] not in ['NUMBER', 'CONSTANT'] and n_token[1] not in variables:
                    raise SyntaxError(f"Expected a number, variable, or constant after 'skip', got {n_token[1]}")
                
                # Se espera un paréntesis de cierre después de la asignación
                close_paren_token = next(token_iter)
                if close_paren_token[0] == 'OPERATOR' and close_paren_token[1] == ')':
                    if not stack or stack[-1][1] != '(':
                        raise SyntaxError("Unmatched closing parenthesis")
                    stack.pop()
                else:
                    raise SyntaxError("Expected closing parenthesis after variable declaration")
#Turn
            elif token[0] == 'KEYWORD' and token[1] == 'turn':
                # Se espera que el token siguiente sea una de las direcciones válidas
                direction_token = next(token_iter)
                if direction_token[1] not in [':left', ':right', ':around']:
                    raise SyntaxError(f"Expected :left, :right, or :around after 'turn', got {direction_token[1]}")

                # Se espera un paréntesis de cierre después de la asignación
                close_paren_token = next(token_iter)
                if close_paren_token[0] == 'OPERATOR' and close_paren_token[1] == ')':
                    if not stack or stack[-1][1] != '(':
                        raise SyntaxError("Unmatched closing parenthesis")
                    stack.pop()
                else:
                    raise SyntaxError("Expected closing parenthesis after variable declaration")
#Face 
            elif token[0] == 'KEYWORD' and token[1] == 'face':
                # Se espera que el token siguiente sea una de las direcciones válidas
                direction_token = next(token_iter)
                if direction_token[1] not in [':north', ':south', ':east', ':west']:
                    raise SyntaxError(f"Expected :north, :south, :east, or :west after 'face', got {direction_token[1]}")

                # Se espera un paréntesis de cierre después de la asignación
                close_paren_token = next(token_iter)
                if close_paren_token[0] == 'OPERATOR' and close_paren_token[1] == ')':
                    if not stack or stack[-1][1] != '(':
                        raise SyntaxError("Unmatched closing parenthesis")
                    stack.pop()
                else:
                    raise SyntaxError("Expected closing parenthesis after variable declaration")
#Put
            elif token[0] == 'KEYWORD' and token[1] == 'put':
                # Se espera que el token siguiente sea :balloons o :chips
                item_token = next(token_iter)
                if item_token[0] != 'ACTION' or item_token[1] not in [':balloons', ':chips']:
                    raise SyntaxError(f"Expected :balloons or :chips after 'put', got {item_token[1]}")

                # Se espera que el siguiente token sea un número o una variable
                quantity_token = next(token_iter)
                if quantity_token[0] not in ['NUMBER', 'CONSTANT'] and quantity_token[1] not in variables:
                    raise SyntaxError(f"Expected a number or variable after {item_token[1]}, got {quantity_token[1]}")

                # Se espera un paréntesis de cierre después de la asignación
                close_paren_token = next(token_iter)
                if close_paren_token[0] == 'OPERATOR' and close_paren_token[1] == ')':
                    if not stack or stack[-1][1] != '(':
                        raise SyntaxError("Unmatched closing parenthesis")
                    stack.pop()
                else:
                    raise SyntaxError("Expected closing parenthesis after variable declaration")
#Pick
            elif token[0] == 'KEYWORD' and token[1] == 'pick':
                # Se espera que el token siguiente sea :balloons o :chips
                item_token = next(token_iter)
                if item_token[0] != 'ACTION' or item_token[1] not in [':balloons', ':chips']:
                    raise SyntaxError(f"Expected :balloons or :chips after 'pick', got {item_token[1]}")

                # Se espera que el siguiente token sea un número o una variable
                quantity_token = next(token_iter)
                if quantity_token[0] not in ['NUMBER', 'CONSTANT'] and quantity_token[1] not in variables:
                    raise SyntaxError(f"Expected a number or variable after {item_token[1]}, got {quantity_token[1]}")

                # Se espera un paréntesis de cierre después de la asignación
                close_paren_token = next(token_iter)
                if close_paren_token[0] == 'OPERATOR' and close_paren_token[1] == ')':
                    if not stack or stack[-1][1] != '(':
                        raise SyntaxError("Unmatched closing parenthesis")
                    stack.pop()
                else:
                    raise SyntaxError("Expected closing parenthesis after variable declaration")
#move-dir
            elif token[0] == 'KEYWORD' and token[1] == 'move-dir':
                # Se espera que el siguiente token sea un número o una variable que represente la cantidad de pasos
                steps_token = next(token_iter)
                if steps_token[0] not in ['NUMBER', 'CONSTANT'] and steps_token[1] not in variables:
                    raise SyntaxError(f"Expected a number or variable for steps, got {steps_token[1]}")

                # Se espera que el siguiente token sea una de las direcciones válidas
                direction_token = next(token_iter)
                if direction_token[1] not in [':front', ':right', ':left', ':back']:
                    raise SyntaxError(f"Expected a direction (:front, :right, :left, :back) after steps, got {direction_token[1]}")

                # Se espera un paréntesis de cierre después de la asignación
                close_paren_token = next(token_iter)
                if close_paren_token[0] == 'OPERATOR' and close_paren_token[1] == ')':
                    if not stack or stack[-1][1] != '(':
                        raise SyntaxError("Unmatched closing parenthesis")
                    stack.pop()
                else:
                    raise SyntaxError("Expected closing parenthesis after variable declaration")

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
#Move-face
            elif token[0] == 'KEYWORD' and token[1] == 'move-face':
                # Se espera que el siguiente token sea un número o una variable que represente la cantidad de pasos
                steps_token = next(token_iter)
                if steps_token[0] not in ['NUMBER', 'CONSTANT'] and steps_token[1] not in variables:
                    raise SyntaxError(f"Expected a number or variable for steps, got {steps_token[1]}")

                # Se espera que el siguiente token sea una de las direcciones válidas
                direction_token = next(token_iter)
                if direction_token[0] != 'DIRECTION' or direction_token[1] not in [':north', ':south', ':west', ':east']:
                    raise SyntaxError(f"Expected a direction (:north, :south, :west, :east) after steps, got {direction_token[1]}")
                
                # Se espera un paréntesis de cierre después de la asignación
                close_paren_token = next(token_iter)
                if close_paren_token[0] == 'OPERATOR' and close_paren_token[1] == ')':
                    if not stack or stack[-1][1] != '(':
                        raise SyntaxError("Unmatched closing parenthesis")
                    stack.pop()
                else:
                    raise SyntaxError("Expected closing parenthesis after variable declaration")
                
#Null
            elif token[0] == 'KEYWORD' and token[1] == 'null':
                # Se espera un paréntesis de cierre después del token null
                close_paren_token = next(token_iter)
                if close_paren_token[0] == 'OPERATOR' and close_paren_token[1] == ')':
                    if not stack or stack[-1][1] != '(':
                        raise SyntaxError("Unmatched closing parenthesis")
                    stack.pop()
                else:
                    raise SyntaxError("Expected closing parenthesis after variable declaration")
#If
            elif token[0] == 'KEYWORD' and token[1] == 'if':
                # Se espera que el token siguiente sea un paréntesis abierto '('
                open_paren_token = next(token_iter)
                if open_paren_token[0] != 'OPERATOR' or open_paren_token[1] != '(':
                    raise SyntaxError("Expected '(' after 'if' keyword")

                # Recopilar las direcciones hasta que encontremos el paréntesis de cierre ')'
                conditions = []
                while True:
                    conditions_tokens = next(token_iter)
                    token_siguiente = next(token_iter)[1] # token siguiente a condition_token
                    if conditions_tokens[0] == 'OPERATOR' and conditions_tokens[1] == ')':
                        break
                    elif conditions_tokens[1] == 'not' and token_siguiente == '(':
                        conditions.append(conditions_tokens[1])
                    elif conditions_tokens[0] == 'CONDITIONS' and conditions_tokens[1] in  ["can-move?", "can-pick?", "isZero?", "not", "facing?", "blocked?", "can-put?"]:
                        conditions.append(conditions_tokens[1])
                    elif conditions_tokens[0] == 'DIRECTION' and conditions_tokens[1] in  [':north', ':south', ':west', ':east']:
                        conditions.append(conditions_tokens[1])
                    elif conditions_tokens[0] == 'NUMBER':
                        conditions.append(conditions_tokens[1])
                    elif conditions_tokens[0] == 'VARIABLE' and conditions_tokens[1] in  ['chips', 'balloons']:
                        conditions.append(conditions_tokens[1])
                    else:
                        # Si el token no es una dirección válida, lanzar un error
                        raise SyntaxError(f"Expected a condition, got {conditions_tokens[1]}")
                
                # Verificar que se haya recogido al menos una dirección
                if not conditions:
                    raise SyntaxError("No conditions provided for 'if' command")
                
#repeat      
            elif token[0] == 'KEYWORD' and token[1] == 'loop':
                # Se espera que el token siguiente sea un paréntesis abierto '('
                open_paren_token = next(token_iter)
                if open_paren_token[0] != 'OPERATOR' or open_paren_token[1] != '(':
                    raise SyntaxError("Expected '(' after 'loop' keyword")

                # Recopilar las direcciones hasta que encontremos el paréntesis de cierre ')'
                conditions = []
                while True:
                    conditions_tokens = next(token_iter)
                    token_siguiente = next(token_iter)[1] # token siguiente a condition_token
                    if conditions_tokens[0] == 'OPERATOR' and conditions_tokens[1] == ')':
                        break
                    elif conditions_tokens[1] == 'not' and token_siguiente == '(':
                        conditions.append(conditions_tokens[1])
                    elif conditions_tokens[0] == 'CONDITIONS' and conditions_tokens[1] in  ["can-move?", "can-pick?", "isZero?", "not", "facing?", "blocked?", "can-put?"]:
                        conditions.append(conditions_tokens[1])
                    elif conditions_tokens[0] == 'DIRECTION' and conditions_tokens[1] in  [':north', ':south', ':west', ':east']:
                        conditions.append(conditions_tokens[1])
                    elif conditions_tokens[0] == 'NUMBER':
                        conditions.append(conditions_tokens[1])
                    elif conditions_tokens[0] == 'VARIABLE' and conditions_tokens[1] in  ['chips', 'balloons']:
                        conditions.append(conditions_tokens[1])
                    else:
                        # Si el token no es una dirección válida, lanzar un error
                        raise SyntaxError(f"Expected a condition, got {conditions_tokens[1]}")
                
                # Verificar que se haya recogido al menos una dirección
                if not conditions:
                    raise SyntaxError("No conditions provided for 'loop' command")
                
#repeatTimes      
            elif token[0] == 'KEYWORD' and token[1] == 'repeat':
                # Se espera que el token siguiente sea un paréntesis abierto '('
                open_paren_token = next(token_iter)
                token_siguiente = next(token_iter)[1] # token siguiente a condition_token
                if token_siguiente != '(':
                    raise SyntaxError("Expected '(' after variable")

                # Recopilar las direcciones hasta que encontremos el paréntesis de cierre ')'
                conditions = []
                while True:
                    conditions_tokens = next(token_iter)
                    token_siguiente = next(token_iter)[1] # token siguiente a condition_token
                    if conditions_tokens[0] == 'OPERATOR' and conditions_tokens[1] == ')':
                        break
                    elif conditions_tokens[1] == 'not' and token_siguiente == '(':
                        conditions.append(conditions_tokens[1])
                    elif conditions_tokens[0] == 'CONDITIONS' and conditions_tokens[1] in  ["can-move?", "can-pick?", "isZero?", "not", "facing?", "blocked?", "can-put?"]:
                        conditions.append(conditions_tokens[1])
                    elif conditions_tokens[0] == 'DIRECTION' and conditions_tokens[1] in  [':north', ':south', ':west', ':east']:
                        conditions.append(conditions_tokens[1])
                    elif conditions_tokens[0] == 'NUMBER':
                        conditions.append(conditions_tokens[1])
                    elif conditions_tokens[0] == 'VARIABLE' and conditions_tokens[1] in  ['chips', 'balloons']:
                        conditions.append(conditions_tokens[1])
                    else:
                        # Si el token no es una dirección válida, lanzar un error
                        raise SyntaxError(f"Expected a condition, got {conditions_tokens[1]}")
                
                # Verificar que se haya recogido al menos una dirección
                if not conditions:
                    raise SyntaxError("No conditions provided for 'run-dirs' command")
#Defun
            elif token[0] == 'KEYWORD' and token[1] == 'defun':
                name_token = next(token_iter)
                if name_token[0] != 'VARIABLE':
                    raise SyntaxError(f"Expected a function name after 'defun', got {name_token[1]}")
                open_paren_token = next(token_iter)
                if open_paren_token[1] != '(':
                    raise SyntaxError('Expected opening parentheses for parameters')
                stack.append(open_paren_token)
                param = next(token_iter)
                parameters = []
                while param[1] != ')':
                    if param == None : raise SyntaxError('Expected closing parentheses for parameters')
                    if param[0] != 'VARIABLE': SyntaxError('Not valid parameter')
                    parameters.append(param[1])
                    param = next(token_iter)
                stack.pop()
                exec(f"fun_{name_token[1]} = function(name_token[1], parameters)") 
                exec(f"functions[name_token[1]] = fun_{name_token[1]}")
#Function call
            elif token[0] == 'VARIABLE' and token[1] in functions:
                param = next(token_iter)
                parameters = []
                while param[1] != ')':
                    if param == None : raise SyntaxError('Expected closing parentheses for parameters')
                    if param[0] != 'VARIABLE': SyntaxError('Not valid parameter')
                    parameters.append(param[1])
                    param = next(token_iter)
                stack.pop()
                expected = len(functions[token[1]].parameters)
                recieved = len(parameters)
                if recieved != expected:
                    raise SyntaxError(f"Expected {expected} parameters, {recieved} recieved")
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

# Estructura de Token
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value


# Llamada a la función de análisis
is_syntax_correct = parse_comands(tokenize(code))
print("Syntax is correct:", is_syntax_correct)
