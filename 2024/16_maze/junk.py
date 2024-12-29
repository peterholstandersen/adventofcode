def matches_end_pos(pos, end_pos, scores, score):
    if end_pos != pos:
        return False
    for facing in [up, down, right, left]:
        state = (pos, facing)
        if state in scores and scores[state] == score:
            print("match end")
            return True
    return False


def insert_linear(work_element, work):
    # Could be optimizing using a binary search, but ...
    SCORE = 1
    for i in range(0, len(work)):
        if work[i][SCORE] >= work_element[SCORE]:
            work.insert(i, work_element)
            return
    work.append(work_element)


zzz = {up: "u", down: "d", left: "l", right: "r"}
def print_states(states):
    global zzz
    out = "[" + (", ".join([str(pos) + zzz[facing] for (pos, facing) in states])) + "]"
    return out

foobar = []
foo = set()
for (txt, facing) in zip(["up", "down", "left", "right", "None"], [up, down, left, right, None]):
    end_state = (end_pos, facing)
    if end_state in scores:
        if scores[end_state] == best:
            print(txt)
            # print(f"all_visited[end_pos,{txt}]:", len(all_visited[end_state]), all_visited[end_state])
            zzz = map(lambda x: x[0], all_visited[end_state])
            foo = foo.union(zzz)
            foobar.append(txt)
    else:
        print("None")

out = ""
for pos in range(0, len(maze)):
    if pos % dim == 0 and pos != 0:
        out += "\n"
    if pos in foo:
        out += "O"
    else:
        out += maze[pos]


(scores, all_visited) = shortest_path2(maze, start_state, end_pos)
best = None
for (txt, facing) in zip(["up", "down", "left", "right", "None"], [up, down, left, right, None]):
    end_state = (end_pos, facing)
    if end_state in scores:
        score = scores[end_state]
        print(txt, score)
        if best is None or score < best:
            best = score
    else:
        print("None")


def shortest_path2(maze, start_state, end_pos):
    # all_visited = dict() # map from position to sets
    result = dict()
    result[start_state] = (0, {start_state})
    work = [(start_state, 0, {start_state})]
    while len(work) > 0:
        (state, score, visited) = work[0]
        work = work[1:]
        (pos, facing) = state
        if pos == end_pos:
            facing = None
            state = (pos, facing)
        if state in scores:
            # we've already reached this one ... and scores[state] cannot be better than score ...
            # it can only be at least as good ... if worse, we disregard this .. remember: lower is better
            if scores[state] < score:
                continue
            if scores[state] != score:
                print("I didnt expect this")
                sys.exit(1)
            if state not in all_visited:
                print("can not happen?")
                sys.exit(1)
                all_visited[state] = set(visited)  # maybe ?
            else:
                # this happens:
                # all_visited[state] = all_visited[state].union(visited)
                # print(f"seen before {pos}{zzz[facing]}, old({len(visited)}): " + print_states(visited) + ", " +
                # (f"new({len(all_visited[state])}): " + print_states(all_visited[state]) if state in all_visited else "None") + f", merged({len(merged)}):", print_states(merged))
                pass
            continue
        scores[state] = score
        if state not in all_visited:
            all_visited[state] = set(visited)
        else:
            print("does this happen?")
            sys.exit(1)
            all_visited[state] += visited
        if pos == end_pos:
            continue
        new_pos = facing(pos)
        if maze[new_pos] != "#":
            new_state = (new_pos, facing)
            work.append((new_state, score + 1, visited + (new_state,)))
        for new_state in [(pos, clockwise[facing]), (pos, counterclockwise[facing])]:
            work.append((new_state, score + 1000, visited + (new_state,)))
        work.sort(key=lambda x: x[1])  # sort by score, I am lazy
    return (scores, all_visited)