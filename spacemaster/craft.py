from common import *
import pickle

class Craft:
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
    resolve = None

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
        return self.colour + self.visual + DEFAULT_COLOUR

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

    def silence_interception(self, other):
        return other.key in self.silence_interception_with

    def __str__(self):
        return f"{self.ident}: key={self.key} pos={self.position} velocity={self.velocity} burn={self.acceleration} traj={self.show_trajectory} transponder={self.transponder}"

AU = 1.496e+11
craft_templates = {
    #                 ident, position, velocity, colour, key, visual, image, max_g):
    "donnager": Craft("Donnager", (0, 0), (0, 0), RED, "D", "D", "Donnager_Render_1.png", 2),
    "generic": Craft("Generic", (0, 0), (0, 0), LIGHT_WHITE, "Z", "Z", None, 2),
}
generic_torpedo = Craft("Torpedo", (0, 0), (0, 0), LIGHT_WHITE, "t", "t", None, 15)
generic_missile = Craft("Missile", (0, 0), (0, 0), LIGHT_WHITE, None, ",", None, 15)   # None to replaced by uuid
crafts = dict()

SMALL_CRAFT = 0
LARGE_CRAFT = 1
WEAPON = 2

def generate_unique_key(kind=SMALL_CRAFT):
    global crafts
    capital_letters = list(range(ord('A'), ord('Z') + 1))
    small_letters = list(range(ord('a'), ord('z') + 1))
    digits = list(range(ord('0'), ord('9') + 1))
    if kind == LARGE_CRAFT:
        base = capital_letters + small_letters + digits
    elif kind == WEAPON:
        base = digits + small_letters + capital_letters
    else:
        base = small_letters + capital_letters + digits
    found = False
    while not found:
        for key in base:
            if chr(key) not in crafts:
                return chr(key)
    return key

def make_craft(key, name):
    global crafts, craft_templates
    if key in crafts:
        print(f"key is already there")
    if name not in craft_templates:
        print(f"unknown craft {name}")
    craft = copy.deepcopy(craft_templates[name])
    craft.key = key
    craft.character = key
    craft.visual = key
    return craft

# TODO TODO TODO
def make_generic_craft():
    # generate key, generic colour
    key = "TODO"
    make_craft(key, "generic")

def make_crafts():
    random.seed(42)
    heroes = Craft("Heroes", (-1000, 500), (0, 0), LIGHT_WHITE, "x", "x", None, 2) # Ospary
    gate = Craft("Gate", (0, 0), (0, 0), CYAN, "o", "o", None, 2)
    donnager = make_craft("D", "donnager")
    nathan_hale = Craft("Nathan Hale", (400, 600), (0, 0), LIGHT_BLUE, "N", "N", None, 2)
    # uranus = Craft("Uranus", (-2 * AU / 1000, 0), (0, 0), GREEN, "U", "U", None, 2)
    # sun = Craft("Sun", (-21.2 * AU / 1000, 0), (0, 0), RED, "S", "S", None, 2)
    crafts = {craft.key: craft for craft in [heroes, gate, donnager, nathan_hale]}
    for craft in crafts.values():
        craft.position = (craft.position[0] * 1000, craft.position[1] * 1000)
    return crafts

crafts = make_crafts()
