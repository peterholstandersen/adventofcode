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
