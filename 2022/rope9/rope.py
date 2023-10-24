import sys

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
stay = lambda x: x
_ = stay

# Rules for moving the tail. Since we cannot index a list with negative numbers, the indices are offset by 2.
# tail_move_rules[dl+2, dc+2] specifies which direction the tail shall move in where
# dl = head_line - tail_line and dc = head_col - tail_col. The _ denotes "stay". So if head is 2 lower
# than tail and they are in the same column, then dl = 2 and dc = 0, tail needs to move
# tail_move_rules[2 + 2, 0 + 2] = D, which is down.
def move_tail(head, tail):
    direction = [
        [UL, UL, U, UR, UR],
        [UL, _,  _,  _, UR],
        [ L, _,  _,  _, R ],
        [DL, _,  _,  _, DR],
        [DL, DL, D, DR, DR],
    ][head[0] - tail[0] + 2][head[1] - tail[1] + 2]
    return direction(tail)

with open("big.in") as file:
    dcs = [ direction_count.split(" ") for direction_count in file.read().strip().split("\n") ]
    directions = "".join([direction * eval(count) for (direction, count) in dcs])

def part1():
    visited = set()
    head = (0, 0)
    tail = (0, 0)
    for d in directions:
        head = eval(d)(head)
        tail = move_tail(head, tail)
        visited.add(tail)
    print(len(visited))

def part2(length):
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

part1()
part2(2)
part2(10)

# part1: 6209
# part2: 2460