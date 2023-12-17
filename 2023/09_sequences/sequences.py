filename = "big.in"
xss = [list(map(int, line.strip().split(" "))) for line in open(filename).read().strip().split("\n")]

def next_value(xs):
    if all(map(lambda x: x == 0, xs)):
        return 0
    return xs[-1] + next_value([x - y for (x,y) in zip(xs[1:], xs)])

print("part1", sum([next_value(xs) for xs in xss]))       # 1696140818
print("part2", sum([next_value(xs[::-1]) for xs in xss])) # 1152