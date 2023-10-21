import sys
from functools import cmp_to_key

def error(msg):
    print(msg)
    sys.exit(1)

# -1: a < b
#  0: a == b
#  1: a > b
def compare(a, b):
    match (a, b):
        case (int(x), int(y)):     return 0 if x == y else -1 if x < y else 1
        case (int(x), list(y)):    return compare([x], y)
        case (list(x), int(y)):    return compare(x, [y])
        case ([], []):             return 0
        case ([],  _):             return -1
        case ( _, []):             return 1
        case ([x, *xs], [y, *ys]): c = compare(x, y); return c if c != 0 else compare(xs, ys)
        case _: error("err")

def main():
    #filename = "small.in"
    filename = "big.in"
    with open(filename) as file:
        data = [(eval(a), eval(b)) for (a, b) in [pair.split("\n") for pair in file.read().split("\n\n")]]
        data2 = [ a for (a, b) in data ] + [ b for (a, b) in data ] + [ [[2]], [[6]] ]
    result = 0
    pair_index = 0
    for (a, b) in data:
        pair_index += 1
        if compare(a, b) == -1:
            result += pair_index
    print("part1", result)
    data2.sort(key=cmp_to_key(compare))
    i1 = data2.index([[2]]) + 1
    i2 = data2.index([[6]]) + 1
    print("part2", i1*i2)


if __name__ == "__main__":
    main()