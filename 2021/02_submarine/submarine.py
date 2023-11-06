import os
import re

# forward 5
# down 5
# forward 8
# up 3
# down 8
# forward 2
#
# part1:
#   forward increased horizontal position
#   down increases depth
#   up descreses depth
#
# part2:
#   down X increases your aim by X units.
#   up X decreases your aim by X units.
#   forward X does two things:
#     It increases your horizontal position by X units.
#     It increases your depth by your aim multiplied by X.

def part1(filename, result):
    program = open(filename).read().strip("\n").\
        replace("forward", "horizontal = horizontal +").\
        replace("down", "depth = depth +").\
        replace("up", "depth = depth -")
    with open("/tmp/hej.py", "w") as file:
        file.write("horizontal = 0\n")
        file.write("depth = 0\n")
        file.write(program + "\n")
        file.write(f"print('part1 {filename}', horizontal, depth, horizontal * depth)\n")
        file.write(f"assert(horizontal * depth == {result})")
    os.system("python /tmp/hej.py")

def part2(filename, result):
    program = open(filename).read().strip("\n").\
        replace("down", "aim = aim +").\
        replace("up", "aim = aim -")
    program = re.sub(r"forward (\d+)", r"horizontal = horizontal + \1; depth = depth + aim * \1", program)
    with open("/tmp/hej.py", "w") as file:
        file.write("aim = 0\n")
        file.write("horizontal = 0\n")
        file.write("depth = 0\n")
        file.write(program + "\n")
        file.write(f"print('part2 {filename}', horizontal, depth, horizontal * depth)\n")
        file.write(f"assert(horizontal * depth == {result})")
    os.system("python /tmp/hej.py")

part1("small.in", 150)
part1("big.in", 1840243)
part2("small.in", 900)
part2("big.in", 1727785422)