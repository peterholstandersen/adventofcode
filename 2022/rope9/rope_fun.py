import sys
from typing import Set, Callable
from rope import Position, Body, MoveFunction
from rope import read_file, R, L, D, U, compose, move_tail

class Rope:
    def __init__(self, body: Body, visited: Set[Position]):
        self.body = body
        self.visited = visited

MoveRopeFunction = Callable[[Rope], Rope]

def make_body(position: Position, length: int):
    return Rope([position] * length, { position })

# rope have already been moved, tails need to be moved
def move_body(rope: Rope, tails: Body):
    if len(tails) == 0:
        rope.visited.add(rope.body[-1])
        return rope
    new_body = rope.body + [ move_tail(rope.body[-1], tails[0]) ]
    return move_body(Rope(new_body, rope.visited), tails[1:])

# From a move function make a move rope function that moves the entire rope
# First, it moves the head and leaves it to move_body to move the rest of the body.
def make_move_rope_function(direction: MoveFunction) -> MoveRopeFunction:
    return lambda rope: move_body(Rope( [direction(rope.body[0])], rope.visited ),
                                  rope.body[1:])

# We overwrite move functions, so that they move the entire rope and not only a single element
R = make_move_rope_function(R)
L = make_move_rope_function(L)
D = make_move_rope_function(D)
U = make_move_rope_function(U)

def my_eval(directions):
    if len(directions) == 1:
        return eval(directions[0])
    return compose(my_eval(directions[1:]), eval(directions[0]))

directions = read_file("big.in")
sys.setrecursionlimit(len(directions) * 2)
body = my_eval(directions)(make_body((0, 0), 10))
print(len(body.visited))