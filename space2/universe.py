from common import *
from utils import *
import clock as c

class SpaceObject:
    universe = None
    key = None
    max_g = None
    image = None
    colour = None
    visual = None
    radius = None
    position = None
    velocity = None
    acceleration = None
    orbits = None
    distance = None
    days = None

    def __init__(self, key, name, position, colour, visual, radius, image, orbits, distance, days):
        self.key = key
        self.name = name
        self.position = position
        self.colour = colour
        self.visual = colour + visual + END
        self.radius = radius
        self.image = image
        self.orbits = orbits
        self.distance = distance
        self.days = days

    def get_visual(self, size_cl, offset_cl, center_xy, scale, enhance=1):
        visual = dict()
        cl = xy_to_cl(self.position, offset_cl, center_xy, scale)
        self_xy = cl_to_xy(cl, offset_cl, center_xy, scale) # own position aligned to viewing grid
        visual[cl] = self.visual
        radius = self.radius * enhance
        (c, l) = cl
        (radius_c, radius_l) = xy_to_cl((radius, - radius), (0, 0), (0, 0), scale)
        (min_c, max_c) = (max(0, c - radius_c), min(size_cl[0], c + radius_c))
        (min_l, max_l) = (max(0, l - radius_l), min(size_cl[1], l + radius_l))
        # print(self.visual, c, l, radius_c, radius_l, min_c, max_c, min_l, max_l)
        for c1 in range(min_c, max_c + 1):
            for l1 in range(min_l, max_l + 1):
                xy = cl_to_xy((c1, l1), offset_cl, center_xy, scale)
                if distance(xy, self_xy) <= radius:
                    visual[(c1, l1)] = self.visual
        return visual

    def update(self, last_update, now):
        if self.orbits is not None:
            xy = self.universe.get_body_position(self.orbits)
            if xy is None:
                print(f"{orbits} is lost in space.")
                orbits = None
                return
            (x, y) = xy
            day = now.timestamp() / 86400
            angle = math.radians(360) - math.radians(360) * (float(day % self.days) / float(self.days))
            dx = math.sin(angle) * self.distance
            dy = math.cos(angle) * self.distance
            self.position = (x + dx, y + dy)

class Ring(SpaceObject):
    def __init__(self, inner_radius, outer_radius, density, *args):
        self._inner_radius = inner_radius
        self._outer_radius = outer_radius
        self._density = density
        super().__init__(*args)

    def get_visual(self, size_cl, offset_cl, center_xy, scale, enhance=1):
        visual = dict()
        cl = xy_to_cl(self.position, offset_cl, center_xy, scale)
        self_xy = cl_to_xy(cl, offset_cl, center_xy, scale) # own position aligned to viewing grid
        # visual[cl] = self.visual
        if center_xy == (0, 0):
            enhance = 1
        inner_radius = self._inner_radius * enhance
        outer_radius = self._outer_radius * enhance
        (c, l) = cl
        (radius_c, radius_l) = xy_to_cl((outer_radius, - outer_radius), (0, 0), (0, 0), scale)
        (min_c, max_c) = (max(0, c - radius_c), min(size_cl[0], c + radius_c))
        (min_l, max_l) = (max(0, l - radius_l), min(size_cl[1], l + radius_l))
        # print(self.visual, c, l, radius_c, radius_l, min_c, max_c, min_l, max_l)
        random.seed(hash(self.name))
        for c1 in range(min_c, max_c + 1):
            for l1 in range(min_l, max_l + 1):
                xy = cl_to_xy((c1, l1), offset_cl, center_xy, scale)
                if inner_radius <= distance(xy, self_xy) <= outer_radius and randint(0, 100) / 100 < self._density:
                    visual[(c1, l1)] = self.visual
        return visual

class Universe:
    bodies = None
    clock = None
    _last_update = None

    def __init__(self, bodies, clock, last_update):
        self.bodies = bodies
        self.clock = clock
        self._last_update = last_update

    def get_body_position(self, key):
        if key in self.bodies:
            return self.bodies[key].position
        return None

    def update(self):
        now = self.clock.timestamp
        if now <= self._last_update:
            return
        [body.update(self._last_update, now) for body in self.bodies.values()]
        self._last_update = now

# Planet m  Mercury 0.4  LIGHT_RED     88
# Planet v  Venus   0.7  YELLOW       225
# Planet e  Earth   1.0  LIGHT_BLUE   365
# Planet M  Mars    1.5  RED          687
# Planet c  Ceres   2.8  DARK_GRAY   1682
# Planet J  Jupiter 5.2  YELLOW      4333
# Planet S  Saturn  9.6  YELLOW     10759
# Planet U  Uranus 19.2  LIGHT_CYAN 30687
# Planet N  Neptune 30.0 LIGHT_BLUE 60190
# Planet p  Pluto   39.5 DARK_GRAY  90560

# Saturn 58.000 km radius
#
# The dense main rings extend from 7,000 km (4,300 mi) to 80,000 km (50,000 mi) away from Saturn's equator, whose radius is 60,300 km (37,500 mi) (see Major subdivisions).
#
# D ring: 66,900 - 76,517. <30m     # The D Ring is the innermost ring, and is very faint.
# C ring: 74,658 - 92,000. 5m       # The C Ring is a wide but faint ring located inward of the B Ring.
# B ring: 92,000 - 117,580, 5-15m   # The B Ring is the largest, brightest, and most massive of the rings. Its thickness is estimated as 5 to 15 m.
# A ring: 122,170 - 136,775, 10-30m # The A Ring is the outermost of the large, bright rings.

def create_test_universe(start_thread=False):
    last_update = datetime.datetime(2030, 8, 20, 16, 49, 7, 652303)
    clock = c.make_clock(last_update + datetime.timedelta(1), start_thread=start_thread)
    bodies = dict()
    bodies["*"] = SpaceObject("*", "Sun",     (0, 0),         RED,        "*", 696340, "star_sun.png", None, None, None)
    bodies["m"] = SpaceObject("m", "Mercury", ( 0.4 * AU, 0), LIGHT_RED,  "m",   2440, "...", "*",  0.4 * AU,    88)
    bodies["v"] = SpaceObject("v", "Venus",   ( 0.7 * AU, 0), YELLOW,     "v",   6000, "...", "*",  0.7 * AU,   225)
    bodies["e"] = SpaceObject("e", "Earth",   ( 1.0 * AU, 0), BLUE,       "e",   6400, "...", "*",  1.0 * AU,   365)
    bodies["M"] = SpaceObject("M", "Mars",    ( 1.5 * AU, 0), RED,        "m",   6400, "...", "*",  1.5 * AU,   687)
    bodies["c"] = SpaceObject("c", "Ceres",   ( 2.8 * AU, 0), DARK_GRAY,  "c",    490, "...", "*",  2.8 * AU,  1682)
    bodies["J"] = SpaceObject("J", "Jupiter", ( 5.2 * AU, 0), YELLOW,     "J",  70000, "...", "*",  5.2 * AU,  4333)
    bodies["S"] = SpaceObject("S", "Saturn",  ( 9.6 * AU, 0), YELLOW,     "S",  58000, "...", "*",  9.6 * AU, 10759)
    bodies["U"] = SpaceObject("U", "Uranus",  (19.2 * AU, 0), LIGHT_CYAN, "U",  15800, "...", "*", 19.2 * AU, 30687)
    bodies["N"] = SpaceObject("N", "Neptun",  (30.0 * AU, 0), LIGHT_BLUE, "N",  15300, "...", "*", 30.0 * AU, 60190)
    bodies["p"] = SpaceObject("p", "Pluto",   (39.5 * AU, 0), DARK_GRAY,  "p",   2400, "...", "*", 39.5 * AU, 90560)

    # dont enhance!
    bodies["belt"]   = Ring(2.5 * AU, 3.3 * AU, 0.25, "belt", "Asteroid Belt",   (0, 0),    DARK_GRAY,  ".", None, "...", None, None, None)

    bodies["c-ring"] = Ring(75000, 85000, 1, "c-ring", "C ring",   (0, 0),    LIGHT_GRAY,  ".", None, "...", "*", 9.6 * AU, 10759)
    bodies["b-ring"] = Ring(92000, 115000, 1, "b-ring", "B ring",   (0, 0),    LIGHT_GRAY,  ".", None, "...", "*", 9.6 * AU, 10759)
    bodies["a-ring"] = Ring(120000, 136000, 1, "a-ring", "A ring",   (0, 0),    LIGHT_GRAY,  ".", None, "...", "*", 9.6 * AU, 10759)

    # bodies["o"] = SpaceObject("o", "Moon",    (AU, AU),       LIGHT_GRAY, "m",   1737, "...", "e", 384400, 27)

    universe = Universe(bodies, clock, last_update)
    for body in bodies.values():
        body.universe = universe
    return (universe, clock)

def run_all_tests():
    (universe, clock) = create_test_universe()
    print(clock)
    print(universe)
    universe.update()

if __name__ == "__main__":
    run_all_tests()