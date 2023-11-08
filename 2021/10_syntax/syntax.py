import sys
from statistics import median

# text is the text to examined for balanced parentheses
# expect is the closing parentheses we are expecting.
# if both text and expect are ["$"] then we have reached the eol and all parenthesis are balanced.
# if we meet an opening parenthesis, we move ahead in text and add the corresponding closing parenthesis to expect.
# returns (['$'], ['$']) if all parentheses in text are balanced.
# otherwise return (text, expect), if text[0] is a closing parenthesis that does not match expect[0]
def match1(text, expect):
    match (text, expect):
        case (["$"], ["$"]):                return (text, expect)
        case (["(", *rest], _):             return match1(rest, [")"] + expect)
        case (["[", *rest], _):             return match1(rest, ["]"] + expect)
        case (["{", *rest], _):             return match1(rest, ["}"] + expect)
        case (["<", *rest], _):             return match1(rest, [">"] + expect)
        case ([X, *rest1], [Y, *rest2]):    return match1(rest1, rest2) if X == Y else (text, expect)
        case _:                             return "should not happen"

# add $ to match end of line
def match(text):
    return match1(list(text + "$"), ["$"])

# Add up the values of the first unbalanced parenthesis in each line
# "$" means we have reached eol without error, so it scores 0
def part1(filename, expected):
    value = {")": 3, "]": 57, "}": 1197, ">": 25137, "$": 0}
    lines = open(filename).read().strip().split("\n")
    total = 0
    for line in lines:
        (text, _) = match(line)
        total = total + value[text[0]]
    print("part1", filename, total)
    assert(total == expected)

# Now, disregard the corrupted lines. The remaining lines are incomplete, meaning you reach eol without closing all ...
# Find the sequence of closing characters that complete all open chunks in the line.
# To score a single line: start with a score of 0, then for all missing closing paranthesis
# multiply the score by 5 and add the value of the closing parenthesis
def part2(filename, expected):
    value = {")": 1, "]": 2, "}": 3, ">": 4}
    lines = open(filename).read().strip().split("\n")
    totals = []
    for line in lines:
        (text, expect) = match(line)
        if text == ["$"] and expect != ["$"]:
            # we have reached the end of the text, but we still expect more parenthesis to be closed
            score = 0
            for x in expect[:-1]:
                score = score * 5 + value[x]
            totals.append(score)
    result = median(totals) # assuming there are no duplicates ...
    print("part2", filename, result)
    assert(result == expected)

if __name__ == "__main__":
    part1("small.in", 26397)
    part1("big.in", 319329)
    part2("small.in", 288957)
    part2("big.in", 3515583998)