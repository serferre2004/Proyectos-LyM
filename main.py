import codeparser as f
with open('prueba.txt', 'r') as file:
    # Read the entire contents of the file into a string variable
    file_contents = file.read()

# Now, file_contents contains the contents of the file as a string

try:
    tokens = f.tokenize(file_contents)
    syntax = f.parse_commands(tokens)
except Exception:
    syntax = False
if syntax:print("Correct Syntax")
else: print("Incorrect Syntax")
