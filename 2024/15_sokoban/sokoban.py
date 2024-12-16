import sys

# file = "smaller.in"
# file = "small.in"
file = "big.in"
(maze_as_str, moves) = open(file).read().strip("\n").split("\n\n")
dim = maze_as_str.index("\n")
maze_as_str = maze_as_str.replace("\n", "")
moves = moves.replace("\n", "")
starting_pos = maze_as_str.find("@")
maze = { pos: maze_as_str[pos] for pos in range(0, len(maze_as_str)) }
maze[starting_pos] = "."

move = {"^": lambda pos: pos - dim,
        "v": lambda pos: pos + dim,
        ">": lambda pos: pos + 1,
        "<": lambda pos: pos - 1}

def print_maze(maze, dim, me):
    xxx = "".join([maze[pos] if pos != me else "@" for pos in range(0, dim * dim)])
    yyy = "\n".join([xxx[n:(n + dim)] for n in range(0, dim * dim, dim)])
    print(yyy)

def do_part1(maze, moves, pos):
    for direction in moves:
        move_it = move[direction]
        new_pos = move_it(pos)
        boxes_to_move = []
        while maze[new_pos] == "O":
            (from_pos, to_pos) = (new_pos, move_it(new_pos))
            if maze[to_pos] == "#":
                boxes_to_move = []
                break
            boxes_to_move.append((from_pos, to_pos))
            new_pos = move_it(new_pos)
        for (from_pos, to_pos) in boxes_to_move[-1::-1]:
            maze[to_pos] = 'O'
            maze[from_pos] = '.'
        new_pos = move_it(pos)
        if maze[new_pos] == ".":
            pos = new_pos
    return pos

ending_pos = do_part1(maze, moves, starting_pos)
part1 = sum([(pos // dim * 100) + (pos % dim) for pos in range(0, dim*dim) if maze[pos] == "O"])

print("part1:", part1) # 1552463
