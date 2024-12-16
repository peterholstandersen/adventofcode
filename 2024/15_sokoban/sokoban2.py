import sys

# file = "smaller2.in"
# file = "small.in"
file = "big.in"
(maze_as_str, moves) = open(file).read().strip("\n").split("\n\n")
maze_as_str = maze_as_str.replace("#", "##").replace(".", "..").replace("@", "@.").replace("O", "[]")
width = maze_as_str.index("\n")
# height = maze_as_str.count("\n") + 1
maze_as_str = maze_as_str.replace("\n", "")
moves = moves.replace("\n", "")
starting_pos = maze_as_str.find("@")
maze = { pos: maze_as_str[pos] for pos in range(0, len(maze_as_str)) }
maze[starting_pos] = "."
walls = { pos for pos in maze if maze[pos] == "#" }
boxes = { pos for pos in maze if maze[pos] == "[" }      # a box is represented by its leftmost position

def print_maze(walls, boxes, me):
    out = ""
    for pos in range(0, len(maze_as_str)):
        if pos != 0 and pos % width == 0:
            out += "\n"
        if pos in walls:
            out += "#"
        elif pos in boxes:
            out += "["
        elif pos - 1 in boxes:
            out += "]"
        elif pos == me:
            out += "@"
        else:
            out += "."
    print(out)

move = {"^": lambda pos: pos - width,
        "v": lambda pos: pos + width,
        ">": lambda pos: pos + 1,
        "<": lambda pos: pos - 1}

def get_box_at(boxes, pos):
    # width = 8
    # ........
    # ...[]...
    # ........
    # box at (1,4)=12 also covering (1,5)=13 represented as boxes = { 12 }
    # get boxes for pos=(1,4)=12 gives { 12 }
    # get boxes for pos=(1,5)=13 also gives { 12 }
    if pos in boxes:
        return pos
    if pos - 1 in boxes:
        return pos - 1
    return None

def get_boxes_to_move(walls, boxes, pos, move_it):
    workset = { pos }
    boxes_to_move = set()
    while len(workset) > 0:
        pos = workset.pop()
        if pos in walls:
            # we hit a wall, it is not possibly to move any boxes
            boxes_to_move = set()
            break
        blocking_box = get_box_at(boxes, pos)
        if blocking_box and blocking_box not in boxes_to_move:
            boxes_to_move.add(blocking_box)
            # check the destination for any boxes to move or if we hit a wall
            workset.add(move_it(blocking_box))
            workset.add(move_it(blocking_box) + 1)
    return boxes_to_move

def sanity_check_before_remove(walls, boxes, boxes_to_move, move_it):
    if any([move_it(box) in walls or move_it(box) + 1 in walls for box in boxes_to_move]):
        print("Error: attempt to move a box into a wall (this should not happen)")
        sys.exit(1)
    for box in boxes_to_move:
        if box not in boxes:
            print(f"Error: attempt to remove a box from {box} where there is no box: {boxes}")
            sys.exit(1)

def sanity_check_after_remove(walls, boxes, boxes_to_move, move_it):
    for box in boxes_to_move:
        if move_it(box) in boxes or move_it(box) - 1 in boxes:
            print(f"Error: attempt to move a box to [{move_it(box)},{move_it(box) + 1}] where there is a box already: {boxes}")
            sys.exit(1)

def move_boxes(walls, boxes, boxes_to_move, move_it):
    sanity_check_before_remove(walls, boxes, boxes_to_move, move_it)
    for box in boxes_to_move:
        boxes.remove(box)
    sanity_check_after_remove(walls, boxes, boxes_to_move, move_it)
    for box in boxes_to_move:
        boxes.add(move_it(box))

def do_part2(walls, boxes, moves, pos):
    for direction in moves:
        move_it = move[direction]
        new_pos = move_it(pos)
        boxes_to_move = get_boxes_to_move(walls, boxes, new_pos, move_it)
        move_boxes(walls, boxes, boxes_to_move, move_it)
        # Only move me (@) if the new_pos is free
        if new_pos not in walls and get_box_at(boxes, new_pos) is None:
            pos = new_pos
    return pos

ending_pos = do_part2(walls, boxes, moves, starting_pos)
part2 = sum([(box // width) * 100 + box % width for box in boxes])
print("part2:", part2) # big: 1554058, small: 9021
