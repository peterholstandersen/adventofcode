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
# dl = head_line - tail_line and dc = head_col - tail_col. The _ denotes "stay".
tail_move_rules = [
    [UL, UL, U, UR, UR],
    [UL, _,  _,  _, UR],
    [ L, _,  _,  _, R ],
    [DL, _,  _,  _, DR],
    [DL, DL, D, DR, DR],
]
# For easy lookup the rules are stored in a dictionary
moves = { (l,c): tail_move_rules[l+2][c+2] for l in range(-2,3) for c in range(-2,3) }

with open("big.in") as file:
    dcs = [ direction_count.split(" ") for direction_count in file.read().strip().split("\n") ]
    directions = "".join([direction * eval(count) for (direction, count) in dcs])

def part1():
    visited = set()
    head = (0, 0)
    tail = (0, 0)
    for d in directions:
        head = eval(f"{d}({head})")
        tail = moves.get((head[0] - tail[0], head[1] - tail[1]), lambda x: x)(tail)
        visited.add(tail)
    print(len(visited))

def part2(length):
    # body[0] is the head
    start = (0, 0)
    body = [ start ] * length
    visited = { start }
    for d in directions:
        # #print(body, d, end=" ")
        body[0] = eval(f"{d}({body[0]})")
        for i in range(1, length):
            prev = body[i - 1]
            this = body[i]
            body[i] = moves[(prev[0] - this[0], prev[1] - this[1])](this)
        visited.add(body[-1])
    print()
    print(len(visited))

pairs = lambda body: [(body[i - 1], body[i]) for i in range(1, len(body))]

def part2b(length):
    start = (0, 0)
    body = [ start ] * length
    visited = { start }
    for d in directions:
        # print(body, dir, end=" ")
        body[0] = eval(d)(body[0])
        for i in range(1, length):
            (line1, col1) = body[i - 1]
            (line2, col2) = body[i]
            body[i] = moves[(line1 - line2, col1 - col2)](body[i])
        visited.add(body[-1])
    print()
    print(len(visited))

move = lambda prev, this: prev

def moveit(prev, body):
    # body[0] has moved, now make the rest follow
    b1 = move(prev, body[1])
    return body[0] + moveit(b1 + body[2:])

#part2(2)
#part2b(2)    # is the same as part1()
# part2(10)
part2(10)
part2b(10)

# part1: 6209
# part2: 2460


