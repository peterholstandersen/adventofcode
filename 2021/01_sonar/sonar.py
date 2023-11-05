from itertools import tee

# Puzzle, part1: How many times is a number higher than the previous? 7 in the example below.
#
# 199
# 200  x
# 208  x
# 210  x
# 200
# 207  x
# 240  x
# 269  x
# 260
# 263  x
#
# Puzzle, part2: adding up the numbers in 3-wide sliding window, how many sums are now higher than previous sum?
# 5 in the example below
#
# 607
# 618  x
# 618
# 617
# 647  x
# 716  x
# 769  x
# 792  x

def pairs(iterable):
    """s -> (s0,s1), (s1,s2), (s2,s3), ..."""
    a, b = tee(iterable)
    _ = next(b)
    return zip(a, b)

def triplets(iterable):
    """s -> (s0,s1,s2), (s1,s2,s3), (s2,s3,s4), ..."""
    a, b, c = tee(iterable, 3)
    _ = next(b)
    _ = next(c)
    _ = next(c)
    return zip(a, b, c)

def part1(filename, result):
    xs = map(int, open(filename).read().strip("\n").split("\n"))
    increases = len([(x,y) for (x,y) in pairs(xs) if x < y])
    print("part1:", filename, increases)
    assert(increases == result)

def part1a(filename, result):
    xs = list(map(int, open(filename).read().strip("\n").split("\n")))
    increases = len([(x,y) for (x,y) in zip(xs, xs[1:]) if x < y])
    print("part1:", filename, increases)
    assert(increases == result)

def part2(filename, result):
    xs = map(int, open(filename).read().strip("\n").split("\n"))
    ys = [a + b + c for (a, b, c) in triplets(xs)]
    increases = len([(x, y) for (x, y) in pairs(ys) if x < y])
    print("part2:", filename, increases)
    assert(increases == result)

def part2b(filename, result):
    xs = list(map(int, open(filename).read().strip("\n").split("\n")))
    ys = [a + b + c for (a, b, c) in zip(xs, xs[1:], xs[2:])]
    increases = len([(x, y) for (x, y) in zip(ys, ys[1:]) if x < y])
    print("part2:", filename, increases)
    assert(increases == result)

part1a("small.in", 7)
part1a("big.in", 1121)
part2b("small.in", 5)
part2b("big.in", 1065)