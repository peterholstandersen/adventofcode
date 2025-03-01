

def foo():
    radius = self.radius * enhance
    if min_x - radius <= x <= max_x + radius and min_y - radius <= y <= max_y + radius:
        (min_c, max_l) = xy_to_cl((x - radius, y - radius), offset_cl, center_xy, scale)
        (max_c, min_l) = xy_to_cl((x + radius, y + radius), offset_cl, center_xy, scale)
        min_c = max(0, min_c)
        min_l = max(0, min_l)
        max_c = min(size_cl[0], max_c)
        max_l = min(size_cl[1], max_l)
        print(self.visual, scale, center_xy, radius, enhance, min_c, max_c, min_l, max_l)
        if min_c == max_c and min_l == max_l:
            visual[(min_c, min_l)] = self.visual
            return visual
        for c in range(min_c, max_c + 1):
            for l in range(min_l, max_l + 1):
                xy = cl_to_xy((c, l), offset_cl, center_xy, scale)
                print(self.visual, c, l, distance(xy, self.position), radius)
                if distance(xy, self.position) <= radius:
                    visual[(c, l)] = self.visual
                else:
                    visual[(c, l)] = "."
        return visual


def get_visual(self, bbox_xy, size_cl, offset_cl, center_xy, scale, enhance=1):
    visual = dict()
    ((min_x, min_y), (max_x, max_y)) = bbox_xy
    radius = self.radius * enhance
    (x, y) = self.position
    if min_x - radius <= x <= max_x + radius and min_y - radius <= y <= max_y + radius:
        (min_c, max_l) = xy_to_cl((x - radius, y - radius), offset_cl, center_xy, scale)
        (max_c, min_l) = xy_to_cl((x + radius, y + radius), offset_cl, center_xy, scale)
        min_c = max(0, min_c)
        min_l = max(0, min_l)
        max_c = min(size_cl[0], max_c)
        max_l = min(size_cl[1], max_l)
        print(self.visual, scale, center_xy, radius, enhance, min_c, max_c, min_l, max_l)
        if min_c == max_c and min_l == max_l:
            visual[(min_c, min_l)] = self.visual
            return visual
        for c in range(min_c, max_c + 1):
            for l in range(min_l, max_l + 1):
                xy = cl_to_xy((c, l), offset_cl, center_xy, scale)
                print(self.visual, c, l, distance(xy, self.position), radius)
                if distance(xy, self.position) <= radius:
                    visual[(c, l)] = self.visual
                else:
                    visual[(c, l)] = "."
    return visual


def _get_visual(self, universe, size_cl):
    offset_cl = (size_cl[0] // 2, size_cl[1] // 2)
    # (min_x, max_y) is correct since line 0 represents the maximum y value
    (min_x, max_y) = cl_to_xy((0, 0), offset_cl, self.center, self.scale)
    (max_x, min_y) = cl_to_xy(size_cl, offset_cl, self.center, self.scale)
    bbox_xy = ((min_x, min_y), (max_x, max_y))
    visual = dict()
    for body in universe.bodies.values():
        visual.update(body.get_visual(bbox_xy, size_cl, offset_cl, self.center, self.scale, self.enhance))
    return visual


# move to utils
def match_and_get(pattern, text, getter):
    match = re.match(pattern, text)
    if match:
        return getter(match)
    return None

def parse_relative_position(universe, text):
    text = text.strip()
    xy = parse_absolute_position(universe, text)
    foo = match_and_get(rf"{number}\s*d\s*{number}", text, lambda match: match.groups())
    if foo:
        (degrees, dist) = (float(foo[0]), float(foo[1]))
        print("ddxyz:", degrees, dist)
    else:
        print("ddxyz:", None)
    return (0,0)

def parse_absolute_position(universe, text):
    text = text.replace(" ", "")
    xy = match_and_get(coords, text, lambda match: (float(match.group(1)), float(match.group(2))))
    if not xy:
        xy = match_and_get(ident, text, lambda match: universe.get_body_position(match.group(1)))
    return xy
