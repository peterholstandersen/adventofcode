import sys

from map import read_file, error, ANSI, right, left, up, down

dice_not_used_for_now_remove_later_or_use_this_instead_of_corners_yes_I_think_so = {
    # A mapping of connecting sides, seen clockwise from above: top, right, bottom, left.
    # Opposing sides are not included in the lists as they are not connected. The lists are
    # rotated after the input file is read (the order is preserved), so that know how there
    # are rotated relative to each other.
    1: [3, 2, 4, 5],
    2: [1, 3, 6, 4],
    3: [1, 5, 6, 2],
    4: [2, 6, 5, 1],
    5: [4, 6, 3, 1],
    6: [4, 2, 3, 5],
}

corners = {
    # top-left, top-right, bottom-right, bottom-left clockwise. Will be rotated later. Order must be preserved.
    # The number itself must be in the list, the opposing side (7 - number) may not be in the list. The self
    # is redundant -- but included for now so that we can compare a corners from different list -- hence,
    # the numbers in a corner definition must be ordered, e.g., (1,3,5)
    1: [ (1,3,5), (1,2,3), (1,2,4), (1,4,5) ],
    2: [ (1,2,3), (2,3,6), (2,4,6), (1,2,4) ],
    3: [ (1,2,3), (1,3,5), (3,5,6), (2,3,6) ],
    4: [ (1,2,4), (2,4,6), (4,5,6), (1,4,5) ],
    5: [ (1,3,5), (1,4,5), (4,5,6), (3,5,6) ],
    6: [ (2,3,6), (3,5,6), (4,5,6), (2,4,6) ],
}

top_left = 0
top_right = 1
bottom_right = 2
bottom_left = 3

facing_char = {right: ">", left: "<", up: "^", down: "v"}

class Dice:
    def __init__(self, number, line, col):
        self.number = number
        self.line = line # anchor
        self.col = col
        self.corners = corners[number].copy()

    def _get_it(self, corner1, corner2):
        xs = [n for n in self.corners[corner1] if n in self.corners[corner2] and n != self.number]
        assert(len(xs) == 1)
        print(f"_get_it: #{self.number},{self.corners}:_get_it({corner1},{corner2})={xs[0]}")
        return xs[0]

    def get_up(self):     return self._get_it(top_left, top_right)
    def get_down(self):   return self._get_it(bottom_left, bottom_right)
    def get_right(self):  return self._get_it(top_right, bottom_right)
    def get_left(self):   return self._get_it(top_left, bottom_left)

    def rotate(self):
        self.corners = self.corners[1:] + self.corners[:1]

    def align(self, other):
        # if you don't succeed the first time, try again ... until you give up
        for _ in range(4):
            if ((self.corners[top_left] == other.corners[bottom_left] and self.corners[top_right] == other.corners[bottom_right]) or
                (self.corners[top_right] == other.corners[top_left] and self.corners[bottom_right] == other.corners[bottom_left]) or
                (self.corners[bottom_left] == other.corners[top_left] and self.corners[bottom_right] == other.corners[top_right]) or
                (self.corners[top_left] == other.corners[top_right] and self.corners[bottom_left] == other.corners[bottom_right])):
                return
            self.rotate()
        error(f"Unable to align {self.number} with {other.number}")
        print(self)
        print(other)

    def __str__(self):
        return f"Dice(#{self.number},({self.line},{self.col}),{self.corners})"

class Layout():
    def __init__(self, height, width, gridsize):
        self.layout = dict()
        self.height = height
        self.width = width
        self.gridsize = gridsize

    def add_die(self, dice):
        if dice.number in self.layout:
            error(f"layout: die {dice.number} is already defined")
        self.layout[dice.number] = dice

    def get_die(self, line, col):
        # get top-left corner of the block
        line = line - 1
        col = col - 1
        line = line - (line % self.gridsize) + 1
        col = col - (col % self.gridsize) + 1
        for die in self.layout.values():
            if die.line == line and die.col == col:
                return die.number
        error(f"layout: Unable to find die at ({line}, {col})")

    def check_integrity(self):
        # maybe
        ...

    def __str__(self):
        return f"Layout({','.join(map(str, self.layout.values()))}"

def print_layout(field, layout, height, width):
    print(layout)
    print("              1       ")
    print("    012345678901234567")
    for line in range(0, height + 2):
        print(f"{line:>2}: ", end="")
        for col in range(0, width + 2):
            if False and (line, col) in field:
                number = layout.get_die(line, col)
                print(number, end="")
            else:
                print(field.get((line, col), ANSI.green + "#" + ANSI.reset), end="")
        print("")


def determine_layout(field, height, width, gridsize):
    up = lambda line, col: (line - gridsize, col)
    down = lambda line, col: (line + gridsize, col)
    left = lambda line, col: (line, col - gridsize)
    right = lambda line, col: (line, col + gridsize)

    # The neighbours of a die, for extending the worklist below
    get_worklist_extension = lambda dice: [
        (up(line, col), dice.get_up(), dice), (down(line, col), dice.get_down(), dice),
        (right(line, col), dice.get_right(), dice), (left(line, col), dice.get_left(), dice)]

    sides = [(line, col) for line in range(1, height + 1, gridsize) for col in range(1, width + 1, gridsize) if (line, col) in field]

    # The layout with all dices, placed and aligned to each other
    layout = Layout(height, width, gridsize)

    # We name the first dice "1" ... it will decide the numbering of the rest according to the
    # "corners" definition as the rest of the dices will be aligned to this one
    (line, col) = sides.pop(0)
    dice1 = Dice(1, line, col)
    layout.add_die(dice1)

    worklist = get_worklist_extension(dice1)
    while len(worklist) > 0:
        print("WL:", worklist)
        ((line, col), number, align_with) = worklist.pop(0)
        if (line, col) not in sides:
            continue
        print(f"IT: #{number},({line},{col}),#{align_with.number}")
        if number in layout.layout:
            dice = layout.layout[number]
            if dice.line == line and dice.col == col and dice.number == number:
                continue
            error(f"layout error: worklist({number},{line},{col}) != layout({dice.number},{dice.line},{dice.col})\n{layout}")
        # If there is anything here, the new dice must align to the dice we came from
        print(layout)
        # assert(number not in layout.layout)
        new_dice = Dice(number, line, col)
        new_dice.align(align_with)
        layout.add_die(new_dice)
        print(layout)
        layout.check_integrity()
        worklist.extend(get_worklist_extension(new_dice))

    # print_layout(field, layout, height, width)
    return layout

def move_ahead(layout, field, line, col, facing):
    (new_line, new_col) = facing(line, col)
    if (new_line, new_col) in field:
        if field[(new_line, new_col)] == "#":
            return (line, col, facing)
        else:
            return (new_line, new_col, facing)
    # we are off the map: here be dragons
    from_die = layout.get_die(line, col)
    from_die_obj = layout.layout[from_die]
    print(f"we are off the map: from=#{from_die}({line},{col}) to ({new_line},{new_col})")
    if facing == up: to_die = from_die_obj.get_up()
    elif facing == right: to_die = from_die_obj.get_right()
    elif facing == down: to_die = from_die_obj.get_down()
    elif facing == left: to_die = from_die_obj.get_left()
    else: error("!?")
    assert(from_die != to_die)
    to_die_obj = layout.layout[to_die]

    if facing == up: out_side = "top"
    elif facing == right: out_side = "right"
    elif facing == down: out_side = "bottom"
    elif facing == left: out_side = "left"
    else: error("?")

    if to_die_obj.get_up() == from_die: in_side = "top"
    elif to_die_obj.get_right() == from_die: in_side = "right"
    elif to_die_obj.get_down() == from_die: in_side = "bottom"
    elif to_die_obj.get_left() == from_die: in_side = "left"
    else: error("!")

    gridsize = layout.gridsize

    # works on coordinates relative to the die anchor
    top_to_top    = lambda line, col: (0, gridsize - col, down)
    top_to_right  = lambda line, col: (gridsize - col, gridsize - 1, left)
    top_to_left   = lambda line, col: (col, 0, right)
    top_to_bottom = lambda line, col: (gridsize - 1, col, up)  # don't think this will happen

    bottom_to_top    = lambda line, col: (0, col, down)        # nor this one
    bottom_to_right  = lambda line, col: (col, gridsize - 1, left)
    bottom_to_bottom = lambda line, col: (gridsize - 1, layout.gridsize - 1 - col, up)
    bottom_to_left   = lambda line, col: (gridsize - 1, 0, right)

    left_to_top    = lambda line, col: (0, line, down)
    left_to_right  = lambda line, col: (line, gridsize - 1, left)
    left_to_bottom = lambda line, col: (gridsize - 1, gridsize -1 - col, up)
    left_to_left   = lambda line, col: (gridsize - 1 - line, 0, right)

    right_to_top    = lambda line, col: (0, gridsize - 1 - line, down)
    right_to_right  = lambda line, col: (gridsize - 1 - line, gridsize - 1, left)
    right_to_bottom = lambda line, col: (gridsize - 1, line, up)
    right_to_left   = lambda line, col: (line, 0, right)

    # line_from_die, col_from_die are relative to from_die's anchor (in range 0 to (gridsize-1) inclusive)
    line_from_die = line - from_die_obj.line
    col_from_die = col - from_die_obj.col

    # line_to_die, col_to_die are relative to to_die's anchor
    print(f"leaving #{from_die}({line_from_die},{col_from_die},out_side={out_side},facing={facing}), entering {to_die}(in_side={in_side})")
    (line_to_die, col_to_die, new_facing) = eval(out_side + "_to_" + in_side)(line_from_die, col_from_die)
    print(f"now in #{to_die}({line_to_die},{col_to_die},facing={new_facing}) ... map({line_to_die + to_die_obj.line},{col_to_die + to_die_obj.col})")
    new_line = line_to_die + to_die_obj.line
    new_col = col_to_die + to_die_obj.col
    if field[(new_line,new_col)] == "#":
        return (line, col, facing)
    else:
        return (line_to_die + to_die_obj.line, col_to_die + to_die_obj.col, new_facing)

def move_it(layout, field, commands):
    facing = right
    line = 1
    col = 1
    while (line, col) not in field:
        col = col + 1
    field[(line, col)] = facing_char[facing]
    for command in commands:
        match command:
            case 'M': (line, col, facing) = move_ahead(layout, field, line, col, facing)
            case 'R': facing = { up: right, right: down, down: left, left: up}[facing]
            case 'L': facing = { up: left, left: down, down: right, right: up}[facing]
            case _: error("bleh")
        field[(line, col)] = facing_char[facing]
    print("done")
    return (field, line, col, facing)

def main():
    filename = "big.in"
    (field_txt, field, commands, height, width) = read_file(filename)
    layout = determine_layout(field, height, width, 4 if filename == "small.in" else 50)
    (_, line, col, facing) = move_it(layout, field, commands)

    print_layout(field, layout, height, width)

    #  Facing is 0 for right (>), 1 for down (v), 2 for left (<), and 3 for up (^).

    facing_number = {right: 0, down: 1, left: 2, up: 3}
    result = 1000 * line + 4 * col + facing_number[facing]

    print(line, col, facing_char[facing], result)


# big.in: 197 11 ^ 197047

if __name__ == "__main__":
    main()