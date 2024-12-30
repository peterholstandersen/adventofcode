import sys

test = {
  "029A": "<vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A",
  "980A": "<v<A>>^AAAvA^A<vA<AA>>^AvAA<^A>A<v<A>A>^AAAvA<^A>A<vA>^A<A>A",
  "179A": "<v<A>>^A<vA<A>>^AAvAA<^A>A<v<A>>^AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A",
  "456A": "<v<A>>^AA<vA<A>>^AAvAA<^A>A<vA>^A<A>A<vA>^A<A>A<v<A>A>^AAvA<^A>A",
  "379A": "<v<A>>^AvA^A<vA<AA>>^AAvA<^A>AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A",
}

numeric_pad = {
    '7': (0, 0),
    '8': (1, 0),
    '9': (2, 0),
    '4': (0, 1),
    '5': (1, 1),
    '6': (2, 1),
    '1': (0, 2),
    '2': (1, 2),
    '3': (2, 2),
    '0': (1, 3),
    'A': (2, 3)
}

directional_pad = {
    '^': (1, 0),
    'A': (2, 0),
    '<': (0, 1),
    'v': (1, 1),
    '>': (2, 1)
}


# +---+---+---+
# | 7 | 8 | 9 |
# +---+---+---+
# | 4 | 5 | 6 |
# +---+---+---+
# | 1 | 2 | 3 |
# +---+---+---+
#     | 0 | A |
#     +---+---+
#
#     +---+---+
#     | ^ | A |
# +---+---+---+
# | < | v | > |
# +---+---+---+

left = lambda dx: "<" * (-dx)
right = lambda dx: ">" * dx
up = lambda dy: "^" * (-dy)
down = lambda dy: "v" * dy

move_horizontally = lambda dx: left(dx) if dx < 0 else right(dx)
move_vertically = lambda dy: up(dy) if dy < 0 else down(dy)

def common(dx, dy):
    horizontal = left(dx) if dx < 0 else right(dx)
    vertical = up(dy) if dy < 0 else down(dy)
    if dx == 0:
        action = vertical
    elif dy == 0:
        action = horizontal
    elif dx < 0 and dy < 0:  # move left, up
        action = horizontal + vertical
    elif dx < 0 and dy > 0:  # move left, down
        action = horizontal + vertical
    elif dx > 0 and dy < 0:  # move right, up
        action = horizontal + vertical
    elif dx > 0 and dy > 0:  # move down, right
        action = vertical + horizontal
    return action + "A"

def operate_numeric_pad(start, end):
    (x1, y1) = numeric_pad[start]
    (x2, y2) = numeric_pad[end]
    (dx, dy) = (x2 - x1, y2 - y1)
    if y1 == 3 and x2 == 0:
        return move_vertically(dy) + move_horizontally(dx) + "A"
    if x1 == 0 and y2 == 3:
        return move_horizontally(dx) + move_vertically(dy) + "A"
    return common(dx, dy)

def operate_directional_pad(start, end):
    if start == "A" and end == "<":
        return "v<<A"
    if start == "^" and end == "<":
        return "v<A"
    (x1, y1) = directional_pad[start]
    (x2, y2) = directional_pad[end]
    (dx, dy) = (x2 - x1, y2 - y1)
    action = ""
    if x1 == 0 and y1 == 1 and dx > 0:
        action += ">"
        dx = dx - 1
    return action + common(dx, dy)

def onp(text):
    action = ""
    current = "A"
    for ttt in text:
        action += operate_numeric_pad(current, ttt)
        current = ttt
    return action

def odp(text):
    action = ""
    current = "A"
    for ttt in text:
        action += operate_directional_pad(current, ttt)
        current = ttt
    return action

def do_one_sequence(text):
    action1 = onp(text)
    action2 = odp(action1)
    action3 = odp(action2)
    # print(f"{text}: {action3}")
    return action3

# sequences = [ "029A", "980A", "179A", "456A", "379A" ]    # Example: 68, 60, 68, 64, 64: 126384
sequences = [ "140A", "143A", "349A", "582A", "964A" ]    # Puzzle input

part1 = sum([len(do_one_sequence(sequence)) * int(sequence[:3]) for sequence in sequences])
print("part1:", part1) # 154208
sys.exit(1)

for what in sequences:
    do_one_sequence(what)
    print(f"{what}: {test[what] if what in test else None}")
    print()

def suk(text):
    print("suk:", text)
    for (t1, t2) in zip(text, text[1:]):
        print(f"from {t1} to {t2}:", operate_directional_pad(t1, t2))
