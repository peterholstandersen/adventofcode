import sys
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

def ok2(text: str, expect: str):
    if len(text) == 0:
        return "ok" if len(expect) == 0 else "premature eol, expected '"+ expect + "'"
    if text[0] in "([{>":
        return ok2(text[1:], open2close[text[0]] + expect)
    if text[0] in ")]{<":
        if len(expect) == 0:
            return "expected eol, found '" + text[0] + "'"
        else:
            return "expected '" + expect[0] + "', found '" + text[0] + "'" if text[0] != expect[0] else ok2(text[1:], expect[1:])
    print("illegal char", t0)

def ok3(text, expect):
    # print(text, expect)
    match (text, expect):
        case (["$"], ["$"]):                return "ok"
        case (["(", *rest], _):             return ok3(rest, [")"] + expect)
        case (["[", *rest], _):             return ok3(rest, ["]"] + expect)
        case (["{", *rest], _):             return ok3(rest, ["}"] + expect)
        case (["<", *rest], _):             return ok3(rest, [">"] + expect)
        case ([X, *rest1], [Y, *rest2]):    return ok3(rest1, rest2) if X == Y else f"expected {''.join(expect)}, found {''.join(text)}"
        case _:                             return "should not happen"
    print("hej")

#print(ok3(list("()$"), list("$")))
#sys.exit(1)

def ok4(text, expect):
    print("ok4:", text, expect)
    if text[0] in "(]{<":
        return ok4(text[1:], [ open2close[text[0]] ] + expect)
    return ok4(text[1:], expect[1:]) if text[0] == expect[0] else "expected " + str(expect) + " found " + str(text)

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
    for x in ["()", "())", "(())", "(((((())", "(]"]:
        print(x, ok3(list(x + "$"), list("$")))

    #part1("small.in", 26397)
    #part1("big.in", 319329)
    #part2("small.in", 288957)
    #part2("big.in", 3515583998)