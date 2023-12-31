import sys
from utils import Map

#    | is a vertical pipe connecting north and south.
#    - is a horizontal pipe connecting east and west.
#    L is a 90-degree bend connecting north and east.
#    J is a 90-degree bend connecting north and west.
#    7 is a 90-degree bend connecting south and west.
#    F is a 90-degree bend connecting south and east.
#    . is ground; there is no pipe in this tile.
#    S is the starting position of the animal; there is a pipe on this tile, but your sketch doesn't show what shape the pipe has.

#           ─ 	━ 	│ 	┃ 	┄ 	┅ 	┆ 	┇ 	┈ 	┉ 	┊ 	┋ 	┌ 	┍ 	┎ 	┏
# U+251x 	┐ 	┑ 	┒ 	┓ 	└ 	┕ 	┖ 	┗ 	┘ 	┙ 	┚ 	┛ 	├ 	┝ 	┞ 	┟
# U+252x 	┠ 	┡ 	┢ 	┣ 	┤ 	┥ 	┦ 	┧ 	┨ 	┩ 	┪ 	┫ 	┬ 	┭ 	┮ 	┯
# U+253x 	┰ 	┱ 	┲ 	┳ 	┴ 	┵ 	┶ 	┷ 	┸ 	┹ 	┺ 	┻ 	┼ 	┽ 	┾ 	┿
# U+254x 	╀ 	╁ 	╂ 	╃ 	╄ 	╅ 	╆ 	╇ 	╈ 	╉ 	╊ 	╋ 	╌ 	╍ 	╎ 	╏
# U+255x 	═ 	║ 	╒ 	╓ 	╔ 	╕ 	╖ 	╗ 	╘ 	╙ 	╚ 	╛ 	╜ 	╝ 	╞ 	╟
# U+256x 	╠ 	╡ 	╢ 	╣ 	╤ 	╥ 	╦ 	╧ 	╨ 	╩ 	╪ 	╫ 	╬ 	╭ 	╮ 	╯
# U+257x 	╰ 	╱ 	╲ 	╳ 	╴ 	╵ 	╶ 	╷ 	╸ 	╹ 	╺ 	╻ 	╼ 	╽ 	╾ 	╿

# ┌─┐
# │ │
# └─┘

N = lambda pos: (pos[0]-1, pos[1])
S = lambda pos: (pos[0]+1, pos[1])
W = lambda pos: (pos[0], pos[1]-1)
E = lambda pos: (pos[0], pos[1]+1)

reverse = { S: N, N: S, E: W, W: E }
f2l = {N: "N", S: "S", E: "E", W: "W", }
pipes = {"|": (N, S), "-": (W, E), "L": (N, E), "J": (N, W), "7": (S, W), "F": (S, E), ".": () }
char2line = str.maketrans("|-LJ7F", "│─└┘┐┌")
get_pipes = lambda pos: pipes[mapp[pos]] if mapp[pos] else ()

mapp = Map("big.in")
start_pos = mapp.find("S")[0]    # There can be only one
pos = [dirr for dirr in [N, S, E, W] if reverse[dirr] in get_pipes(dirr(start_pos))]
direction = pos[0]               # There can be only two: pick one

pos = direction(start_pos)
from_direction = reverse[direction]
legal = set()
while mapp[pos] != "S":
    legal.add(pos)
    (pipe1, pipe2) = get_pipes(pos)
    direction = pipe1 if pipe2 == from_direction else pipe2     # pick the other direction than the one we came from
    pos = direction(pos)
    from_direction = reverse[direction]
for (pos, _) in mapp.all():
    if pos not in legal:
        mapp[pos] = "."
print(str(mapp).translate(char2line))
print("part1", (len(legal) + 1) // 2) # 6890

worklist = [(row, col) for ((row, col), value) in mapp.all() if value == "." and (row == 1 or row == mapp.height or col == 1 or col == mapp.width)]
while len(worklist) > 0:
    pos = worklist.pop()
    mapp[pos] = "O"
    worklist = worklist + [pos1 for pos1 in mapp.get_neighbours(pos) if mapp[pos1] == "."]
print(str(mapp).translate(char2line))
print(len(mapp.get_some(lambda x: x == ".")))

# 721 too high according to the puzzle -- inside means something different in the puzzle
