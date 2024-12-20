import sys
import re
from functools import cache

# file = "small.in"
file = "big.in"
[towels, designs] = open(file).read().strip().split("\n\n")
towels = towels.split(", ")
designs = designs.split("\n")

@cache
def calc_combinations(design, towels):
    if len(design) == 0:
        return 1
    return sum([calc_combinations(design[len(towel):], towels) for towel in towels if design.startswith(towel)])

def do_part2(designs, towels):
    combos = 0
    for design in designs:
        combos += calc_combinations(design, tuple(towels))
    print("part2:", combos) # 715514563508258

p = lambda x: x if len(x) == 1 else "(" + x + ")"

def get_fewer(towels):
    fewer = []
    towels = sorted(towels, key=len)
    for t in towels:
        if len(t) == 1:
            fewer.append(t)
            continue
        regexp = "(" + ("|".join([p(towel) for towel in fewer])) + ")+"
        if re.fullmatch(regexp, t):
            continue
        fewer.append(t)
    return fewer

def do_part1():
    count = 0
    towels.sort()
    for design in designs:
        fewer = [ towel for towel in towels if towel in design]
        even_fewer = get_fewer(fewer)
        regexp = "(" + ("|".join([p(towel) for towel in even_fewer])) + ")+"
        if re.fullmatch(regexp, design):
            count += 1
    print("part1:", count) # 322

do_part2(designs, towels)
do_part1()