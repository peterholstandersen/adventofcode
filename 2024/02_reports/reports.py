import sys
from collections import Counter

# one report per line:
# 7 6 4 2 1
# 1 2 7 8 9
# 9 7 6 2 1
# 1 3 2 4 5
# 8 6 4 4 1
# 1 3 6 7 9
#
# a report only counts as safe if both of the following are true:
# - The levels are either all increasing or all decreasing.
# - Any two adjacent levels differ by at least one and at most three.
#
# part1: How many reports are safe?

# file = "small.in"
file = "big.in"
reports = [list(map(int, line.strip().split(" "))) for line in open(file).read().strip().split("\n")]

is_safe_ascending = lambda xs: all([1 <= (x - y) <= 3 for (x, y) in zip(xs[1:], xs)])
is_safe = lambda xs: is_safe_ascending(xs) or is_safe_ascending(list(reversed(xs)))
part1 = list(map(is_safe, reports)).count(True)

# make all lists of xs with one element removed .. including xs itself
def combinations(xs):
    xss = [xs[:i] + xs[i+1:]  for i in range(0, len(xs))]
    xss.append(xs)
    return xss

part2 = [any([is_safe(report1) for report1 in combinations(report)]) for report in reports].count(True)

print("part1:", part1)
print("part2:", part2) # 544!