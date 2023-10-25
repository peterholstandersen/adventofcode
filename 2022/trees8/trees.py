# Naive implementation

from typing import Set, Tuple, Iterable

Position = Tuple[int, int]
Field = (str, int, int)

def read_file(filename: str) -> Field:
    with open(filename) as file:
        trees = file.read().strip("\n")
        width = trees.find("\n")
        height = trees.count("\n") + 1
        trees = trees.replace("\n", "")
        return (trees, height, width)

def mark_visible_horizontally(trees: str, field_width: int, line: int, visible: Set[Position], rng: Iterable[int]) -> None:
    tree_height = chr(ord("0") - 1)
    for col in rng:
        tree_height1 = trees[line * field_width + col]
        if tree_height1 > tree_height:
            tree_height = tree_height1
            visible.add( (line, col) )

def mark_visible_vertically(trees: str, width: int, col: int, visible: Set[Position], rng: Iterable[int]) -> None:
    tree_height = chr(ord("0") - 1)
    for line in rng:
        tree_height1 = trees[line * width + col]
        if tree_height1 > tree_height:
            tree_height = tree_height1
            visible.add( (line, col) )

# Part 1 of the puzzle: count number of visible trees from the edges
def count_visible(trees: str, height: int, width: int) -> int:
    visible = set()
    for line in range(0, height):
        mark_visible_horizontally(trees, height, line, visible, range(0, width))
        mark_visible_horizontally(trees, height, line, visible, range(width - 1, 0, -1))
    for col in range(0, width):
        mark_visible_vertically(trees, width, col, visible, range(0, height))
        mark_visible_vertically(trees, width, col, visible, range(height - 1, 0, -1))
    return len(visible)

# To measure the viewing distance from a given tree, look up, down, left, and right from that tree; stop if you reach
# an edge or at the first tree that is the same height or taller than the tree under consideration. (If a tree is right
# on the edge, at least one of its viewing distances will be zero.)
def measure_viewing_distance_from(trees: str, height: int, width: int, from_line: int, from_col: int, line1: int, col1: int) -> int:
    if from_line == 0 or from_line == height - 1 or from_col == 0 or from_col == width - 1:
        return 0
    starting_tree_height = trees[from_line * width + from_col]
    distance = 1
    line = from_line + line1
    col = from_col + col1
    while True:
        if col == 0 or col == width - 1 or line == 0 or line == height - 1:
            break
        if trees[line * width + col] >= starting_tree_height:
            break
        distance += 1
        line = line + line1
        col = col + col1
    return distance

def calculate_scenic_value(trees, height, width, line, col):
    value = 1
    value = value * measure_viewing_distance_from(trees, height, width, line, col, 1, 0)
    value = value * measure_viewing_distance_from(trees, height, width, line, col, -1, 0)
    value = value * measure_viewing_distance_from(trees, height, width, line, col, 0, 1)
    value = value * measure_viewing_distance_from(trees, height, width, line, col, 0, -1)
    return value

# Part 2 of the puzzle: find the most scenic position anywhere on the field.
# Looking from a given position, multiply the numbers of visible trees in the four directions (up, down, left, right)
def find_most_scenic_position(trees: str, height: int, width: int):
    scenic_value = -1
    position = None
    what = 0
    rng = ( (line, col) for line in range(1, height - 1) for col in range(1, width - 1) )
    for (line, col) in rng:
        scenic_value1 = calculate_scenic_value(trees, height, width, line, col)
        if scenic_value1 > scenic_value:
            (position, scenic_value) = ( (line, col), scenic_value1 )
            print(position, scenic_value1)
        what = what + 1
    return position, scenic_value

def main():
    (trees, height, width) = read_file("big.in")
    count = count_visible(trees, height, width)
    (position, scenic_value) = find_most_scenic_position(trees, height, width)
    print("part1", count)
    print("part2", position, scenic_value)
    # 1672
    # (57, 84) 327180

if __name__ == "__main__":
    main()