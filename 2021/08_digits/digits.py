import sys
import time
import re
from itertools import permutations

class Timer:
    def __init__(self):
        pass

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, *args):
        print("time:", time.time() - self.start)


#   0:      1:      2:      3:      4:
#  aaaa    ....    aaaa    aaaa    ....
# b    c  .    c  .    c  .    c  b    c
# b    c  .    c  .    c  .    c  b    c
#  ....    ....    dddd    dddd    dddd
# e    f  .    f  e    .  .    f  .    f
# e    f  .    f  e    .  .    f  .    f
#  gggg    ....    gggg    gggg    ....
#
#   5:      6:      7:      8:      9:
#  aaaa    aaaa    aaaa    aaaa    aaaa
# b    .  b    .  .    c  b    c  b    c
# b    .  b    .  .    c  b    c  b    c
#  dddd    dddd    ....    dddd    dddd
# .    f  e    f  .    f  e    f  .    f
# .    f  e    f  .    f  e    f  .    f
#  gggg    gggg    ....    gggg    gggg

digits = {
    "abcefg": '0',
    "cf": '1',
    "acdeg": '2',
    "acdfg": '3',
    "bcdf": '4',
    "abdfg": '5',
    "abdefg": '6',
    "acf": '7',
    "abcdefg": '8',
    "abcdfg": '9',
}

# Count the number of easy identifable output signals, that is, the ones of length 2, 3, 4 and 7 corresponding to the
# digits 1, 7, 4, and 8
def part1(filename, result):
    # mumbo jumbo
    xs = list(map(len, (' '.join([x.split("|")[1].strip() for x in open(filename).read().strip().split("\n")])).split(" ")))
    count = xs.count(2) + xs.count(3) + xs.count(4) + xs.count(7)
    print("part1", filename, count)
    assert(count == result)

def get_digit(garbled_signal, wiring):
    ungarbled = ''.join(sorted([wiring[ord(segment) - ord('a')] for segment in garbled_signal]))
    return digits.get(ungarbled, None)

def part2(filename, expected):
    lines = [re.findall(r"([a-z]+)", line) for line in open(filename).read().strip().split("\n")]  # list of all signals
    total = 0
    for garbled_signals in lines:
        # We fix one wire to get the running time <1 sec; the one that appears in 7, but not in 1 must be segment 'a'.
        # 7 is only one with 3 segments, 1 is the only one with 2 segments
        one =   [s for s in garbled_signals if len(s) == 2][0]
        seven = [s for s in garbled_signals if len(s) == 3][0]
        wire_a = ord([segment for segment in seven if segment not in one][0]) - ord('a')
        # Find a wiring that converts all garbled signals into valid digits. There is only one that works.
        # wiring[x - org('a')] = y means that wire y is wired to x.
        for wiring in permutations("abcdefg", 7):
            if wiring[wire_a] == 'a' and all((get_digit(signal, wiring) for signal in garbled_signals)):
                break
        assert(wiring is not None)
        total += int(''.join([ get_digit(output_signals, wiring) for output_signals in garbled_signals[-4:]]))
    print("part2", filename, total)
    assert(total == expected)

def main():
    with Timer():
        part1("small.in", 26)
        part1("big.in", 488)
        part2("small.in", 61229)
        part2("big.in", 1040429)

if __name__ == "__main__":
    main()