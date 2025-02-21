from common import *
import pickle

class Base:
    ident = None
    position = None
    velocity = None
    acceleration = None
    colour = None
    key = None
    visual = None
    image = None
    max_g = None
    show_trajectory = True
    transponder = None
    course_handler = None
    course_arg = None
    target = None

    def __init__(self, ident, position, velocity, colour, key, visual, image, max_g):
        self.ident = ident
        self.position = position
        self.velocity = velocity
        self.colour = colour
        self.key = key
        self.visual = visual
        self.image = image
        self.max_g = max_g
        self.acceleration = (0, 0)
        self.generate_transponder_code()
        self.silence_interception_with = set()

    def get_visual(self):
        return self.colour + self.visual[0] + DEFAULT_COLOUR

    def set_visual(self, visual):
        self.visual = visual

    def set_ident(self, ident):
        self.ident = ident
        self.generate_transponder_code()

    def set_key(self, key):
        self.key = key

    def generate_transponder_code(self):
        random.seed(hash(self.ident))
        code = ""
        for i in range(0, 3):
            code += chr(random.randint(ord("A"), ord("Z")))
        code += "-"
        for i in range(0, 8):
            code += str(random.randint(0, 10))
        self.transponder = code

    def get_acceleration(self, t=None):
        return self.acceleration

    def get_speed(self, t=0):
        (dx, dy) = self.get_velocity(t)
        return sqrt(dx * dx + dy * dy)

    def get_velocity(self, t):
        (dx, dy) = self.velocity
        (ddx, ddy) = self.acceleration
        return (dx + ddx * t, dy + ddy * t)

    def set_position(self, pos):
        self.position = pos

    def get_position(self, t=0):
        (x, y) = self.position
        (dx, dy) = self.velocity
        (ddx, ddy) = self.acceleration
        foo = lambda pos, v, a: pos + v * t + (1/2) * a * t * t
        return (foo(x, dx, ddx), foo(y, dy, ddy))

    def set_acceleration(self, acceleration):
        self.acceleration = acceleration

    def set_velocity(self, velocity):
        self.velocity = velocity

    def adjust_course(self):
        if self.course_handler:
            self.course_handler(self.key, self.course_arg)

    def set_course_handler(self, fun, arg=None):
        self.course_handler = fun
        self.course_arg = arg

    def tick(self, seconds):
        self.position = self.get_position(seconds)
        (dx, dy) = self.velocity
        (ddx, ddy) = self.acceleration
        self.velocity = (dx + ddx * seconds, dy + ddy * seconds)

    def __str__(self):
        return f"{self.ident}: key={self.key} pos={self.position} velocity={self.velocity} burn={self.acceleration} target={self.target.key if self.target else None} image={self.image}"

class Craft(Base):
    def __init__(self, ident, position, velocity, colour, key, visual, image, max_g):
        super().__init__(ident, position, velocity, colour, key, visual, image, max_g)

class Weapon(Base):
    def __init__(self, ident, position, velocity, colour, key, visual, image, max_g):
        super().__init__(ident, position, velocity, colour, key, visual, image, max_g)

class Planet(Base):
    def __init__(self, ident, position, velocity, colour, key, visual, image, max_g):
        super().__init__(ident, position, velocity, colour, key, visual, image, max_g)

class Star(Base):
    def __init__(self, ident, position, velocity, colour, key, visual, image, max_g):
        super().__init__(ident, position, velocity, colour, key, visual, image, max_g)

AU = 1.496e+11
generic_torpedo = Weapon("Torpedo", (0, 0), (0, 0), LIGHT_WHITE, "t", "t", None, 15)
generic_missile = Weapon("Missile", (0, 0), (0, 0), LIGHT_WHITE, None, ",", None, 15)

def generate_unique_key(crafts, start="a"):
    from_to = lambda a, b: list(range(ord(a), ord(b) + 1))
    selection = list(map(chr, from_to('a', 'z') + from_to('A', 'Z') + from_to('0', '9')))
    index = selection.index(start) if start in selection else 0
    found = False
    for key in selection[index:] + selection[:index]:
        if key not in crafts:
            return key
    return "!"

def make_craft(crafts, name, key=None, colour=None):
    name = name.lower()
    ships = [filename for filename in os.listdir(SHIPS_PATH) if name in filename and filename.endswith(".png")]
    if len(ships) == 0:
        print(f"{name} is lost in space")
        return
    filename = ships[random.randint(0, len(ships) - 1)]
    xs = filename[:-4].split("_")
    match = re.match("([0-9]+)m", xs[-1])
    if not match:
        xs.append("50m")
        size = 50
    else:
        size = int(match.group(1))
    army = xs[0]
    name = " ".join(xs[1:-1])
    if not key:
        key = name[0] if size < 100 else name[0].upper()
    key = generate_unique_key(crafts, key)
    if not colour:
        colours = { "mcrn": RED, "unn": LIGHT_BLUE, "fn": LIGHT_PURPLE, "opa": YELLOW, "civil": LIGHT_GREEN, "protogen": LIGHT_GRAY }
        colour = colours[army] if army in colours else LIGHT_WHITE
    ident = name.capitalize()
    position = (0, 0)
    velocity = (0, 0)
    visual = key
    image = filename
    max_g = 2
    craft = Craft(ident, position, velocity, colour, key, visual, image, max_g)
    return craft

planets = [
    ("Mercury",  0.4, "me", LIGHT_RED, 88), # Solid red, 2.4M km (radius)
    ("Venus",    0.7, "v", YELLOW, 225), # Cream, 6M km
    ("Earth",    1.0, "e", LIGHT_BLUE, 365), # Clear blue, 6.4M km
    ("Mars",     1.5, "ma", RED, 687), # Clear red, 3.4M km
    # Belt       2.8 Black      (Ceres), 490 km
    ("Ceres",    2.8, "c", DARK_GRAY, 1682),
    ("Jupiter",  5.2, "J", YELLOW, 4333), # Orange, 70M km
    ("Saturn",   9.6, "S", YELLOW, 10759), # Clear gold, 58M km
    ("Uranus",  19.2, "U", BLUE, 30687), # Dark blue, 15.8M km
    ("Neptune", 30.0, "N", LIGHT_BLUE, 60190), # Light blue, 15.3M km
    ("Pluto",   39.5, "p", DARK_GRAY, 90560), #  29.7-39.5-49.3 (closest-average-most_distant) Brown. 2.4K km
    # Gate 21.2
]

def set_day(crafts, day):
    for (planet, distance, key, _, orbit) in planets:
        if key not in crafts:
            continue
        if not isinstance(crafts[key], Planet):
            print(f"set_day: skipping {planet}. {crafts[key].get_visual()} is not a planet")
            continue
        angle = math.radians(360) - math.radians(360) * (float(day % orbit) / float(orbit))
        x = math.sin(angle) * distance * AU
        y = math.cos(angle) * distance * AU
        crafts[key].set_position((x, y))

def make_planets():
    col = LIGHT_WHITE
    psst = { "*": Star("Sun", (0, 0), (0, 0), RED, "*", "*", None, None) }
    psst.update({ key: Planet(name, (dist * AU, 0), (0, 0), colour, key, key, None, None) for (name, dist, key, colour, _) in planets })
    return psst

foo = [
    ("Heroes", -1000000, 500000, "x", "ospary"),
    ("Donnager", 1000000, 600000, "D", "donnager"),
    ("Leonideas", 400000, -300000, "L", "leonideas"),
    ("Behemonth", -800000, -200000, "B", "behemoth"),
    ("Gate", 0, 0, "o", "ring"),
]

def make_setup_1():
    crafts = dict()
    for (_, x, y, key, name) in foo:
        colour = LIGHT_WHITE if name == "Heroes" else None
        craft = make_craft(crafts, name, key, colour)
        craft.set_position((x + 21.2 * AU, y))
        crafts[key] = craft
    return crafts