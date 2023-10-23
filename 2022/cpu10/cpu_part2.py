import sys

# Add a dummy element to the beginning of the list so that the index matches the cycle
with open("big.in") as file:
    assembler = ["dummy"] + file.read().strip().split()

def pixel(position, x):
    out = "\n" if position == 0 else ""
    out += "#" if position in [x - 1, x, x + 1] else "."
    return out

# The horizontal position equals (cycle - 1) % 40
scan = ""
x = 1
cycle = 1
while cycle < len(assembler):
    if assembler[cycle] == "addx":
        arg = eval(assembler[cycle + 1])
        scan += pixel((cycle - 1) % 40, x)
        scan += pixel(cycle % 40, x)
        x = x + arg
        cycle = cycle + 2
    elif assembler[cycle] == "noop":
        scan += pixel((cycle - 1) % 40, x)
        cycle = cycle + 1
    else:
        print("ERROR")
        sys.exit(1)

print(scan)
