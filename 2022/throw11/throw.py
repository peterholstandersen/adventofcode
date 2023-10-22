import os
from string import Template

# Example input:
#
# Monkey 0:
#   Starting items: 79, 98
#   Operation: new = old * 19
#   Test: divisible by 23
#     If true: throw to monkey 2
#     If false: throw to monkey 3
#
# Pass 1 generates initialization statements for the monkeys and inspect lists.
# It also collects divisors for later use to solve part 2 of the puzzle.
# Pass 2 generates the one_round function with one while loop for every monkey.
# Example generated code:
#
# monkeys = [
#    [79, 98],
#    ...
# ]
# inspect = [0] * 8
#
# def one_round():
#     while len(monkeys[0]) > 0:
#         old = monkeys[0].pop(0)
#         inspect[0] += 1
#         new = old * 19
#         new = new // 3                              # For part 2 generate "new = new % (divisors * divisors ...)"
#         test = (new % 23 == 0)
#         if test: monkeys[2].append(new)
#         if not test: monkeys[3].append(new)
#     ...
# for _ in range(0, 10000):
#     one_round()
# print(inspect)

def pass1(lines, outfile):
    emit = lambda txt: outfile.write(txt + "\n")
    emit("monkeys = [")
    divisors = []
    count = 0
    for line in lines:
        match line.strip().split(" "):
            case ["Starting", "items:", *rest]:           emit(f"    [" + " ".join(rest) + "],"); count += 1
            case ["Test:", "divisible", "by", *number]:   divisors.append(number[0])
    emit("]")
    emit(f"inspect = [0] * {count}")
    return divisors

loop = Template("""\
    while len(monkeys[$index]) > 0:
        old = monkeys[$index].pop(0)
        inspect[$index] += 1
        $operation
        $extra_operation
        test = (new % $divisor == 0)
        if test: monkeys[$monkey1].append(new)
        if not test: monkeys[$monkey2].append(new)""")

def pass2(lines, divisors, outfile, do_part2):
    emit = lambda txt: outfile.write(txt + "\n")
    if do_part2:
        keys1 = { "extra_operation": "new = new % (" + " * ".join(divisors) + ")" }
        rounds = 10000
    else:
        keys1 = { "extra_operation": "new = new // 3" }
        rounds = 20
    keys = keys1.copy()
    emit("def one_round():")
    for line in lines:
        match line.strip().split(" "):
            case ["Monkey", rest]:                      keys["index"] = rest.strip(":")
            case ["Operation:", *stmt]:                 keys["operation"] = " ".join(stmt)
            case ["Test:", "divisible", "by", number]:  keys["divisor"] = number
            case ["If", "true:", *rest]:                keys["monkey1"] = rest[-1]
            case ["If", "false:", *rest]:               keys["monkey2"] = rest[-1]; \
                                                        emit(loop.substitute(keys)); \
                                                        keys = keys1.copy()
    emit(f"for _ in range(0, {rounds}):")
    emit(f"    one_round()")
    emit(f"print(inspect)")

def doit(filename):
    with open(filename) as file:
        lines = file.read().strip().split("\n")
    with open("/tmp/hej.py", "w") as outfile:
        divisors = pass1(lines, outfile)
        pass2(lines, divisors, outfile, do_part2=True)
    os.system("python /tmp/hej.py")

#doit("small.in")
doit("big.in")

# answer for big.in, part 2
# [60020, 7592, 119998, 59985, 62507, 57608, 117503, 119999]
# 52166*52013
# 2713310158