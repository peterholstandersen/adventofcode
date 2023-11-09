import sys
from typing import Tuple, List
from functools import reduce
from statistics import median

# text is the text to examined for balanced parentheses.
# expected are the closing parentheses we expect to see before the eol.
#
# If all parenthesis are balanced, return ([], [])
# If we reach eol without matching all expected closing parentheses, return ([], expected)
# If we meet a mismatching parenthesis, return (text, expected) where text is the rest of the
# text starting from the mismatched parenthesis and expected is the list of closing parentheses
# we expected to meet.
#
# if we meet an opening parenthesis, we move ahead in text and add the corresponding closing parenthesis to expect.
# if text[0] is a closing parenthesis that matches expected[0], then continue matching, otherwise return (text, expected)
def match1(text: List[str], expected: List[str]) -> Tuple[List[str], List[str]]:
    match (text, expected):
        case ([], _):                       return (text, expected)
        case (["(", *rest], _):             return match1(rest, [")"] + expected)
        case (["[", *rest], _):             return match1(rest, ["]"] + expected)
        case (["{", *rest], _):             return match1(rest, ["}"] + expected)
        case (["<", *rest], _):             return match1(rest, [">"] + expected)
        case ([X, *rest1], [Y, *rest2]):    return match1(rest1, rest2) if X == Y else (text, expected)
        case _:                             return (text, expected)

def match(text: str) -> Tuple[str, str]:
    (text, expected) = match1(list(text), [])
    return (''.join(text), ''.join(expected))

# Add up the scores of the first incorrect closing parentheses (if any) for every line
def part1(filename: str, expected_result: int) -> None:
    score = { ")": 3, "]": 57, "}": 1197, ">": 25137 }
    lines = open(filename).read().strip().split("\n")
    matches = (match(line) for line in lines)
    # score lines where we reach eol before completing the match, text[0] is the first mismatch
    total = sum([score[text[0]] for (text, _) in matches if text != ""])
    print("part1", filename, total)
    assert(total == expected_result)

# Disregard lines with incorrect balanced parentheses, only score the lines where we reach eol
# without finding all the expected closing parentheses. To score a single line: start with a
# score of 0, then for all missing closing paranthesis multiply the score by 5 and add the value
# of the closing parenthesis
def part2(filename: str, expected_result: int) -> None:
    value = { ")": 1, "]": 2, "}": 3, ">": 4 }
    lines = open(filename).read().strip().split("\n")
    matches = (match(line) for line in lines)
    scores = []
    for (text, expected) in matches:
        if text == "" and expected != "":
            # we have reached eol, but we still expect more closing parentheses
            scores.append(reduce(lambda score, parenthesis: score * 5 + value[parenthesis], expected, 0))
    result = median(scores) # find the middle score, assuming there are no duplicates and len(scores) is odd ...
    print("part2", filename, result)
    assert(result == expected_result)

if __name__ == "__main__":
    part1("small.in", 26397)
    part1("big.in", 319329)
    part2("small.in", 288957)
    part2("big.in", 3515583998)