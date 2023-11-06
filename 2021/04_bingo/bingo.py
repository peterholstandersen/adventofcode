import sys
import re
import copy

# https://adventofcode.com/2021/day/4

BINGO = 1

class Board:
    def __init__(self, numbers):
        self.numbers = numbers
        # rows, cols, and all represent the remaining numbers during the game
        self.rows = [ set(self.numbers[n: n + 5]) for n in range(0, 25, 5) ]
        self.cols = [ set(self.numbers[n * 5 + m] for n in range(5)) for m in range(5) ]
        self.all = set(numbers)

    def call_number(self, number):
        # if any row or column is empty, we have bingo
        self.all.discard(number)
        _ = [ self.rows[n].discard(number) for n in range(5) ]
        _ = [ self.cols[n].discard(number) for n in range(5) ]
        return BINGO if any([len(self.rows[n]) == 0 or len(self.cols[n]) == 0 for n in range(5)]) else None

    def get_score(self):
        return sum(map(int, self.all))

    def __str__(self):
        return str(self.numbers) + "\n" + "rows: " + str(self.rows) + "\n" + "cols: " + str(self.cols) + "\n" + "all: " + str(self.all)

def main(filename, part1, part2):
    text = open(filename).read().strip().split("\n\n")
    called = text[0].split(",")
    boards = [Board(re.findall(r"(\d+)", board)) for board in text[1:]]
    boards_copy = copy.deepcopy(boards)

    # Part 1: find the first board with bingo
    for number in called:
        bingo_boards = list(filter(lambda board: board.call_number(number) == BINGO, boards))
        if len(bingo_boards) == 1:
            break
    score = bingo_boards[0].get_score()
    result = score * int(number)
    print(f"part1 result ({filename}):", result)
    assert(result == part1)

    # Part 2: Figure out which board is the last to get bingo
    boards = boards_copy
    for number in called:
        boards1 = [board for board in boards if board.call_number(number) != BINGO]
        if len(boards1) == 0:
            break
        boards = boards1
    score = boards[0].get_score()
    result = score * int(number)
    print(f"part2 result ({filename})", result)
    assert(result == part2)

if __name__ == "__main__":
    main("small.in", 4512, 1924)
    main("big.in", 41668, 10478)