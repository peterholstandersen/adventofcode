from utils import Timer
from statistics import median

open2close = { "(": ")", "{": "}", "<": ">", "[": "]" }
close2open = { ")": "(", "}": "{", ">": "<", "]": "[" }

value = { ")": 3, "]": 57, "}": 1197, ">": 25137}

opening = open2close.keys()
closing = close2open.keys()

def ok(match, text):
    if len(text) == 0:
        # print("premature eof", match)
        return (len(match) == 0, match)
    if text[0] in opening:
        return ok(match + [text[0]], text[1:])
    if text[0] in closing:
        if len(match) == 0:
            # print("expected eof, found", text[0])
            return (False, match)
        if text[0] == open2close[match[-1]]:
            return ok(match[:-1], text[1:])
        else:
            # print("expected", open2close[match[-1]], "found", text[0])
            return (value[text[0]], [])
    print("illegal char", text[0])


def part1(filename, expected):
    lines = open(filename).read().strip().split("\n")
    total = 0
    for line in lines:
        (what, _) = ok([], line)
        if what != False:
            # print(line, what)
            total += what
    print("part1", filename, total)
    assert (total == expected)

value_part2 = { ")": 1, "]": 2, "}": 3, ">": 4}

def part2(filename, expected):
    lines = open(filename).read().strip().split("\n")
    totals = []
    for line in lines:
        (what, match) = ok([], line)
        if match != []:
            # print(line, "          ", ''.join(reversed(list(map(lambda x: open2close[x], match)))), end=" ")
            score = 0
            for x in reversed(list(map(lambda x: open2close[x], match))):
                score = score * 5 + value_part2[x]
            # print(score)
            totals.append(score)
    result = median(totals) # assuming there are duplicates ...
    print("part2", filename, result)
    assert (result == expected)

if __name__ == "__main__":
    part1("small.in", 26397)
    part1("big.in", 319329)
    part2("small.in", 288957)
    part2("big.in", 3515583998)