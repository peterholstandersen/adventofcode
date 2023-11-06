import re
import sys
from itertools import chain

def sign(a):
    return 0 if a == 0 else -1 if a < 0 else 1

def range_2d(x1, y1, x2, y2):
    (dx, dy) = (sign(x2 - x1), sign(y2 - y1))
    (x, y) = (x1, y1)
    while True:
        yield((x, y))
        if (x, y) == (x2, y2):
            return
        (x, y) = (x + dx, y + dy)

def part(filename, result, part):
    text = open(filename).read().strip()
    numbers = [ list(map(int, re.findall(r"(\d+)", line))) for line in text.split("\n") ]
    if part == 1:
        numbers = filter(lambda rr: rr[0] == rr[2] or rr[1] == rr[3], numbers)
    vents = dict()
    for (x, y) in chain.from_iterable([range_2d(x1, y1, x2, y2) for (x1, y1, x2, y2) in numbers]):
        vents[(x,y)] = vents.get((x,y), 0) + 1
    nof_overlapping_vents = len([xy for xy, count in vents.items() if count > 1])
    print(f"part{part} {filename}", nof_overlapping_vents)
    assert (nof_overlapping_vents == result)

def main():
    part("small.in", 5, 1)
    part("big.in", 8350, 1)
    part("small.in", 12, 2)
    part("big.in", 19374, 2)

if __name__ == "__main__":
    main()