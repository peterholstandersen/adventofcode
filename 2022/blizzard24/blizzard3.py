import sys
import copy
import time
import os

from state import State, bfs
from utils import ansi

# Advent of Code 2022, Day 24: https://adventofcode.com/2022/day/24, https://adventofcode.com/2022/day/24/input
#
# In the code below, width and height specifies the field _including_ the walls. So the area
# inside the walls are width-2 times height-2.
#
# When we reach the round equal to width-2, the blizzards moving left and right will be
# back to their original positions. Similarly, when we reach the round height-2, the blizzards
# moving upwards and downwards will also be back to their original positions.
#
# A state in this puzzle is represented by the original text, the current position of the elf,
# and the round. Two states are equal when the original texts match, the current positions of
# the elf match, the rounds modulus width-2 match, and the rounds modulus height-2 match.
#
# Incidentally, when we reach the round equal to the lowest common multiple of width-2, height-2
# all the blizzards will be back to their original positions. For example, lcm(6,4) = 12.
#
# round 0  round 1  round 2  round 3  round 4  round 5
# ######## ######## ######## ######## ######## ########
# #.<....# #<.....# #.....<# #....<v# #...<..# #..<...#
# #.....v# #......# #......# #......# #.....v# #......#
# #......# #.....v# #......# #......# #......# #.....v#
# #......# #......# #.....v# #......# #......# #......#
# ######## ######## ######## ######## ######## ########
#
# round 6  round 7  round 8  round 9  round 10 round 11 round 12
# ######## ######## ######## ######## ######## ######## ########
# #.<....# #<....v# #.....<# #....<.# #...<..# #..<..v# #.<....#
# #......# #......# #.....v# #......# #......# #......# #.....v#
# #......# #......# #......# #.....v# #......# #......# #......#
# #.....v# #......# #......# #......# #.....v# #......# #......#
# ######## ######## ######## ######## ######## ######## ########

class FieldState(State):
    def __init__(self, text, round):
        # Each line in the text is terminated by a newline
        self.text = text.strip()                      # strip trailing newlines in case there are more than one
        self.height = text.count('\n') + 1            # +1 as we have stripped the last newline
        self.width = text.index('\n')                 # width without newline
        self.start_elf = self.find_position('E')
        self.goal = self.find_position('G')
        self.round = round
        self.elf = self.start_elf
        print(f"height: {self.height}, width: {self.width}")
        print(f"start_elf: ({self.start_elf[0]},{self.start_elf[1]})")
        print(f"goal:      ({self.goal[0]},{self.goal[1]})")

    def find_position(self, char):
        index = self.text.find(char)
        if index == -1:
            print(f"Unable to find {char}")
            sys.exit(1)
        # // is integer division, +1 to account for newline
        return (index // (self.width + 1), index % (self.width + 1))

    def __eq__(self, other):
        # Normalizing round according to width and height will account for blizzards wrapping around.
        # The rest of the values in the class are derived from text, so there is no need to check them.
        return (self.text == other.text and
                self.elf == other.elf and
                self.normalize_position(self.round, self.round) == other.normalize_position(other.round, other.round))

    def __hash__(self):
        # Hash over text, elf position and round.
        # The rest of the values in the class are derived from text, so there is no need to hash over them.
        return hash( (self.text, self.elf, self.round) )

    def __str__(self):
        highlight_elf = ansi.green + ansi.bold + ansi.reverse
        normal = ansi.reset + ansi.white
        out = f"Round {self.round}\n"
        for line in range(0, self.height):
            for column in range(0, self.width):
                if (line, column) == self.elf:
                    char = highlight_elf + '@' + normal
                elif (line, column) == self.goal:
                    char = 'G'
                elif (line, column) == self.start_elf:
                    char = '.'
                elif line == 0 or column == 0 or line == self.height - 1 or column == self.width - 1:
                    char = '#'
                else:
                    char = self.get_print_char(line, column)
                out = out + char
            out = out + "\n"
        return out

    def normalize_position(self, line, column):
        return ((line - 1) % (self.height - 2) + 1, (column - 1) % (self.width - 2) + 1)

    def get(self, line, column):
        (line, column) = self.normalize_position(line, column)
        # multiply by width + 1 compensating for the newline characters in text
        return self.text[line * (self.width + 1) + column]

    def get_print_char(self, line, column):
        count = 0
        char = '.'
        if self.get(line + self.round, column) == '^':
            char = '^'
            count = count + 1
        if self.get(line - self.round, column) == 'v':
            char = 'v'
            count = count + 1
        if self.get(line, column + self.round) == '<':
            char = '<'
            count = count + 1
        if self.get(line, column - self.round) == '>':
            char = '>'
            count = count + 1
        if count > 0:
            return '*'
        if count == 0 or count == 1:
            return char
        return str(count)

    def elf_can_move_here(self, line, column):
        # Start and goal positions are always legal, blizzards cannot reach there
        if (line, column) == self.start_elf or (line, column) == self.goal:
            return True
        # We hit a wall
        if line <= 0 or line >= self.height or column <= 0 or column >= self.width:
            return False
        # Check to see if a blizzard has arrived from any of the four directions: above, below, right or left.
        # For example, if an upwards moving blizzard ('^') was originally placed two lines below, and we are now in
        # round two, then the blizzard will now occupy this position, so the elf cannot go here.
        # self.get takes into account that blizzards wrap around
        if (self.get(line + self.round, column) == '^' or
            self.get(line - self.round, column) == 'v' or
            self.get(line, column + self.round) == '<' or
            self.get(line, column - self.round) == '>'):
            return False
        return True

    def children(self):
        children = []
        # Create a new state representing the next round
        state_copy = copy.copy(self)
        state_copy.round = state_copy.round + 1
        # Check whether the elf can stay or move in any of the four directions
        for (move_line, move_column) in [ (1,0), (0,1), (0,0), (0,-1), (-1,0) ]:
            new_line = self.elf[0] + move_line
            new_column = self.elf[1] + move_column
            if state_copy.elf_can_move_here(new_line, new_column):
                new_state = copy.copy(state_copy)
                new_state.elf = (new_line, new_column)
                children.append(new_state)
        return children

def main():

    start = \
        "#E########################################################################################################################\n" \
        "#<..<^>vv^.>>>^.>v.^v<.^<>><^v><vv.>v^v><><^<<.<..^^.<v>.^>v>><>^>><vv^^<><v>>vv><v>v.<^v>v<^v^>.^<^^<<><<<v<<><>^vv^>.^>#\n" \
        "#<>><>^^<.<v^v^.<<>^<v^^<><><v.^>^^>^^><^><^>v>v>v>>>^><<<>>v<>v>^v>>^v>v<<<.>^<<<<<>>v<<>^v^>.<v>>>v<<<vv<<v.^v^^^^^..>>#\n" \
        "#>.^>.><vv>v<><^^>..^....v>^^>>^v><<v.^><<<<^<^v><.v<.>..<>.>^v^^^.>^<v>^><^<v<><vv<vv^>v^^v<<....>^>v><<>v>^<v>>^>v^^v><#\n" \
        "#<^<v^v<<>>^>v>.<^<.v<<<>^>vv^<<v^>vvv<v><^vv^v^<>vv<vv..^>^<><<<vv^.>>v<>v.vvv.>>v^><v>><<<>^^v><^^v^^v^^v>>v><<.>^vv.^<#\n" \
        "#>>^<v>><>.>>><><.<>v><<><>vvvv>^><>vv^>^<>^<>^^>><^^>.vvv<v>^<<vv^<^v<.^.v.<vvv<<v.>^><v^^v><^.>vvvv>^.vv<^><^.^<v>vvv<<#\n" \
        "#<v^<v^><>^<v^<<^^>.v.<^.v<>^^^^^>><^<..v<^v<>>.>>^><^v<^^v^>v^<v^v><.<^<.><^^<vv^><>^v^><.<>..^>v^.v>.^<><>^.^v><>>>>^.<#\n" \
        "#><^><v.>^<^.^<^.v<v^<>v>.>v^<.>.<>.v<>>v^><><<<v^.<><<^<v<<.>vv<<.v^<>><.^<^..^^><v>.v^<<<>^.<v^..<v<<<>v^<>^<v><.^<<>><#\n" \
        "#<>vvv.v.<^<>^v.v<vv>><^^.>^>^<^v.v>>v<^^^<^<^^v.^.><<<>.<<>>^>>^<>.^>v<^.v.vv^v^^^..><v^v<^>.<v.^<>v<v><.vv<>.>>>>.^><><#\n" \
        "#<>v<v^<v<v>.^><vv><<<<>>.<<^v>.>v^<>^v>^>>.v.>>^.v^<v^vv^^.^v>^^><^<<<^^.^v<v..v<vv>^^>^vv<<>>>.><.^^<<^^<<.<<><^<^^.v><#\n" \
        "#>>><<v^^v<^<^.<<.>v><v^^><v^<>^v<^^v^vv><^.v..v.v.>vv><<^...><^v>><v^v<<v^^<v>^<><<vv>>^>>^><v>^^<>>>.<^^>.v^^^.><>v<>.<#\n" \
        "#><^^^v<><<<^v>^^><vv<vv>^<<>>.<^^vvv<<>^v^<.<><v<<>^v^..v>v<.<^^v><^<<v^v<><<^<v>v.><>v<v.>v><^vvv>^v^<v>.^<.>vvvvv<>><>#\n" \
        "#>^<>^v^^v<^vvvvv^<v>v.<<>v>>>^<^^<..>^<^<^.>v<vvvv^^><>^>^>><>v.vvv.^^v.^^>^<>>^^v<>v<<<^^.>>^>>^><v^^.<<v<>.>>><><><v.<#\n" \
        "#>^^^>>^>><<^<v>^^>>v<>>>>^v<v<.vvv<<><^^>.><vv<^.><<^>^<vv..^><v<..<>^^<.<>v<^><><>>>v>.>.>vv>.v<.<^^<v^>>>vv^<v^>v>>vv>#\n" \
        "#>>.<v>>.vv>^>><vvv<><^>^.^v>^v<>..<>^^.><v>..vv<^v>>^.vvv>>^^<vvvvvvv>^vv^^v>^<^.<v<>><<<vv^<>v^<<>><^v>>^>^^.v^<^^<>><>#\n" \
        "#<^>^>v<^<v^<^.<v^^<v.>.v^vv^^v>^^v>v^^vv^v^vv>^.><.v<.<><>v<v<>^<v...<><><<<<>.v^v^<<>^<<>>>>>><.^^^<><<><v^>^v^^<v<^v<>#\n" \
        "#.<^^>>v<v<><^^<vv<<v><^>>>>.vvv^>^^<v<<>><<v^>^><.<><vv.v<vv^<><v>v^^<v^<.>v<vv>v^v<^>>^<vv^><.<v>>^<v>>><^<^<v^>><<..v>#\n" \
        "#<.>>^.v^.^.v^v<>v>v>v^vv^^<^<<>^^><<><.v<>><v<<<vv^<<..v<v.<>^>vv^^>>v<><v^^><^^<>^v<<vv<v>vv.vvv>v<.^v^.^><><v.>v>>vvv>#\n" \
        "#<>^.v<^v>>>v>v<>^>v^<vv<<^v<<^^>vv<^<.^v.<v<vvv>vv^>.v..>>.>vv>>>v^.^^>>^>>><><><>v>>..<^.>^v<^^v^<>>><v>.^^<^<.v>^>vvv>#\n" \
        "#<^.v^<><<..^^v<v^>v>>>^vv.><v>^<>v^v^v^.>^<v><^<.>>^v><^^v>>^<<<..v<^>v>^vv>^vv^>^v.>>^<<^^>.><v<vv><v^.^<>>^>^>^^v<vvv<#\n" \
        "#>v.<^v^>>>.>>><^>>v^^^.vv.<<^v^.>v>><^>v.v><^<vvvv><<>v>v^<v^^v.<>vv.v<.><><>.^v>.>>>^<>.^>^>v.<v>^v^>v^<><.<<<^<^><^^^<#\n" \
        "#>^<>v>v>.>><>.><..vvvv<>vv<<^^v<>v<v^^vv.^<<v<v<<<<v<>><^<><<^v>^v<<<v<^v^<..vv<<<<<^.^v^>.<v^><<^^<.v>.<<<v<><>vvv.v<v<#\n" \
        "#<^^<<^<<.^>><v<v.^<^^<>>v^v.>^<>>.<<^v.^^v<^^v.^<.v<<>...<<<<^^^v^.<.>^^<>>^>v^^<v<vv^>^^<^v^<><^<<^^.^^<^vv^v<<^^<^<.^>#\n" \
        "#<^.^^.<.<<^v^<..><.^v<<>v.<^vv><<v<vv<vvv^<^^>v<v>>>v><<^.<.>^>v>>>.<><v<.vv<^^><.>^v>>v^v<.^^>.v^v>^><^^v^v>>vv>^.v<>^>#\n" \
        "#.>^.v<.>>^<><^>v><.<>>^^vv^.<.>.v>>v.>^><<..v<>v>v>>v><>v^^<^>^<<>^.<<<v^>^>v<v.>.>v^<vv^vv<^^<<<<.v^.<v.^v>>v<v^^.>v<>>#\n" \
        "#<><.^^^^<>>.<^v.>^<<>v>.<v>>>vv^^<>v^v<^.<.v^v>>>>^><^vvv.>>>v<<<.^^.v<vv^>.^v.><<.v<>>>^.^v>^vvv.<>v^<^v^<^v<^<><^^^v^<#\n" \
        "########################################################################################################################G#"

    start = \
        "#E######\n" \
        "#>>.<^<#\n" \
        "#.<..<<#\n" \
        "#>v.><>#\n" \
        "#<^v^^>#\n" \
        "######G#"


    initial_state = FieldState(start, 0)
    end_state = lambda state: state.elf == state.goal
    start_time = time.time()
    result = bfs(initial_state, end_state)
    print(f"path length: {len(result)} ... number of moves: {len(result) - 1}")
    print()
    initial_state2 = copy.copy(result[-1])
    (initial_state2.goal, initial_state2.start_elf) = (initial_state2.start_elf, initial_state2.goal)
    if initial_state2.elf != initial_state2.start_elf:
        print("Something is wrong")
        sys.exit(1)
    result2 = bfs(initial_state2, end_state)
    print(f"path length: {len(result2)} ... number of moves: {len(result2) - 1}")
    print()

    initial_state3 = copy.copy(result2[-1])
    (initial_state3.goal, initial_state3.start_elf) = (initial_state3.start_elf, initial_state3.goal)
    if initial_state3.elf != initial_state3.start_elf:
        print("Something else is wrong")
        sys.exit(1)
    result3 = bfs(initial_state3, end_state)
    print(f"path length: {len(result3)} ... number of moves: {len(result3) - 1}")
    print()

    os.system("clear")
    for s in result:
        print(ansi.top)
        print(s)
    for s in result2:
        print(ansi.top)
        print(s)
    for s in result3:
        print(ansi.top)
        print(s)

    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    main()
