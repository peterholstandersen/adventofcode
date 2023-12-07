import re
import sys
from typing import List

# part1:
# - find the first (x) and last digit (y) of each line, and compute the value 10*x + y. E.g., foo1bar2biz equals 12.
# - compute the sum of all values in the file.

def add_first_and_last(numbers: List[str]) -> int:
    return int(numbers[0]) * 10 + int(numbers[-1])

lines = open("big.in").read().strip().split("\n")             # read all lines from file
all_numbers = [ re.findall(r"\d", x) for x in lines ]         # find all numbers in each line
part1 = sum(map(add_first_and_last, all_numbers))             # compute sum of all numbers
print(part1) # 54304


# part2: as part1, only the words "one", "two", ..., "nine" are considered numbers too. E.g., one2ninefoo equals 19

numbers = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9"
}

# regexp
# - pattern: (one|two|...|nine|1|2|...|9)
# - rpattern: (eno|owt|...|enin|1|2|...|9)

pattern = "|".join(list(numbers.keys()) + list(map(str, range(1,10))))
rpattern = "|".join(list(map(lambda x: x[::-1], numbers.keys())) + list(map(str, range(1,10))))
get_value = lambda word: int(numbers.get(word, word))
get_first = lambda line: get_value(re.findall(pattern, line)[0])
get_last = lambda line: get_value(re.findall(rpattern, line[::-1])[0][::-1])
part2 = sum(map(lambda line: 10 * get_first(line) + get_last(line), open("big.in").read().strip().split("\n")))
print(part2) # 54418
