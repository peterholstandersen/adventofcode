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

    # N: Longtitude of ascending node (OM)
    # i: inclination
    # w: argument of perihelion (small omega)  = longtitude of perihelion - longtitude of the ascending node
    # a: semi-major axis
    # e: eccentricity
    # M: mean anomaly

    # N, i, w, a, e shifts slight over time, so we use the values for April 19, 1990 (Earth & Pluto are missing)
    # It is not common practice to use mean anomaly as an orbital parameter (because it is not!), but we
    # can get the values from https://ssd.jpl.nasa.gov/horizons/app.html#/ using julian day 0: 1999-12-31
    #               N       i         w         a         e    |
    # Mercury   48.2163  7.0045   29.0882   0.387098  0.205633 |    M = 168.6562_deg + 4.0923344368_deg * d
    # Venus     76.5925  3.3945   54.8420   0.723330  0.006778 |    M =  48.0052_deg + 1.6021302244_deg * d
    # Earth   -11.26064 0.00005   85.901    1.000000  0.016710 |    M = 357.2894       0.9853068413288855
    # Mars      49.4826  1.8498  286.3978   1.523688  0.093396 |    M =  18.6021_deg + 0.5240207766_deg * d
    # Jupiter  100.3561  1.3036  273.8194   5.20256   0.048482 |    M =  19.8950_deg + 0.0830853001_deg * d
    # Saturn   113.5787  2.4890  339.2884   9.55475   0.055580 |    M = 316.9670_deg + 0.0334442282_deg * d
    # Uranus    73.9510  0.7732   96.5529  19.18176   0.047292 |    M = 142.5905_deg + 0.011725806_deg  * d
    # Neptune  131.6737  1.7709  272.8675  30.05814   0.008598 |    M = 260.2471_deg + 0.005995147_deg  * d
    #
    # As of 31-12-1999: https://ssd.jpl.nasa.gov/horizons/app.html#/
    #       EC     Eccentricity, e
    #       QR     Periapsis distance, q (km)
    #       IN     Inclination w.r.t X-Y plane, i (degrees)
    #       OM     Longitude of Ascending Node, OMEGA, (degrees)
    #       W      Argument of Perifocus, w (degrees)
    #       Tp     Time of periapsis (Julian Day Number)
    #       N      Mean motion, n (degrees/sec)
    #       MA     Mean anomaly, M (degrees)
    #       TA     True anomaly, nu (degrees)
    #       A      Semi-major axis, a (km)
    #       AD     Apoapsis distance (km)
    #       PR     Sidereal orbit period (sec)
    #
    # Ceres:
    #  EC= 7.837390637197418E-02 QR= 3.814252192614897E+08 IN= 1.058336111445534E+01
    #  OM= 8.049437998936864E+01 W = 7.392263662469732E+01 Tp=  2451516.162549284287
    #  N = 2.479113932292490E-06 MA= 5.855557387082620E+00 TA= 6.870203088713857E+00
    #  A = 4.138611329459985E+08 AD= 4.462970466305074E+08 PR= 1.452131728641855E+08
    #             N (OM)                      i (IN)              w (W)                   a (A) km                 e (EC)             M (MA)                  dM (N * 3600 * 24)
    # Ceres    8.049437998936864E+01, 1.058336111445534E+01, 7.392263662469732E+01, 4.138611329459985E+08, 7.837390637197418E-02, 5.855557387082620E+00,  0.21419544375007113
    #
    # Pluto    110.0             113.175
    # Haumea   122.1628          238.779
    # Makemake  79.6194          294.835
    # Eris      35.9409          151.643

    bodies["Sun"] =     SpaceObject("Sun",         ( 0, 0, 0),        YELLOW,     "#f29f05", "*", 696340, "star_sun.png", None)

    bodies["Mercury"] = SpaceObject("Mercury", ( 0.4 * AU, 0, 0), DARK_GRAY,  "#d1cfc8", "m",   2440, "...",
                                    Orbit("Sun", N=48.3313, i=7.0047, w=29.1241, a=0.387098, e=0.205635, M=168.6562, dM=4.0923344368))
    bodies["Venus"] =   SpaceObject("Venus",   ( 0.7 * AU, 0, 0), YELLOW,     "#fade7c", "v",   6000, "...",
                                    Orbit("Sun", 76.5925, 3.3945, 54.8420, 0.723330, 0.006778, 48.0052, 1.6021302244))
    bodies["Earth"] =   SpaceObject("Earth",   ( 1.0 * AU, 0, 0), BLUE,       "#023ca7", "e",   6400, "...",
                                    Orbit("Sun", -11.26064, 0.00005, 85.901, 1.000000, 0.016710, 357.2894, 0.9853068413288855))
    bodies["Mars"] =    SpaceObject("Mars",    ( 1.5 * AU, 0, 0), RED,        "#b82020", "m",   3390, "...",
                                    Orbit("Sun", 49.4826, 1.8498, 286.3978, 1.523688, 0.093396, 18.6021, 0.5240207766))
    bodies["Jupiter"] = SpaceObject("Jupiter", ( 5.2 * AU, 0, 0), BROWN,      "#cea589", "J",  70000, "...",
                                    Orbit("Sun", 100.3561, 1.3036, 273.8194, 5.20256, 0.048482, 19.8950, 0.0830853001))
    bodies["Saturn"] =  SpaceObject("Saturn",  ( 9.6 * AU, 0, 0), YELLOW,     "#f6ddbd", "S",  58000, "...",
                                    Orbit("Sun", 113.5787, 2.4890, 339.2884, 9.55475, 0.055580, 316.9670, 0.0334442282))
    bodies["Uranus"] =  SpaceObject("Uranus",  (19.2 * AU, 0, 0), LIGHT_CYAN, "#bbe1e4", "U",  15800, "...",
                                    Orbit("Sun", 73.9510, 0.7732, 96.5529, 19.18176, 0.047292, 142.5905, 0.011725806))
    bodies["Neptune"] = SpaceObject("Neptune", (30.0 * AU, 0, 0), LIGHT_BLUE, "#3d5ef9", "N",  15300, "...",
                                    Orbit("Sun", 131.6737, 1.7709, 272.8675, 30.05814, 0.008598, 260.2471, 0.005995147))
    bodies["Ceres"] =   SpaceObject("Ceres",   ( 2.8 * AU, 0, 0), DARK_GRAY,  "#707070", "c",    490, "...",
                                    Orbit("Sun", 8.049437998936864E+01, 1.058336111445534E+01, 7.392263662469732E+01, 4.138611329459985E+08 / AU, 7.837390637197418E-02, 5.855557387082620E+00,  0.21419544375007113))

    bodies["Heroes"] = SpaceObject("Heroes",   ( 0.3 * AU, 0, 0), LIGHT_WHITE, "#eeeeee", "x", 0.040, "...", None)
    return bodies


    bodies["Pluto"] =   SpaceObject("Pluto",   (39.5 * AU, 0, 0), DARK_GRAY,  "#ddc4af", "p",   2400, "...", Orbit("Sun", 39.5 * AU, 90560))
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
    # print("Earth position:", universe.bodies["Earth"].position)

if __name__ == "__main__":
    run_all_tests()