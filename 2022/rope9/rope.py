import sys
from typing import Tuple

compose = lambda f, g: lambda x: f(g(x))

# Direction functions when applied on (line, col) will return (line1, col1) in the given direction
R = lambda lc: (lc[0], lc[1] + 1)
L = lambda lc: (lc[0], lc[1] - 1)
D = lambda lc: (lc[0] + 1, lc[1])
U = lambda lc: (lc[0] - 1, lc[1])
UR = compose(U, R)
UL = compose(U, L)
DR = compose(D, R)
DL = compose(D, L)
_ = lambda x: x  # stay put

def move_tail(head: Tuple[int, int], tail: Tuple[int, int]) -> Tuple[int, int]:
    direction = [
        [UL, UL, U, UR, UR],
        [UL, _,  _,  _, UR],
        [ L, _,  _,  _, R ],
        [DL, _,  _,  _, DR],
        [DL, DL, D, DR, DR],
    ][head[0] - tail[0] + 2][head[1] - tail[1] + 2]
    return direction(tail)

def read_file(filename):
    with open(filename) as file:
        dcs = [ direction_count.split(" ") for direction_count in file.read().strip().split("\n") ]
        directions = "".join([direction * eval(count) for (direction, count) in dcs])
    return directions

def part1(directions):
    visited = set()
    head = (0, 0)
    tail = (0, 0)
    for d in directions:
        head = eval(d)(head)
        tail = move_tail(head, tail)
        visited.add(tail)
    print(len(visited))

def part2(directions, length):
    # body[0] is the head
    start = (0, 0)
    body = [ start ] * length
    visited = { start }
    for direction in directions:
        body[0] = eval(direction)(body[0])
        for i in range(1, length):
            body[i] = move_tail(body[i - 1], body[i])
        visited.add(body[-1])
    print(len(visited))

# heads are already moved, tails need to be moved
def move_body(heads, tails):
    if tails == []:
        return heads
    return move_body(heads + [move_tail(heads[-1], tails[0])], tails[1:])

def part2b(directions, length):
    # body[0] is the head
    start = (0, 0)
    body = [ start ] * length
    visited = { start }
    for direction in directions:
        body = move_body([ eval(direction)(body[0]) ], body[1:])
        visited.add(body[-1])
    print(len(visited))

def main():
    directions = read_file("big.in")
    sys.setrecursionlimit(len(directions) + 10)
    part1(directions)
    part2(directions, 2)       # same as part1(directions)
    part2(directions, 10)
    part2b(directions, 10)

if __name__ == "__main__":
    main()

# Results
# part1: 6209
# part2: 2460