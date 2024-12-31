def operate_directional_pad_XXX(start, end):
    if start == "A" and end == "<":
        action = "v<<A"
    elif start == "^" and end == "<":
        action = "v<A"
    elif start == "<":
        action = move_horizontally(dx) + move_vertically(dy) + "A"
    else:
        (x1, y1) = directional_pad[start]
        (x2, y2) = directional_pad[end]
        (dx, dy) = (x2 - x1, y2 - y1)
        action = ""
        if x1 == 0 and y1 == 1 and dx > 0:
            action += ">"
            dx = dx - 1
        action += common(dx, dy)
    return action


test = {
  "029A": "<vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A",
  "980A": "<v<A>>^AAAvA^A<vA<AA>>^AvAA<^A>A<v<A>A>^AAAvA<^A>A<vA>^A<A>A",
  "179A": "<v<A>>^A<vA<A>>^AAvAA<^A>A<v<A>>^AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A",
  "456A": "<v<A>>^AA<vA<A>>^AAvAA<^A>A<vA>^A<A>A<vA>^A<A>A<v<A>A>^AAvA<^A>A",
  "379A": "<v<A>>^AvA^A<vA<AA>>^AAvA<^A>AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A",
}

def operate_pad(text, pad):
    global remember
    text = "A" + text
    action = "".join([pad(text[i], text[i + 1]) for i in range(0, len(text) - 1)])
    if pad == operate_directional_pad:
        remember[text] = action
    return action

def chop(text):
    xxx = text.strip("A").split("A")
    action = ""
    for yyy in xxx:
        zzz = operate_pad(yyy + "A", operate_directional_pad)
        print(f"{yyy:<4} {zzz}")
        action += zzz
    return action

def test_it():
    for start in directional_pad:
        for end in directional_pad:
            if start == end:
                continue
            action = operate_directional_pad(start, end)
            print(start, end, "", action)

def operate_directional_pad_not_optimal(start, end):
    # need to favor up/down over left/right
    (x1, y1) = directional_pad[start]
    (x2, y2) = directional_pad[end]
    (dx, dy) = (x2 - x1, y2 - y1)
    action = ""
    # moving right is always safe
    if dx > 0:
        action += ">" * dx
        dx = 0
    # now it safe to move up and down
    if dy > 0:
        action += "v" * dy
    else:
        action += "^" * (-dy)
    dy = 0
    if dx < 0:
        action += "<" * (-dx)
    action += "A"
    return action
