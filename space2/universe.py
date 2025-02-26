from common import *
from utils import *

class SpaceObject:
    key = None
    max_g = None
    image = None
    colour = None
    visual = None
    radius = None
    position = None
    velocity = None
    acceleration = None

    def __init__(self, key, name, position, colour, visual, radius, image):
        self.key = key # TODO: create key and visual
        self.name = name
        self.position = position
        self.colour = colour
        self.visual = visual
        self.radius = radius
        self.image = image
        pass

    def get_visual(self, bbox_xy, size_cl, offset_cl, center_xy, scale, zoom=1):
        visual = dict()
        ((min_x, min_y), (max_x, max_y)) = bbox_xy
        radius = self.radius * zoom
        (x, y) = self.position
        if min_x - radius <= x <= max_x + radius and min_y - radius <= y <= max_y + radius:
            (min_c, max_l) = xy_to_cl((x - radius, y - radius), offset_cl, center_xy, scale)
            (max_c, min_l) = xy_to_cl((x + radius, y + radius), offset_cl, center_xy, scale)
            min_c = max(0, min_c)
            min_l = max(0, min_l)
            max_c = min(size_cl[0], max_c)
            max_l = min(size_cl[1], max_l)
            print(scale, center_xy, radius, zoom, min_c, max_c, min_l, max_l)
            for c in range(min_c, max_c + 1):
                for l in range(min_l, max_l + 1):
                    xy = cl_to_xy((c, l), offset_cl, center_xy, scale)
                    if distance(xy, self.position) <= radius:
                        visual[(c, l)] = self.visual
        return visual

class Craft(SpaceObject):
    def __init__(self, *args):
        super().__init__(*args)

class Planet(SpaceObject):
    orbits = None
    days = None
    def __init__(self, orbits, days, *args):
        self.orbits = orbits
        self.days = days
        super().__init__(*args)

class Star(SpaceObject):
    def __init__(self, *args):
        super().__init__(*args)

class Universe:
    _bodies = None
    def __init__(self, bodies):
        self._bodies = bodies

    def get_body_position(self, key):
        if key in self._bodies:
            return self._bodies[key].position
        return None

def create_test_universe():
    #     # Star * Sun (0, 0) (0, 0) RED 696 star_sun.png
    bodies = dict()
    bodies["*"] = Star(           "*", "Sun",     (0, 0),        RED,    "*", 696000, "start_sun.png")
    bodies["m"] = Planet("*", 88, "m", "Mercury", (0.4 * AU, 0), YELLOW, "m",   2400, "...")    # 2.4M km radius
    universe = Universe(bodies)
    return universe

def run_all_tests():
    universe = create_test_universe()
    print(universe)

if __name__ == "__main__":
    run_all_tests()