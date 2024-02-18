import LyM as f
code = "(defvar name 10) (= name Dim) (move Dim) (skip 2) (move 10) (turn :right) (face :east) (put :chips n) (pick :balloons n) (move-dir n :front) (run-dirs (:left :left :right)) (move-face n :north) (null) (if (isZero? 10) (move 5) (null))"
print(f.tokenize(code))
"""token_iter = iter(f.tokenize(code))
token = next(token_iter)
try:
    while token:
        syntax = f.parse_commands(token_iter,token)
except StopIteration as e:
    raise SyntaxError(e)
if f.stack:
    raise SyntaxError("Unmatched opening parenthesis")
    # Hemos llegado al final de los tokens sin errores
    # # La sintaxis es correcta si no hay paréntesis sin cerrar"""