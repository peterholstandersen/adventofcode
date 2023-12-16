import re
from functools import reduce

body = r" x-\g<2>+\g<1> if x in range(\2,\2+\3) else"
numbers = r"(\d+) (\d+) (\d+)"

functions = []
inside = False
function = ""

for line in open("big.in").read().strip().split("\n"):
    if "seeds:" in line:
        seeds = "[" + line[line.index(" "):].strip().replace(" ", ",") + "]"
    elif "-" in line:
        inside = True
        function = ""
    elif re.match(numbers, line):
        function += re.sub(numbers, body, line)
    elif inside and line == "":
        function = "(lambda x:" + function + " x)"
        functions.append(function)
        function = ""
        inside = False

if inside:
    function = "(lambda x:" + function + " x)"
    functions.append(function)

expr = reduce(lambda x, y: y + "(" + x + ")", functions, "seed")
expr = f"min(map(lambda seed: {expr}, {seeds}))"

print("part1", eval(expr)) # 621354867
