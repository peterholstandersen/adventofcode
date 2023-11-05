from functools import cache
from typing import Self
from map import read_file, error, ANSI, right, left, up, down

# Puzzle: https://adventofcode.com/2022/day/22, part 2
#
# Algorithm:
#
# The cube is modelled after real dice, where the opposing sides are 1-6, 3-4, 2-5. The corners on the side
# are defined as the three sides it connects.
#
# First, make a sparse representation of the input map: field[(line,col)] = char. I use the words "map" and "field"
# interchangably in the comments. Next, identify the blocks on the map. Each block corresponds to a side on the die.
# The gridsize of the blocks are given: 4x4 for small.in and 50x50 for big.in.
#
# We define the first block as being side 1 of the die with the default orientation: 3 is above, 2 is to the right,
# 4 is below, and 5 is to the left. Note, that we do not know yet whether there is anything on the map in either
# direction, but if anything is there, they must be these sides for the cube to be correct. This is indicated by
# the parenthesis:
#    (3)
# (5)-1-(2)
#    (4)
#
# Then, we look for neighbouring blocks on the map. Say, we only find a block below, it must be a 4 in order for
# it to match the orientation of 1. We rotate 4 so that 1 is above it. After 4 has been rotated, 5 must be left
# of 4, 2 must be to the right, and 6 below according to the definition of the corners. In this example, we did
# not find any other blocks next to 1, so we can forget about the (3), (2) and (5) from above. The layout so far,
# where (2), (5), (6) indicate potential neighbours to 4.
#     1
# (5)-4-(2)
#    (6)
#
# We continue until we have found all 6 blocks on the map and rotated them so that they all align. This is our
# final layout. For example for "small.in":
#    1
#  354
#    62
#
# Sine we know the orientation of all sides and know which side is connected to which, we know that when we go
# upwards from 1 we shall enter 3. If we leave 5 from the top side, we shall enter 1 from the left side. This
# way we can find the new position on the map when we leave it somewhere and also the new direction to continue
# in.

(TOP_LEFT, TOP_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT) = (0, 1, 2, 3)    # indices into the list below
corners = {
    # The 4 corners for each side on the die. The order of the corners in the list defines the orientation of the
    # side: they are listed clockwise starting from the top-left: top-left, top-right, bottom-right, bottom-left.
    # On purpose, the number itself is included in the defition of a corner. This will make it easier to compare two
    # corners from different lists since the numbers are sorted.
    1: [ (1,3,5), (1,2,3), (1,2,4), (1,4,5) ],
    2: [ (1,2,3), (2,3,6), (2,4,6), (1,2,4) ],
    3: [ (1,2,3), (1,3,5), (3,5,6), (2,3,6) ],
    4: [ (1,2,4), (2,4,6), (4,5,6), (1,4,5) ],
    5: [ (1,3,5), (1,4,5), (4,5,6), (3,5,6) ],
    6: [ (2,3,6), (3,5,6), (4,5,6), (2,4,6) ],
}

class Side:
    def __init__(self, number, line, col):
        self.number = number
        self.line = line # anchor into the map
        self.col = col
        self.corners = corners[number].copy()

    @cache
    def _get_common(self, corner1, corner2):
        # Find the common side number between corner1 and corner2 (excluding self)
        xs = set(self.corners[corner1]).intersection(self.corners[corner2]) - {self.number}
        assert(len(xs) == 1)
        return xs.pop()

    def get_up(self):     return self._get_common(TOP_LEFT, TOP_RIGHT)
    def get_down(self):   return self._get_common(BOTTOM_LEFT, BOTTOM_RIGHT)
    def get_right(self):  return self._get_common(TOP_RIGHT, BOTTOM_RIGHT)
    def get_left(self):   return self._get_common(TOP_LEFT, BOTTOM_LEFT)

    def get_to_side(self, layout, direction):
        # Get the side we are moving into
        if direction == up: to_side = self.get_up()
        elif direction == down: to_side = self.get_down()
        elif direction == right: to_side = self.get_right()
        elif direction == left: to_side = self.get_left()
        else: error("Unable to get_to_side")
        return layout.layout[to_side]

    def align(self, other):
        # Rotate the side until it is aligned with the other side. When a pair of corners match, they are aligned.
        for _ in range(4):
            if ((self.corners[TOP_LEFT] == other.corners[BOTTOM_LEFT] and self.corners[TOP_RIGHT] == other.corners[BOTTOM_RIGHT]) or
                (self.corners[TOP_RIGHT] == other.corners[TOP_LEFT] and self.corners[BOTTOM_RIGHT] == other.corners[BOTTOM_LEFT]) or
                (self.corners[BOTTOM_LEFT] == other.corners[TOP_LEFT] and self.corners[BOTTOM_RIGHT] == other.corners[TOP_RIGHT]) or
                (self.corners[TOP_LEFT] == other.corners[TOP_RIGHT] and self.corners[BOTTOM_LEFT] == other.corners[BOTTOM_RIGHT])):
                return
            # rotate
            self.corners = self.corners[1:] + self.corners[:1]
        error(f"Unable to align #{self.number} with #{other.number}")

    def __str__(self):
        return f"Side(#{self.number},({self.line},{self.col}),{self.corners})"

class Layout():
    def __init__(self, height, width, gridsize):
        self.layout = dict()        # mapping from side number to Side object
        self.height = height        # of the entire map
        self.width = width
        self.gridsize = gridsize    # the size of the blocks are gridsize x gridsize

    def add_side(self, side: Side):
        if side.number in self.layout:
            error(f"layout: side {side.number} is already defined")
        self.layout[side.number] = side

    def get_side(self, line: int, col: int) -> Side:
        # line, col is the absolute position on the map starting at (1,1)
        # return the Side at line, col
        line = line - 1
        col = col - 1
        anchor_line = line - (line % self.gridsize) + 1
        anchor_col = col - (col % self.gridsize) + 1
        for side in self.layout.values():
            if side.line == anchor_line and side.col == anchor_col:
                return side
        error(f"layout: Unable to find side at ({line},{col})")

    def __str__(self):
        return f"Layout({','.join(map(str, self.layout.values()))}"

def print_layout(field, layout, height, width):
    for line in range(0, height + 2):
        print(f"{line:>2}: ", end="")
        for col in range(0, width + 2):
            if False and (line, col) in field:
                number = layout.get_side(line, col).number
                print(number, end="")
            else:
                print(field.get((line, col), ANSI.green + "#" + ANSI.reset), end="")
        print("")

def determine_layout(field, height, width, gridsize):
    # Go through the map (aka field) and determine the layout of all sides and their rotations
    layout = Layout(height, width, gridsize)

    up = lambda line, col: (line - gridsize, col)
    down = lambda line, col: (line + gridsize, col)
    left = lambda line, col: (line, col - gridsize)
    right = lambda line, col: (line, col + gridsize)

    # The neighbours of a side, for extending the worklist below
    get_worklist_extension = lambda side: [
        (up(line, col), side.get_up(), side), (down(line, col), side.get_down(), side),
        (right(line, col), side.get_right(), side), (left(line, col), side.get_left(), side)]  # TODO: could replace side.get_up() and side with something else, so that align gets easier

    # Find the anchors for all the non-empty blocks in the map
    blocks = [(line, col) for line in range(1, height + 1, gridsize) for col in range(1, width + 1, gridsize) if (line, col) in field]

    # We name the first side "1" ... it will decide the numbering of the rest according to the "corners" definition
    # as the rest of the side will be aligned to this one
    (line, col) = blocks.pop(0)
    side1 = Side(1, line, col)
    layout.add_side(side1)

    worklist = get_worklist_extension(side1)
    while len(worklist) > 0:
        ((line, col), number, align_with) = worklist.pop(0)
        if (line, col) not in blocks:
            continue
        if number in layout.layout:
            side = layout.layout[number]
            if side.line == line and side.col == col and side.number == number:
                continue
            error(f"layout error: worklist({number},{line},{col}) != layout({side.number},{side.line},{side.col})\n{layout}")
        # If there is anything here, the new side must align to the side we came from
        new_side = Side(number, line, col)
        new_side.align(align_with)
        layout.add_side(new_side)
        worklist.extend(get_worklist_extension(new_side))
    return layout

def move_ahead(layout, field, line, col, facing):
    (new_line, new_col) = facing(line, col)
    if (new_line, new_col) in field:
        if field[(new_line, new_col)] == "#":
            return (line, col, facing)
        else:
            return (new_line, new_col, facing)
    # we are off the map: here be dragons
    from_side = layout.get_side(line, col)
    to_side = from_side.get_to_side(layout, facing)

    if facing == up: out_edge = "top"
    elif facing == right: out_edge = "right"
    elif facing == down: out_edge = "bottom"
    elif facing == left: out_edge = "left"
    else: error("?")

    if to_side.get_up() == from_side.number: in_edge = "top"
    elif to_side.get_right() == from_side.number: in_edge = "right"
    elif to_side.get_down() == from_side.number: in_edge = "bottom"
    elif to_side.get_left() == from_side.number: in_edge = "left"
    else: error("!")

    last = layout.gridsize - 1      # last column / last line
    reverse = lambda x: last - x    # works for columns and line both

    # The functions below are for determining the new line, column, and facing when leaving one side of the die
    # and entering another, where the name of the function denotes the edge we leave from, followed by _to_ and
    # then the edge we are entering. For example, right_to_top means we are leaving the right edge of one side
    # and entering the top of another. The functions work on coordinate relative to the side's anchor.
    top_to_top    = lambda line, col: (0, reverse(col), down)
    right_to_top  = lambda line, col: (0, reverse(line), down)
    bottom_to_top = lambda line, col: (0, col, down)
    left_to_top   = lambda line, col: (0, line, down)

    top_to_bottom    = lambda line, col: (last, col, up)
    right_to_bottom  = lambda line, col: (last, line, up)
    bottom_to_bottom = lambda line, col: (last, reverse(col), up)
    left_to_bottom   = lambda line, col: (last, reverse(line), up)

    top_to_right    = lambda line, col: (reverse(col), last, left)
    right_to_right  = lambda line, col: (reverse(line), last, left)
    bottom_to_right = lambda line, col: (col, last, left)
    left_to_right   = lambda line, col: (line, last, left)

    top_to_left    = lambda line, col: (col, 0, right)
    right_to_left  = lambda line, col: (line, 0, right)
    bottom_to_left = lambda line, col: (reverse(col), 0, right)
    left_to_left   = lambda line, col: (reverse(line), 0, right)

    # line_from_side, col_from_side are relative to from_side's anchor (in range 0 to (gridsize-1) inclusive)
    line_from_side = line - from_side.line
    col_from_side = col - from_side.col
    (line_to_side, col_to_side, new_facing) = eval(out_edge + "_to_" + in_edge)(line_from_side, col_from_side)
    new_line = line_to_side + to_side.line
    new_col = col_to_side + to_side.col
    if field[(new_line,new_col)] == "#":
        return (line, col, facing)
    else:
        return (line_to_side + to_side.line, col_to_side + to_side.col, new_facing)

def move_it(layout, field, commands):
    facing_char = {right: ">", left: "<", up: "^", down: "v"}
    # we start in the top-left corner of the first block on the map, facing right
    facing = right
    line = 1
    col = 1
    while (line, col) not in field:
        col = col + 1
    field[(line, col)] = facing_char[facing]   # drop breadcrums for a "nice" printout later
    for command in commands:
        match command:
            case 'M': (line, col, facing) = move_ahead(layout, field, line, col, facing)
            case 'R': facing = { up: right, right: down, down: left, left: up}[facing]
            case 'L': facing = { up: left, left: down, down: right, right: up}[facing]
            case _: error("illegal command in input")
        field[(line, col)] = facing_char[facing]
    return (field, line, col, facing)

def main():
    filename = "big.in"
    (field_txt, field, commands, height, width) = read_file(filename)
    layout = determine_layout(field, height, width, 4 if filename == "small.in" else 50)  # gridsize is given by defintion
    (_, line, col, facing) = move_it(layout, field, commands)
    print_layout(field, layout, height, width)

    # When calculating the result, the value of facing is 0 for right (>), 1 for down (v), 2 for left (<), and 3 for up (^).
    facing_number = {right: 0, down: 1, left: 2, up: 3}
    result = 1000 * line + 4 * col + facing_number[facing]

    print(line, col, facing_number[facing], result)

    if (filename == "big.in" and result != 197047) or (filename == "small.in" and result != 5031):
        error("ERROR")
    else:
        print("CORRECT")

# big.in: 197 11 ^ 197047

if __name__ == "__main__":
    main()