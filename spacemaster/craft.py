from common import *

class Craft:
    # max g capability
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
            self.course_handler(self)

    def set_course_handler(self, fun):
        self.course_handler = fun

    def tick(self, seconds):
        self.position = self.get_position(seconds)
        (dx, dy) = self.velocity
        (ddx, ddy) = self.acceleration
        self.velocity = (dx + ddx * seconds, dy + ddy * seconds)

    def __str__(self):
        return f"{self.ident}: pos={self.position} velocity={self.velocity} burn={self.acceleration} traj={self.show_trajectory} transponder={self.transponder}"

def make_crafts():
    random.seed(42)
    heroes = Craft("Heroes", (-1000, 500), (0, 0), LIGHT_WHITE, "x", "x", None, 2)
    gate = Craft("Gate", (0, 0), (0, 0), CYAN, "o", "o", None, 2)
    donnager = Craft("Donnager", (1000, 1000), (0, 0), RED, "D", "D", "Donnager_Render_1.png", 2)
    nathan_hale = Craft("Nathan Hale", (400, 600), (0, 0), LIGHT_BLUE, "N", "N", None, 2)
    crafts = {craft.key: craft for craft in [heroes, gate, donnager, nathan_hale]}
    km_to_m = 1000
    for craft in crafts.values():
        craft.position = (craft.position[0] * km_to_m, craft.position[1] * km_to_m)
    return crafts

generic_torpedo = Craft("Torpedo", (0, 0), (0, 0), LIGHT_WHITE, "t", "t", None, 15)
generic_missile = Craft("Missile", (0, 0), (0, 0), LIGHT_WHITE, None, ",", None, 15)   # None to replaced by uuid

