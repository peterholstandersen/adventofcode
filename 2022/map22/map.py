import sys
import re

class ANSI:
    black = "\u001b[30m"
    red = "\u001b[31m"
    green = "\u001b[32m"
    yellow = "\u001b[33m"
    blue = "\u001b[34m"
    purple = "\u001b[35m"
    cyan = "\u001b[36m"
    white = "\u001b[37m"
    bold = "\u001b[1m"
    reset = "\u001b[0m"
    reverse = "\u001b[7m"
    home = "\u001b[H"
    goto = lambda line, col: f"\u001b[{line};{col}H"
    clear = "\u001b[2J"
    curser_off = "\u001b[?25l"
    cursor_on = "\u001b[?25h"

def error(msg):
    print(msg)
    sys.exit(1)

compose = lambda f, g: lambda x: f(g(x))

def read_file(filename):
    with open(filename) as file:
        (field_txt, commands) = file.read().split("\n\n")
    commands = commands.strip()
    commands = re.sub("([0-9]+)", lambda m: "M" * int(m.group(1)), commands)
    field_dict = dict()
    height = field_txt.count("\n") + 1
    width = -1
    for (line, line_txt) in zip(range(sys.maxsize), field_txt.split("\n")):
        line_txt = line_txt.strip("\n")
        for col in range(len(line_txt)):
            if line_txt[col] != ' ':
                field_dict[ (line + 1, col + 1) ] = line_txt[col]
            if col + 1 > width:
                width = col + 1

    return (field_txt, field_dict, commands, height, width)


up = lambda line, col: (line - 1, col)
down = lambda line, col: (line + 1, col)
right = lambda line, col: (line, col + 1)
left = lambda line, col: (line, col - 1)

def R(x):
    (field, line, col, facing) = x
    return (field, line, col, { up: right, right: down, down: left, left: up}[facing])

def L(x):
    (field, line, col, facing) = x
    return (field, line, col, {up: left, left: down, down: right, right: up}[facing])

def M(x):
    (field, line, col, facing) = x
    (new_line, new_col) = facing(line, col)
    if (new_line, new_col) not in field:
        (new_line, new_col) = (line, col)
        while (new_line, new_col) in field:
            (new_line, new_col) = { up: down, down: up, right: left, left: right}[facing](new_line, new_col)
        (new_line, new_col) = facing(new_line, new_col)
    if field[(new_line, new_col)] == "#":
        return (field, line, col, facing)
    else:
        # assert(field[(new_line, new_col)] == ".")
        field[(new_line, new_col)] = "*"
        return (field, new_line, new_col, facing)

def print_field(field_txt):
    print(ANSI.clear)
    print(field_txt)

def my_eval(x):
    if len(x) == 1:
        return eval(x[0])
    return compose(my_eval(x[1:]), eval(x[0]))

def part1():
    (field_txt, field, commands, height, width) = read_file("big.in")
    print(commands)
    sys.setrecursionlimit(len(commands) + 10)
    start_line = 1
    start_col = 1
    while (start_line, start_col) not in field:
        start_col = start_col + 1

    start = (field, start_line, start_col, right)
    (field, end_line, end_col, facing) = my_eval(commands)(start)

    print("              1       ")
    print("    012345678901234567")

    for line in range(0, height + 2):
        print(f"{line:>2}: ", end="")
        for col in range(0, width + 2):
            if (line, col) == (end_line, end_col):
                print("@", end="")
            else:
                print(field.get( (line, col), ANSI.green + "#" + ANSI.reset), end="")
        print("")

    print("line=", end_line)
    print("col=", end_col)
    print("facing=", facing)

    # Facing is 0 for right (>), 1 for down (v), 2 for left (<), and 3 for up (^).
    # The final password is the sum of 1000 times the row, 4 times the column, and the facing.
    facing_number = { right: 0, down: 1, left: 2, up: 3 }[facing]
    print("result:", 1000 * end_line + 4 * end_col + facing_number)


if __name__ == "__main__":
    part1()

# big, part1: 56372