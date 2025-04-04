from common import *
from utils import *
import clock2 as c
import view as v
import plot_view as pv
import command as cmd
from course import Orbit

class SpaceObject:
    universe = None
    max_g = None
    image = None
    colour = None
    visual = None
    colour_visual = None
    radius = None
    position = None
    velocity = (0, 0)
    acceleration = (0, 0)
    course = None

    def __init__(self, name, position, ansi_colour, rgb_colour, visual, radius, image, course):
        self.name = name
        self.position = position
        self.colour = ansi_colour
        self.visual = visual
        self.colour_visual = ansi_colour + visual + END
        self.rgb_colour = rgb_colour
        self.radius = radius
        self.image = image
        self.course = course

    def get_visual(self, size_cl, offset_cl, center_xy, scale, enhance=1):
        visual = dict()
        cl = xy_to_cl(self.position[0:2], offset_cl, center_xy, scale)
        self_xy = cl_to_xy(cl, offset_cl, center_xy, scale) # own position aligned to viewing grid
        visual[cl] = self.colour_visual
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
                    visual[(c1, l1)] = self.colour_visual
        return visual

    def update(self, last_update, now):
        if self.course:
            new_position = self.course.calculate_position(self.universe, self, last_update, now)
            if new_position:
                self.position = new_position
            else:
                self.course = None

class Ring(SpaceObject):
    def __init__(self, inner_radius, outer_radius, density, *args):
        self._inner_radius = inner_radius
        self._outer_radius = outer_radius
        self._density = density
        super().__init__(*args)

    def get_visual(self, size_cl, offset_cl, center_xy, scale, enhance=1):
        visual = dict()
        cl = xy_to_cl(self.position[0:2], offset_cl, center_xy, scale)
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
                    visual[(c1, l1)] = self.colour_visual
        return visual

class Universe:
    alive = True
    bodies = None
    clock = None
    view = None
    plot_view = None
    command = None
    _last_update = None

    def __init__(self, bodies, clock, view, plot_view, command):
        self.alive = True
        self.bodies = bodies
        self.clock = clock
        self.view = view
        self.plot_view = plot_view
        self.command = command
        self._last_update = None
        self.clock.universe = self
        self.view.universe = self
        self.plot_view.universe = self
        self.command.universe = self
        for body in bodies.values():
            body.universe = self
        self.update(force=True)

    def find_bodies(self, key):
        if key in self.bodies:
            return [ self.bodies[key] ]
        return [body for body in self.bodies.values() if key == body.visual]

    def get_body_position(self, name):
        if name in self.bodies:
            return self.bodies[name].position
        return None

    def update(self, force=False):
        now = self.clock.get_time()
        if force or self._last_update is None or now > self._last_update:
            [body.update(self._last_update, now) for body in self.bodies.values()]
            self._last_update = now

    def die(self):
        self.alive = False

# Saturn 58.000 km radius
#
# The dense main rings extend from 7,000 km (4,300 mi) to 80,000 km (50,000 mi) away from Saturn's equator, whose radius is 60,300 km (37,500 mi) (see Major subdivisions).
#
# D ring: 66,900 - 76,517. <30m     # The D Ring is the innermost ring, and is very faint.
# C ring: 74,658 - 92,000. 5m       # The C Ring is a wide but faint ring located inward of the B Ring.
# B ring: 92,000 - 117,580, 5-15m   # The B Ring is the largest, brightest, and most massive of the rings. Its thickness is estimated as 5 to 15 m.
# A ring: 122,170 - 136,775, 10-30m # The A Ring is the outermost of the large, bright rings.

def create_bodies():
    bodies = dict()
    bodies["Sun"] =     SpaceObject("Sun",         ( 0, 0, 0),        YELLOW,     "#f29f05", "*", 696340, "star_sun.png", None)
    bodies["Mercury"] = SpaceObject("Mercury", ( 0.4 * AU, 0, 0), DARK_GRAY,  "#d1cfc8", "m",   2440, "...", Orbit("Sun",  0.4 * AU,    88))
    bodies["Venus"] =   SpaceObject("Venus",   ( 0.7 * AU, 0, 0), YELLOW,     "#fade7c", "v",   6000, "...", Orbit("Sun",  0.7 * AU,   225))
    bodies["Earth"] =   SpaceObject("Earth",   ( 1.0 * AU, 0, 0), BLUE,       "#023ca7", "e",   6400, "...", Orbit("Sun",  1.0 * AU,   365))
    bodies["Mars"] =    SpaceObject("Mars",    ( 1.5 * AU, 0, 0), RED,        "#b82020", "m",   3390, "...", Orbit("Sun",  1.5 * AU,   687))
    bodies["Ceres"] =   SpaceObject("Ceres",   ( 2.8 * AU, 0, 0), DARK_GRAY,  "#707070", "c",    490, "...", Orbit("Sun",  2.8 * AU,  1682))
    bodies["Jupiter"] = SpaceObject("Jupiter", ( 5.2 * AU, 0, 0), BROWN,      "#cea589", "J",  70000, "...", Orbit("Sun",  5.2 * AU,  4333))
    bodies["Saturn"] =  SpaceObject("Saturn",  ( 9.6 * AU, 0, 0), YELLOW,     "#f6ddbd", "S",  58000, "...", Orbit("Sun",  9.6 * AU, 10759))
    bodies["Uranus"] =  SpaceObject("Uranus",  (19.2 * AU, 0, 0), LIGHT_CYAN, "#bbe1e4", "U",  15800, "...", Orbit("Sun", 19.2 * AU, 30687))
    bodies["Neptune"] = SpaceObject("Neptune", (30.0 * AU, 0, 0), LIGHT_BLUE, "#3d5ef9", "N",  15300, "...", Orbit("Sun", 30.0 * AU, 60190))
    bodies["Pluto"] =   SpaceObject("Pluto",   (39.5 * AU, 0, 0), DARK_GRAY,  "#ddc4af", "p",   2400, "...", Orbit("Sun", 39.5 * AU, 90560))
    bodies["Heroes"] = SpaceObject("Heroes",   ( 0.3 * AU, 0, 0), LIGHT_WHITE, "#eeeeee", "x", 0.040, "...", None)
    #bodies["Asteroid Belt"] = Ring(2.5 * AU, 3.3 * AU, 0.25, "Asteroid Belt",   (0, 0),    DARK_GRAY,  ".", None, "...", None, None, None)
    return bodies

    random.seed(1000)
    for n in range(0, 400):
        name = f"Asteroid-{n}"
        distance = random.randint(round(2.5 * AU), round(3.2 * AU))
        z = random.randint(-round(0.1 * AU), round(0.1 * AU))
        radius = random.randint(10, 20)
        orbit = random.randint(3 * 365, 6 * 365)
        colour = randint(80, 122) / 256
        bodies[n] = SpaceObject(name, (distance, 0, z), DARK_GRAY, (colour, colour, colour), ".", radius, "...", Orbit("Sun", distance, orbit))

    #bodies["C ring"] = Ring(75000, 85000, 1,   "C ring",   (0, 0),    LIGHT_GRAY,  ".", None, "...", "Sun", 9.6 * AU, 10759)
    #bodies["B ring"] = Ring(92000, 115000, 1,  "B ring",   (0, 0),    FAINT + BROWN,  ".", None, "...", "Sun", 9.6 * AU, 10759)
    #bodies["A ring"] = Ring(120000, 136000, 1, "A ring",   (0, 0),    YELLOW,  ".", None, "...", "Sun", 9.6 * AU, 10759)
    #bodies["Sol Gate"] = SpaceObject("Sol Gate", (21.2 * AU, 0), LIGHT_CYAN, "o", 1000, "...", None, None, None)
    return bodies

def big_bang():
    clock = c.Clock2(datetime.datetime(2030, 8, 20, 16, 49, 7, 652303).timestamp())
    plot_view = pv.PlotView3D()
    view = v.View((0, 0), plot_view.scale, 4)
    command = cmd.Command("x")
    bodies = create_bodies()
    universe = Universe(bodies, clock, view, plot_view, command)
    return universe

def run_all_tests():
    universe = big_bang()
    print("No Nones please")
    print(universe)
    print(universe.clock, universe.clock.universe, universe.clock.get_time())
    print(universe.view, universe.view.universe)
    print(universe.plot_view, universe.plot_view.universe)
    print(universe.command, universe.command.universe)
    print("Earth position:", universe.bodies["Earth"].position)

if __name__ == "__main__":
    run_all_tests()