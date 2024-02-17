import LyM as f
code = "(defvar name 10) (= name Dim) (move Dim) (skip 2) (move 10) (turn :right) (face :east) (put :chips n) (pick :balloons n) (move-dir n :front) (run-dirs (:left :left :right)) (move-face n :north) (null) (if (isZero? 10) (move 5) (null))"
token_iter = iter(f.tokenize(code))
token = next(token_iter)
try:
    while token:
    # Continuar hasta que no haya más tokens   
        token = f.parse_commands(token_iter,token)
        token = f.parse_controlstructs(token_iter,token)  
except StopIteration:
    pass
if f.stack:
    raise SyntaxError("Unmatched opening parenthesis")
    # Hemos llegado al final de los tokens sin errores
    # # La sintaxis es correcta si no hay paréntesis sin cerrar