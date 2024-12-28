import sys
from utils import Timer

# file = "small.in"
# file = "small2.in"
file = "big.in"
maze = open(file).read()

up = lambda pos: pos - dim
down = lambda pos: pos + dim
right = lambda pos: pos + 1
left = lambda pos: pos - 1

clockwise = { up: right, right: down, down: left, left: up }
counterclockwise = { up: left, left: down, down: right, right: up}

dim = maze.index("\n")
maze = maze.replace("\n", "")
start_state = (maze.find("S"), right)
end_pos = maze.find("E")

def shortest_path(maze, start_state, end_pos):
    end_state = None
    scores = dict()
    work = [(start_state, 0)]
    while len(work) > 0:
        # print(work)
        (state, score) = work[0]
        work = work[1:]
        (pos, facing) = state
        if state in scores:
            continue
        scores[state] = score
        if pos == end_pos:
            end_state = state
            break
        # 3 actions: move forward, turn clockwise, turn counterclockwise
        work += [((facing(pos), facing), score + 1)] if maze[facing(pos)] != "#" else []
        work += [((pos, clockwise[facing]), score + 1000), ((pos, counterclockwise[facing]), score + 1000)]
        work.sort(key=lambda x: x[1]) # I am lazy
    return scores[end_state]

x = shortest_path(maze, start_state, end_pos)
print(x)
print("score:", x) # 102488