import sys
from functools import cache

# create pad coordiantes (x, y)
numpad_text = "789"  \
              "456"  \
              "123"  \
              ".0A"
numpad = {numpad_text[pos]: (pos % 3, pos // 3) for pos in range(0, len(numpad_text)) if numpad_text[pos] != "."}

dirpad_text = ".^A" \
              "<v>"
dirpad = {dirpad_text[pos]: (pos % 3, pos // 3) for pos in range(0, len(dirpad_text)) if dirpad_text[pos] != "."}

# hack: 'x' * n where n <= 0 equals the empty string, for example, left(dx) = '' when dx > 0
left =  lambda dx: "<" * (-dx)
right = lambda dx: ">" * dx
up =    lambda dy: "^" * (-dy)
down =  lambda dy: "v" * dy
left_or_right = lambda dx: left(dx) if dx < 0 else right(dx)
up_or_down    = lambda dy: up(dy)   if dy < 0 else down(dy)

# +---+---+---+
# | 7 | 8 | 9 |
# +---+---+---+
# | 4 | 5 | 6 |
# +---+---+---+
# | 1 | 2 | 3 |
# +---+---+---+
#     | 0 | A |
#     +---+---+
@cache
def get_numpad_actions1(start, end):
    (x1, y1) = numpad[start]
    (x2, y2) = numpad[end]
    (dx, dy) = (x2 - x1, y2 - y1)
    if y1 == 3 and x2 == 0:    # avoid empty corner when starting from bottom row and moving to first column
        actions = up(dy) + left_or_right(dx)
    elif x1 == 0 and y2 == 3:  # avoid empty corner when starting from first column and moving to bottom row
        actions = right(dx) + down(dy)
    else:
        # favor left over up/down over right to achieve the least number of actions
        actions = left(dx) + up_or_down(dy) + right(dx)
    return actions + "A"

def get_numpad_actions(sequence):
    actions = ""
    for (start, end) in zip("A" + sequence, sequence):
        actions += get_numpad_actions1(start, end)
    return actions

#     +---+---+
#     | ^ | A |
# +---+---+---+
# | < | v | > |
# +---+---+---+
@cache
def get_dirpad_actions1(start, end):
    (x1, y1) = dirpad[start]
    (x2, y2) = dirpad[end]
    (dx, dy) = (x2 - x1, y2 - y1)
    if y1 == 0 and x2 == 0:       # avoid empty corner when moving from first row to first columm
        actions = down(dy) + left(dx)
    elif x1 == 0 and y2 == 0:     # avoid empty corner when moving from first column to first row
        actions = right(dx) + up(dy)
    else:
        # favor left over up/down over right to achieve the least number of actions
        actions = left(dx) + up(dy) + down(dy) + right(dx)
    return actions + "A"

# Returns a string of the actions to move from start to end and press the end button
# operating through multiple number of pads. Ineffecient for larger number of pads.
def get_dirpad_actions(start, end, pad_number):
    actions = get_dirpad_actions1(start, end)
    if pad_number == 1:
        return actions
    next_pad_actions = ""
    for (start, end) in zip("A" + actions, actions):
        next_pad_actions += get_dirpad_actions(start, end, pad_number - 1)
    return next_pad_actions

# Same as above, but only count the actions without actually generating them. Caching is essential.
@cache
def count_dirpad_actions(start, end, pad_number):
    actions = get_dirpad_actions1(start, end)
    if pad_number == 1:
        return len(actions)
    result = 0
    for (start, end) in zip("A" + actions, actions):
        result += count_dirpad_actions(start, end, pad_number - 1)
    return result

# Main
def generate_and_count_actions(sequence, nof_dirpads):
    actions = get_numpad_actions(sequence)
    result = 0
    for (start, end) in zip("A" + actions, actions):
        result += len(get_dirpad_actions(start, end, nof_dirpads))
    return result * int(sequence[:3])

def count_actions_without_generating(sequence, nof_dirpads):
    actions = get_numpad_actions(sequence)
    result = 0
    for (start, end) in zip("A" + actions, actions):
        result += count_dirpad_actions(start, end, nof_dirpads)
    return result * int(sequence[:3])

# sequences = [ "029A", "980A", "179A", "456A", "379A" ]    # Example: 68, 60, 68, 64, 64: 126384
sequences = [ "140A", "143A", "349A", "582A", "964A" ]    # Puzzle input

part1 = sum([generate_and_count_actions(sequence, 2) for sequence in sequences])
print("part1:", part1, "(generated)")  # 154208

part1 = sum([count_actions_without_generating(sequence, 2) for sequence in sequences])
print("part1:", part1, "(counted)") # 154208

part2 = sum([count_actions_without_generating(sequence, 25) for sequence in sequences])
print("part2:", part2, "(counted)") # 188000493837892
