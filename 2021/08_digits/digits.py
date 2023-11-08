import sys
import time
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

def part1(filename, result):
        xs = list(map(len, (' '.join([x.split("|")[1].strip() for x in open(filename).read().strip().split("\n")])).split(" ")))
        count = xs.count(2) + xs.count(3) + xs.count(7) + xs.count(4)
        print("part1", filename, count)
        assert(count == result)

def get_digit(sequence, wiring):
    seq = ''.join(sorted([wiring[ord(a) - ord('a')] for a in sequence]))
    return digits.get(seq, None)

def get_len(n, signals):
    return [signal for signal in signals if len(signal) == n][0]

def part2(filename, expected):
    ys = [ line.strip().split(" | ") for line in open(filename).read().strip().split("\n") ]
    xs = [ (xy[0].strip().split(" "), xy[1].strip().split(" ")) for xy in ys ]
    added = 0
    count = 0
    for (signals, output) in xs:
        seven = get_len(3, signals)
        one = get_len(2, signals)
        wire_a = ord([x for x in seven if x not in one][0]) - ord('a')  # from 500865 iteratons (5 sec) to 71667 (<1 sec)
        ok = False
        for ungarble in permutations("abcdefg", 7):
            if ungarble[wire_a] != 'a':
                continue
            count += 1
            result = [ get_digit(sequence, ungarble) for sequence in signals ]
            if all(result):
                ok = True
                break
        if not ok:
            print("error")
            sys.exit(1)
        foo = int(''.join([ get_digit(ooo, ungarble) for ooo in output]))
        added += foo
    print("part2", filename, added)
    print(count)
    assert(added == expected)

def main():
    part1("small.in", 26)
    part1("big.in", 488)
    with Timer():
        part2("small.in", 61229)
    with Timer():
        part2("big.in", 1040429)

if __name__ == "__main__":
    main()