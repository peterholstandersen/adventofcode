import sys
from typing import Tuple

def add(x: Tuple[int,int], y: Tuple[int,int]):
    return (x[0] + y[0], x[1] + y[1])

def error(text):
    print(text)
    sys.exit(1)

class Rock:
    def __init__(self, blocks):
        lines = [line for (line, _) in blocks]
        columns = [column for (_, column) in blocks]
        if min(lines) != 0 or min(columns) != 0:
            error(f"Rock definition must start in (0,0): {blocks}")
        self.blocks = blocks
        self.height = max(lines) + 1
        self.width = max(columns) + 1

class Chamber:
    def __init__(self):
        # Constants (unless the space-continuum ruptures)
        self.down = (1, 0)
        self.left = (0, -1)
        self.right = (0, 1)
        self.start_free_lines = 3
        self.chamber_width = 7
        self.start_column = 2
        # Not constant
        self.fixed_blocks = set()
        self.top_line = 0          # The top-most line of the fixed blocks
        self.rock = None           # The rock we are handling at the moment
        self.rock_position = None

    def start_new_rock(self, rock):
        # Each rock appears so that its left edge is two units away from the left wall and its bottom
        # edge is three units above the highest rock in the room (or the floor, if there isn't one).
        # A rock specification always start in (0,0)
        #
        # Example: starting a square rock (height 2) in 7 wide chamber. The top_line is -1.
        # The rock must start in line top_line - rock-height - free-lines = -1 - 2 - 3 = -6.
        # A rock always starts in column 2.
        #
        # -6 |..@@...|
        # -5 |..@@...|
        # -4 |.......|
        # -3 |.......|
        # -2 |.......|
        # -1 |.####..|
        #  0 +-------+
        #
        # We assume that the chamber is wide enough for the rock
        if self.rock:
            error("Attempt to start a new rock without fixing the former")
        self.rock = rock
        self.rock_position = (self.top_line - rock.height - self.start_free_lines, self.start_column)

    # Attempt to move a rock, return False if we are not able to move it
    def move_rock(self, direction: Tuple[int,int]) -> bool:
        # Check if there is room for all blocks in the rock
        new_rock_position = add(self.rock_position, direction)
        for block in self.rock.blocks:
            new_block_position = add(new_rock_position, block)
            if new_block_position[1] < 0 or new_block_position[1] >= self.chamber_width:
                return False
            if new_block_position[0] >= 0 or new_block_position in self.fixed_blocks:
                return False
        self.rock_position = new_rock_position
        return True

    def apply_jet(self, direction):
        self.move_rock(self.left if direction == "<" else self.right)

    def drop_rock(self):
        return self.move_rock(self.down)

    def fix_rock(self):
        for block in self.rock.blocks:
            position = add(self.rock_position, block)
            self.fixed_blocks.add(position)
            if position[0] < self.top_line:
                self.top_line = position[0]
        self.rock = None
        self.rock_position = None

    def __str__(self):
        out = ""
        out = out + f"top_line = {self.top_line}\n"
        rock_blocks = { add(self.rock_position, rock_block) for rock_block in self.rock.blocks } if self.rock else set()
        rock_height = self.rock.height if self.rock else 0
        for line in range(self.top_line - rock_height, 0):
            out = out + "|"
            for column in range(0, self.chamber_width):
                if (line, column) in rock_blocks:
                    out = out + "@"
                elif (line, column) in self.fixed_blocks:
                    out = out + "#"
                else:
                    out = out + "."
            out = out + "|\n"
        out = out + "+" + ("-" * self.chamber_width) + "+"
        return out

def get_rocks_specification():
    #    ####
    rock1 = Rock( ((0,0), (0,1), (0,2), (0,3)) )

    #     #
    #    ###
    #     #
    rock2 = Rock( ((0,1), (1,0), (1,1), (1,2), (2,1)) )

    #      #
    #      #
    #    ###
    rock3 = Rock( ((0,2), (1,2), (2,0), (2,1), (2,2)) )

    #    #
    #    #
    #    #
    #    #
    rock4 = Rock( ((0,0), (1,0), (2,0), (3,0)) )

    #    ##
    #    ##
    rock5 = Rock( ((0,0), (0,1), (1,0), (1,1)) )

    return (rock1, rock2, rock3, rock4, rock5)

def check_cycle(turn, chamber, rock_index, jet_index, seen_states):
    height = - chamber.top_line
    state = (rock_index, jet_index)
    if state not in seen_states:
        seen_states[state] = [(turn, height)]
        return None
    seen_states[state].append((turn, height))
    turn_and_heights = seen_states[state]
    if len(turn_and_heights) > 2:
        # We have seen this state at least 3 times now, if the height increases are the same, then we have a cycle
        (t1, h1) = turn_and_heights[-1]   # this turn
        (t2, h2) = turn_and_heights[-2]   # previous time we encountered this state
        (t3, h3) = turn_and_heights[-3]   # and the time before that
        if (h1 - h2) == (h2 - h3):
            cycle_starts_in_turn = t3
            cycle_length = t1 - t2
            height_increase = h1 - h2
            print(f"Detected cycle in turn {turn}. Cycle starts in turn {cycle_starts_in_turn}, cycle length {cycle_length}, height increase {height_increase}.\n")
            return (cycle_starts_in_turn, cycle_length, height_increase)
    return None

def main():
    #filename = "small.in"; number_of_rocks = 2022; expected_height = 3068
    #filename = "small.in"; number_of_rocks = 1000000000000; expected_height = 1514285714288
    #filename = "big.in"; number_of_rocks = 2022; expected_height = 3065
    filename = "big.in"; number_of_rocks = 1000000000000; expected_height = 1562536022966

    with open(filename) as file:
        jet = file.read()
    rocks = get_rocks_specification()

    do_check_cycle = True
    seen_states = dict()
    extra_height = 0

    chamber = Chamber()
    jet_index = 0
    rock_index = 0

    current_turn = 0
    while current_turn < number_of_rocks:
        current_turn = current_turn + 1
        if do_check_cycle:
            cycle = check_cycle(current_turn, chamber, rock_index, jet_index, seen_states)
            if cycle:
                (starts_in, cycle_length, height_increase) = cycle
                skip_ahead_to = number_of_rocks - ((number_of_rocks - starts_in) % cycle_length)
                turns_to_skip = skip_ahead_to - current_turn
                if turns_to_skip % cycle_length != 0:
                    error("miscalculation of turns_to_skip")
                extra_height = (turns_to_skip // cycle_length) * height_increase
                do_check_cycle = False
                print(f"Skipping ahead from {current_turn} to {skip_ahead_to}")
                current_turn = skip_ahead_to

        chamber.start_new_rock(rocks[rock_index])
        rock_index = (rock_index + 1) % len(rocks)
        rock_moved_downwards = True
        while rock_moved_downwards:
            chamber.apply_jet(jet[jet_index])
            jet_index = (jet_index + 1) % len(jet)
            rock_moved_downwards = chamber.drop_rock()
        chamber.fix_rock()

    height = - chamber.top_line + extra_height
    print(f"Rock {number_of_rocks}: height {height}:", "ok" if height == expected_height else f"not ok: expected {expected_height}")

if __name__ == "__main__":
    main()