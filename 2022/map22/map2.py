from map import read_file, error, ANSI, right, left, up, down
from functools import cache

(TOP_LEFT, TOP_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT) = (0, 1, 2, 3)   # indices
corners = {
    # top-left, top-right, bottom-right, bottom-left clockwise. Will be rotated later. Order must be preserved.
    # Integrity check: The number itself nor the opppsing side (7 - number) may be in the list.
    # Having the number itself is redundant on purpose. This allows us to compare two corners from different lists
    # provided the numbers in a corner definition are sorted.
    1: [ (1,3,5), (1,2,3), (1,2,4), (1,4,5) ],
    2: [ (1,2,3), (2,3,6), (2,4,6), (1,2,4) ],
    3: [ (1,2,3), (1,3,5), (3,5,6), (2,3,6) ],
    4: [ (1,2,4), (2,4,6), (4,5,6), (1,4,5) ],
    5: [ (1,3,5), (1,4,5), (4,5,6), (3,5,6) ],
    6: [ (2,3,6), (3,5,6), (4,5,6), (2,4,6) ],
}

class Dice:
    def __init__(self, number, line, col):
        self.number = number
        self.line = line # anchor
        self.col = col
        self.corners = corners[number].copy()

    @cache
    def _get_it(self, corner1, corner2):
        # Find the common dice number between corner1 and corner2 (excluding self)
        xs = set(self.corners[corner1]).intersection(self.corners[corner2]) - {self.number}
        assert(len(xs) == 1)
        return xs.pop()

    def get_up(self):     return self._get_it(TOP_LEFT, TOP_RIGHT)
    def get_down(self):   return self._get_it(BOTTOM_LEFT, BOTTOM_RIGHT)
    def get_right(self):  return self._get_it(TOP_RIGHT, BOTTOM_RIGHT)
    def get_left(self):   return self._get_it(TOP_LEFT, BOTTOM_LEFT)

    def align(self, other):
        # Rotate the dice until it is aligned with the other dice. When a pair of corners match, they are aligned.
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
        return f"Dice(#{self.number},({self.line},{self.col}),{self.corners})"

class Layout():
    def __init__(self, height, width, gridsize):
        self.layout = dict()
        self.height = height
        self.width = width
        self.gridsize = gridsize

    def add_dice(self, dice):
        if dice.number in self.layout:
            error(f"layout: dice {dice.number} is already defined")
        self.layout[dice.number] = dice

    def get_dice(self, line, col):
        # get top-left corner of the block
        # line, col is the absolute position on the map starting at (1,1)
        line = line - 1
        col = col - 1
        anchor_line = line - (line % self.gridsize) + 1
        anchor_col = col - (col % self.gridsize) + 1
        for dice in self.layout.values():
            if dice.line == anchor_line and dice.col == anchor_col:
                return dice.number
        error(f"layout: Unable to find dice at ({line},{col})")

    def __str__(self):
        return f"Layout({','.join(map(str, self.layout.values()))}"

def print_layout(field, layout, height, width):
    for line in range(0, height + 2):
        print(f"{line:>2}: ", end="")
        for col in range(0, width + 2):
            if False and (line, col) in field:
                number = layout.get_dice(line, col)
                print(number, end="")
            else:
                print(field.get((line, col), ANSI.green + "#" + ANSI.reset), end="")
        print("")

def determine_layout(field, height, width, gridsize):
    # Go through the map (aka field) and determine the layout of all dice and their rotation
    layout = Layout(height, width, gridsize)

    up = lambda line, col: (line - gridsize, col)
    down = lambda line, col: (line + gridsize, col)
    left = lambda line, col: (line, col - gridsize)
    right = lambda line, col: (line, col + gridsize)

    # The neighbours of a die, for extending the worklist below
    get_worklist_extension = lambda dice: [
        (up(line, col), dice.get_up(), dice), (down(line, col), dice.get_down(), dice),
        (right(line, col), dice.get_right(), dice), (left(line, col), dice.get_left(), dice)]

    # Find the anchors for all the non-empty blocks in the map
    blocks = [(line, col) for line in range(1, height + 1, gridsize) for col in range(1, width + 1, gridsize) if (line, col) in field]

    # Get the dice rolling ... we name the first dice "1" ... it will decide the numbering of the
    # rest according to the "corners" definition as the rest of the dice will be aligned to this one
    (line, col) = blocks.pop(0)
    dice1 = Dice(1, line, col)
    layout.add_dice(dice1)

    worklist = get_worklist_extension(dice1)
    while len(worklist) > 0:
        ((line, col), number, align_with) = worklist.pop(0)
        if (line, col) not in blocks:
            continue
        if number in layout.layout:
            dice = layout.layout[number]
            if dice.line == line and dice.col == col and dice.number == number:
                continue
            error(f"layout error: worklist({number},{line},{col}) != layout({dice.number},{dice.line},{dice.col})\n{layout}")
        # If there is anything here, the new dice must align to the dice we came from
        new_dice = Dice(number, line, col)
        new_dice.align(align_with)
        layout.add_dice(new_dice)
        worklist.extend(get_worklist_extension(new_dice))
    return layout

def move_ahead(layout, field, line, col, facing):
    (new_line, new_col) = facing(line, col)
    if (new_line, new_col) in field:
        if field[(new_line, new_col)] == "#":
            return (line, col, facing)
        else:
            return (new_line, new_col, facing)
    # we are off the map: here be dragons
    from_dice = layout.get_dice(line, col)
    from_dice_obj = layout.layout[from_dice]
    if facing == up: to_dice = from_dice_obj.get_up()
    elif facing == right: to_dice = from_dice_obj.get_right()
    elif facing == down: to_dice = from_dice_obj.get_down()
    elif facing == left: to_dice = from_dice_obj.get_left()
    else: error("!?")
    assert(from_dice != to_dice)
    to_dice_obj = layout.layout[to_dice]

    if facing == up: out_side = "top"
    elif facing == right: out_side = "right"
    elif facing == down: out_side = "bottom"
    elif facing == left: out_side = "left"
    else: error("?")

    if to_dice_obj.get_up() == from_dice: in_side = "top"
    elif to_dice_obj.get_right() == from_dice: in_side = "right"
    elif to_dice_obj.get_down() == from_dice: in_side = "bottom"
    elif to_dice_obj.get_left() == from_dice: in_side = "left"
    else: error("!")

    last = layout.gridsize - 1      # last column / last line
    reverse = lambda x: last - x    # works for columns and line both

    # works on coordinates relative to the dice anchor
    top_to_top    = lambda line, col: (0, reverse(col), down)
    top_to_right  = lambda line, col: (reverse(col), last, left)
    top_to_left   = lambda line, col: (col, 0, right)
    top_to_bottom = lambda line, col: (last, col, up)

    bottom_to_top    = lambda line, col: (0, col, down)
    bottom_to_right  = lambda line, col: (col, last, left)
    bottom_to_bottom = lambda line, col: (last, reverse(col), up)
    bottom_to_left   = lambda line, col: (last, 0, right)

    left_to_top    = lambda line, col: (0, line, down)
    left_to_right  = lambda line, col: (line, last, left)
    left_to_bottom = lambda line, col: (last, reverse(col), up)
    left_to_left   = lambda line, col: (reverse(line), 0, right)

    right_to_top    = lambda line, col: (0, reverse(line), down)
    right_to_right  = lambda line, col: (reverse(line), last, left)
    right_to_bottom = lambda line, col: (last, line, up)
    right_to_left   = lambda line, col: (line, 0, right)

    # line_from_dice, col_from_dice are relative to from_dice's anchor (in range 0 to (gridsize-1) inclusive)
    line_from_dice = line - from_dice_obj.line
    col_from_dice = col - from_dice_obj.col

    # line_to_dice, col_to_dice are relative to to_dice's anchor
    # print(f"leaving #{from_dice}({line_from_dice},{col_from_dice},out_side={out_side},facing={facing}), entering {to_dice}(in_side={in_side})")
    (line_to_dice, col_to_dice, new_facing) = eval(out_side + "_to_" + in_side)(line_from_dice, col_from_dice)
    # print(f"now in #{to_dice}({line_to_dice},{col_to_dice},facing={new_facing}) ... map({line_to_dice + to_dice_obj.line},{col_to_dice + to_dice_obj.col})")
    new_line = line_to_dice + to_dice_obj.line
    new_col = col_to_dice + to_dice_obj.col
    if field[(new_line,new_col)] == "#":
        return (line, col, facing)
    else:
        return (line_to_dice + to_dice_obj.line, col_to_dice + to_dice_obj.col, new_facing)

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