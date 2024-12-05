import sys

# file = "small.in"
file = "big.in"

text = open(file).read().split("\n")
dim = len(text[0])

def get(text, x, y):
    return text[x][y] if 0 <= x < dim and 0 <= y < dim else None

def match_word(word, text, x, y):
    matches = 0
    for (x1,y1) in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
        if all([get(text, x + x1*i, y + y1*i) == word[i] for i in range(0, len(word))]):
            matches += 1
    return matches

def match_part2(text, line, col):
    mas = list("MAS")
    sam = list("SAM")
    for diag in [((-1, -1), (0, 0), (1, 1)), ((-1, 1), (0, 0), (1, -1))]:
        xx = [ get(text, line + line1, col + col1) for (line1, col1) in diag ]
        if xx != mas and xx != sam:
            return 0
    return 1

part1 = sum([match_word("XMAS", text, x, y) for x in range(0, dim) for y in range(0, dim)])
part2 = sum([match_part2(text, x, y) for x in range(0, dim) for y in range(0, dim)])

print("part1:", part1) # 2557
print("part2:", part2) # 1854


# ============= Visual coding =================

patterns1 = [
    ["XMAS"],
    ["SAMX"],
    ["X", "M", "A", "S"],
    ["S", "A", "M", "X"],
    ["X...",
     ".M..",
     "..A.",
     "...S"],
    ["S...",
     ".A..",
     "..M.",
     "...X"],
    ["...X",
     "..M.",
     ".A..",
     "S..."],
    ["...S",
     "..A.",
     ".M..",
     "X..."]
]

patterns2 = [
    ["M.S",
     ".A.",
     "M.S"],
    ["M.M",
     ".A.",
     "S.S"],
    ["S.S",
     ".A.",
     "M.M"],
    ["S.M",
     ".A.",
     "S.M"]
]

def match_pattern(pattern, text, line, col):
    for line1 in range(0, len(pattern)):
        for col1 in range(0, len(pattern[line1])):
            if pattern[line1][col1] == ".":
                continue
            try:
                if pattern[line1][col1] != text[line + line1][col + col1]:
                    return False
            except IndexError:
                return False
    return True

def count_matches(patterns, text):
    count = 0
    for line in range(0, len(text)):
        for col in range(0, len(text[line])):
            for pattern in patterns:
                if match_pattern(pattern, text, line, col):
                    count += 1
    return count

part1 = count_matches(patterns1, text)
part2 = count_matches(patterns2, text)

print()
print("part1:", part1)
print("part2:", part2)


# ======= List (in)comprenhensions ======
# Hard to make a comprenhensive list comprehension of the match_pattern function ...

count_patterns_again = lambda patterns, text: [match_pattern(pattern, text, line, col)
                                               for line in range(0, len(text))
                                                 for col in range(0, len(text[line]))
                                                   for pattern in patterns]\
                                               .count(True)
part1 = count_patterns_again(patterns1, text)
part2 = count_patterns_again(patterns2, text)

print()
print("part1:", part1)
print("part2:", part2)
