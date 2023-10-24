import sys

from rope import read_file, R, L, D, U, compose, move_tail

def make_body(position, length):
    return [position] * length + [ {position} ]

def move_body(heads, tails):
    if len(tails) == 1:
        tails[0].add(heads[-1])
        return heads + tails
    return move_body(heads + [move_tail(heads[-1], tails[0])], tails[1:])

make_move_function = lambda direction: lambda body: move_body([direction(body[0])], body[1:])

# We overwrite move functions, so that they move the entire rope and not only a single element
R = make_move_function(R)
L = make_move_function(L)
D = make_move_function(D)
U = make_move_function(U)

def my_eval(directions):
    if len(directions) == 1:
        return eval(directions[0])
    return compose(my_eval(directions[1:]), eval(directions[0]))

directions = read_file("big.in")
sys.setrecursionlimit(len(directions) * 2)
body = my_eval(directions)(make_body((0, 0), 10))
print(len(body[-1]))