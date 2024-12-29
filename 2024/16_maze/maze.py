import sys
import bisect

# file = "tiny.in"
# file = "tiny2.in"
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
start_pos = maze.find("S")
end_pos = maze.find("E")
start_facing = right
start_state = (start_pos, start_facing)

def shortest_path(maze, start_state, end_pos):
    end_state = None
    scores = dict()
    work = [(start_state, 0)]
    while len(work) > 0:
        (state, score) = work.pop(0)
        (pos, facing) = state
        if state in scores:
            continue
        scores[state] = score
        if pos == end_pos:
            end_state = state
            break
        # three possible actions: move forward, turn clockwise, turn counterclockwise
        new_pos = facing(pos)
        if maze[new_pos] != "#":
            new_work = ((new_pos, facing), score + 1)
            bisect.insort(work, new_work, key=lambda x: x[1])
        work += [((pos, clockwise[facing]), score + 1000), ((pos, counterclockwise[facing]), score + 1000)]
    return scores[end_state]

def shortest_path2(maze, start_state, end_pos):
    # In general, a state is a (pos, facing) pair.
    # start_state: (start pos, start facing)
    # end_pos:     the goal postion, end facing is irrevant
    # scores:      mapping from state to score (lower is better)
    # work:        work list of (state, score, come_from) tuples. come_from is the state we came from
    # come_froms:  mapping from state to the previous states (plural) that can lead to this state with the same score
    #              (facing is relevant)
    end_state = None
    scores = dict()
    work = [(start_state, 0, set())]
    come_froms = dict()
    while len(work) > 0:
        (state, score, come_from) = work.pop(0)
        if state in scores:
            # we have seen this state before. update come_froms in case we reached here with the same score
            # it is not possible to reach here with a lower score as the work list is ordered by score
            if scores[state] == score:
                come_froms[state].update(come_from)
            continue
        (pos, facing) = state
        scores[state] = score
        come_froms[state] = come_from
        if pos == end_pos:
            end_state = state
            break
        new_pos = facing(pos)
        # new states: move forward if possible, turn clockwise, turn counterclockwise. work list must be ordered by score
        if maze[new_pos] != "#":
            new_work = ((new_pos, facing), score + 1, { state })
            bisect.insort(work, new_work, key=lambda x: x[1])
        work += [((pos, clockwise[facing]), score + 1000, { state }), ((pos, counterclockwise[facing]), score + 1000, { state })]
    return end_state, scores, come_froms

# accumulate all visited positions by walking the routes (plural) backwards using come_froms
def get_visited(state, come_froms, visited):
    visited.add(state[0])
    for sss in come_froms[state]:
        get_visited(sss, come_froms, visited)

def print_maze(maze, visited):
    out = ""
    for pos in range(0, len(maze)):
        if pos % dim == 0 and pos != 0:
            out += "\n"
        out += "O" if pos in visited else maze[pos]
    print(out)

part1 = shortest_path(maze, start_state, end_pos)
print("part1:", part1) # 102488

(end_state, scores, come_froms) = shortest_path2(maze, start_state, end_pos)
visited = set()
get_visited(end_state, come_froms, visited)

part1 = scores[end_state]
part2 = len(visited)
# print_maze(maze, visited)
print("part1:", part1)
print("part2:", part2) # small: 45, small2: 64, big: 559
