import sys
import os
import re
import math
from math import sqrt, atan2, degrees, ceil, floor
from functools import cache
import datetime
import random
import signal

BLACK = "\033[0;30m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
BROWN = "\033[0;33m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
CYAN = "\033[0;36m"
LIGHT_GRAY = "\033[0;37m"
DARK_GRAY = "\033[1;30m"
LIGHT_RED = "\033[1;31m"
LIGHT_GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
LIGHT_BLUE = "\033[1;34m"
LIGHT_PURPLE = "\033[1;35m"
LIGHT_CYAN = "\033[1;36m"
LIGHT_WHITE = "\033[1;37m"
BOLD = "\033[1m"
FAINT = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
NEGATIVE = "\033[7m"
CROSSED = "\033[9m"
END = "\033[0m"

DEFAULT_COLOUR = LIGHT_WHITE

class Craft:
    # max g capability
    ident = None
    position = None
    velocity = None
    burn = []                   # list of (burn, direction, time)
    colour = None
    character = None
    image = None
    max_g = None
    show_trajectory = True
    transponder = None
    def __init__(self, ident, position, velocity, colour, character, image, max_g):
        self.ident = ident
        self.position = position
        self.velocity = velocity
        self.colour = colour
        self.character = character
        self.image = image
        self.max_g = max_g
        self.burn = []                    # list of ((ddx, ddy), t)
        self.generate_transponder_code()

    def get_visual(self):
        return self.colour + self.character + DEFAULT_COLOUR

    def generate_transponder_code(self):
        random.seed(hash(self.ident))
        code = ""
        for i in range(0, 3):
            code += chr(random.randint(ord("A"), ord("Z")))
        code += "-"
        for i in range(0, 8):
            code += str(random.randint(0, 10))
        self.transponder = code

    @cache
    def get_acceleration(self, time):
        if time == 0:
            return (0, 0)
        t = 0
        for (acceleration, dt) in self.burn:
            t = t + dt
            if time <= t:
                return acceleration
        return (0, 0)

    @cache
    def get_speed(self, time=0):
        (dx, dy) = self.get_velocity(time)
        return sqrt(dx * dx + dy * dy)

    @cache
    def get_velocity(self, time):
        if time == 0:
            return self.velocity
        (dx, dy) = self.get_velocity(time - 1)
        (ddx, ddy) = self.get_acceleration(time - 1)
        return (dx + ddx, dy + ddy)

    @cache
    def get_position(self, time):
        if time == 0:
            return self.position
        (x, y) = self.get_position(time - 1)
        (dx, dy) = self.get_velocity(time)
        return (x + dx, y + dy)

    def cache_clear(self):
        self.get_speed.cache_clear()
        self.get_position.cache_clear()
        self.get_velocity.cache_clear()
        self.get_acceleration.cache_clear()

    def set_burn(self, burn):
        self.cache_clear()
        self.burn = burn

    def set_velocity(self, velocity):
        self.cache_clear()
        self.velocity = velocity

    def __str__(self):
        return f"{self.ident}: pos={self.position} velocity={self.velocity} burn={self.burn} traj={self.show_trajectory} transponder={self.transponder}"

km_to_m = 1000

random.seed(42)
heroes = Craft("Heroes", (-1000, 500), (0, 0), LIGHT_WHITE, "x", None, 2)
heroes.show_trajectory = True
gate = Craft("Gate", (0, 0), (0, 0), CYAN, "o", None, 2)
donnager = Craft("Donnager", (1000, 1000), (0, 0), RED, "D", "Donnager_Render_1.png", 2)
nathan_hale = Craft("Nathan Hale", (400, 600), (0, 0), LIGHT_BLUE, "N", None, 2)
crafts = { craft.character: craft for craft in [heroes, gate, donnager, nathan_hale] }

for craft in crafts.values():
    craft.position = (craft.position[0] * km_to_m, craft.position[1] * km_to_m)

prompt = "> "
scale = 50000
center = (0, 0)

# solve 2nd degree quation a*x2 + b*x + c = 0 ... returns True if true for all x
def solve(a, b, c):
    # print("solve:", a, b, c)
    if a == 0 and b == 0:
        return True if c == 0 else None
    if a == 0:
        return [-c / b]
    foo = b * b - 4 * a * c
    if foo < 0:
        return None
    if foo == 0:
        return [-b / (2 * a)]
    bar = math.sqrt(foo)
    return [(-b + bar) / (2 * a), (-b - bar) / (2 * a)]

def view(match):
    craft = get_craft(match.group(1))
    if craft:
        os.system(f"eog -g {craft.image}")

def get_craft(name):
    if name in crafts:
        return crafts[name]
    print("cannot find", name)
    return None

def plot_trajectories(what):
    for craft in crafts.values():
        if craft.show_trajectory:
            for t in range(0, 10000):
                what[craft.get_position(t)] = craft.colour + "." + DEFAULT_COLOUR

def show(match):
    me = get_craft("x")
    [ craft.cache_clear() for craft in crafts.values() ]
    (columns, lines) = os.get_terminal_size()
    size = (columns, lines - 15)
    offset = (size[0] // 2, size[1] // 2)
    what1 = dict()
    plot_trajectories(what1)
    what1.update({ craft.position: craft.get_visual() for craft in crafts.values() })
    what = { ((x - center[0]) // scale + offset[0], (y - center[1]) // scale + offset[1]): visual for ((x, y), visual) in what1.items() if "." in visual }
    what.update({ ((x - center[0]) // scale + offset[0], (y - center[1]) // scale + offset[1]): visual for ((x, y), visual) in what1.items() if "." not in visual })
    out = ""
    for y in range(size[1], -1, -1):
        for x in range(0, size[0]):
            out += what[(x, y)] if (x, y) in what else " "
        out += "\n"
    os.system("clear")
    print(out)
    print("scale:", scale)
    print("center:", center)
    for craft in crafts.values():
        speed = craft.get_speed()
        unit = "m/s"
        if speed > 1000:
            speed = speed / 1000
            unit = "km/s"
        speed = f"{speed:.1f} {unit}"
        (ddx, ddy) = craft.get_acceleration(1)
        acc = sqrt(ddx * ddx + ddy * ddy)
        print(f"{craft.get_visual()}: {speed:>10}  {acc:>4.1f} m/s2", end="")
        if craft != me:
            print(f"  {get_distance_as_text(me, craft)}", end="")
            time = get_interception_time(me, craft)
            if time:
                print(f"  tti={time}s", end="")
        print()
    print()

def calculate_interception_course(me, target):
    me = get_craft(me)
    target = get_craft(target)
    if me is None or target is None:
        return None
    (x1, y1) = me.position
    (x2, y2) = target.position
    (dx1, dy1) = me.velocity
    (dx2, dy2) = target.velocity
    (ddx2, ddy2) = target.get_acceleration(1)
    for t in range(1, 3000):
        ddx1 = 2 * ((x2 - x1) / (t * t) + (dx2 - dx1) / t)
        ddy1 = 2 * ((y2 - y1) / (t * t) + (dy2 - dy1) / t)
        (ddx1, ddy1) = (ddx1 + ddx2, ddy1 + ddy2)
        g = sqrt(ddx1 * ddx1 + ddy1 * ddy1) / 9.81
        if g <= me.max_g:
            break
    if g > me.max_g:
        print(f"Unable to plot interception course with less than {max_g}g")
        return
    burn = [((ddx1, ddy1), t)]
    me.set_burn(burn)
    me.show_trajectory = True
    show(None)
    print(f"{me.get_visual()}: burn {g:.1f}g ({ddx1:.1f}, {ddy1:.1f}) for {t} seconds")

def get_distance(a, b):
    (x1, y1) = a
    (x2, y2) = b
    xx = x1 - x2
    yy = y1 - y2
    return sqrt(xx * xx + yy * yy)

def get_interception_time(me, target):
    (x1, y1) = me.get_position(0)
    (dx1, dy1) = me.get_velocity(0)
    (ddx1, ddy1) = me.get_acceleration(1)
    (x2, y2) = target.get_position(0)
    (dx2, dy2) = target.get_velocity(0)
    (ddx2, ddy2) = target.get_acceleration(1)
    a = (ddx1 - ddx2) / 2
    b = (dx1 - dx2)
    c = (x1 - x2)
    foo = solve(a, b, c)
    a = (ddy1 - ddy2) / 2
    b = (dy1 - dy2)
    c = (y1 - y2)
    bar = solve(a, b, c)
    if foo is None or bar is None:
        return None
    # print("foo:", foo, "bar:", bar)
    foo = map(floor, filter(lambda t: t >= 0, foo))
    bar = map(floor, filter(lambda t: t >= 0, bar))
    times = [t for t in foo if t in bar]
    # print("times:", times)
    if len(times) == 0:
        return None
    time = floor(min(times))
    # fill cache
    for n in range(0, time):
        me.get_position(n)
        target.get_position(n)

    pos1 = me.get_position(time)
    pos2 = target.get_position(time)
    dist = get_distance(pos1, pos2)
    if False:
        print("time:", time)
        print("pos1:", pos1)
        print("pos2:", pos2)
        print("dist:", dist)

    pos1a = me.get_position(time + 1)
    pos2a = target.get_position(time + 1)
    dist1 = get_distance(pos1a, pos2a)
    if False:
        print("time:", time + 1)
        print("pos1a:", pos1a)
        print("pos2a:", pos2a)
        print("dist1:", dist1)

    return time if dist < dist1 else time + 1

def show_interception_time(match):
    me = get_craft(match.group(1))
    target = get_craft(match.group(2))
    if me is None or target is None:
        return
    time = get_interception_time(me, target)
    if time:
        print(f"{me.get_visual()} intercepts {target.get_visual()} in {time} seconds")
    else:
        print(f"{me.get_visual()} will not intercept {target.get_visual()}")

def set_prompt(p):
    global prompt
    prompt = p

def set_scale(match):
    global scale
    scale = int(match.group(1))
    show(None)

def zoom(match):
    global scale
    what = match.group(1)
    if "-" in what:
        for _ in what:
            scale = 100 * scale // 90
    if "+" in what:
        for _ in what:
            scale = 90 * scale // 100
    show(None)

def set_center(match):
    global center
    craft = get_craft(match.group(1))
    if craft:
       center = craft.position
       show(None)

#def fire_torpedo(match):
#    shooter = match.group(1)
#    target = match.group(2)
#    ((x1, y1), (dx, dy), _) = get_craft(shooter)
#    torpedo = ((x1, x2), lambda crafts: intercept(crafts, "t", target), "t")   # TODO: unique torps ids

def info(match):
    x = get_craft(match.group(1))
    if x is None:
        return
    print(x)

def toggle_trajectory(match):
    name = match.group(1)
    craft = get_craft(name)
    if craft:
        craft.show_trajectory = not craft.show_trajectory
        show(None)

def set_burn_vector(match):
    craft = get_craft(match.group(1))
    (ddx, ddy) = (float(match.group(2)), float(match.group(3)))
    seconds = int(match.group(4))
    if not craft:
        return
    g = sqrt(pow((ddx / 9.81), 2) + pow((ddy / 9.81), 2))
    print(f"{craft.get_visual()}: burning ({ddx:.2f}, {ddy:.2f}) for {seconds}s ({g:.2f}g)" + (". Here comes The Juice!" if g >= 2 else ""))
    craft.set_burn([((ddx, ddy), seconds)])
    show(None)

def set_velocity(match):
    craft = get_craft(match.group(1))
    if not craft:
        return
    (dx, dy) = (float(match.group(2)), float(match.group(3)))
    craft.set_velocity((dx, dy))
    show(None)

def show_velocity(match):
    craft = get_craft(match.group(1))
    if not craft:
        return
    time = int(match.group(2))
    (dx, dy) = craft.get_velocity(time)
    velocity = sqrt(dx * dx + dy * dy)
    print(f"{craft.get_visual()}: velocity {velocity:.0f} m/s")

def reset(match):
    global scale, center
    for craft in crafts.values():
        craft.show_trajectory = True
    scale = 50
    center = (0, 0)
    show(None)

def show_position(match):
    me = get_craft(match.group(1))
    time = int(match.group(2))
    if not me:
        return
    print(f"{me.get_visual()} is at {me.get_position(time)} in {time} seconds")

def get_distance_as_text(me, target):
    dist = int(round(get_distance(me.get_position(0), target.get_position(0))))
    unit = "m"
    if dist > 1000:
        dist = dist // 1000
        unit = "km"
    return f"{dist} {unit}"

def show_distance(match):
    me = match.group(1)
    if me == "":
        me = "x"
    me = get_craft(me)
    target = get_craft(match.group(2))
    if me is None or target is None:
        return
    print(f"distance from {me.get_visual()} to {target.get_visual()}: {get_distance_as_text(me, target)}")

hide = ["su", "exit", ".*", "\\?"]

commands = (
    (r"view ([A-Za-z0-9]+)", view),
    (r"scale ([0-9]+)", set_scale),
    (r"center ([a-zA-Z0-9])", set_center),
    # (r"([a-zA-Z0-9]): torpedo ([a-zA-Z0-9])", fire_torpedo),
    (r"info ([a-zA-Z0-9]+)", info),
    (r"show", show),
    (r"traj ([a-zA-Z0-9]+)", toggle_trajectory),
    (r"([a-zA-Z0-9]+): intercept ([a-zA-Z0-9]+)", lambda m: calculate_interception_course(m.group(1), m.group(2))),
    (r"([a-zA-Z0-9]+): burn [\(]*([0-9\.\-]+)[, ]*([0-9\.\-]+)[\)]* ([0-9]+)[s]?", set_burn_vector), # X: burn (0.8, 1.0) Ns
    (r"([a-zA-Z0-9]+): vel [\(]*([0-9\.\-]+)[, ]*([0-9\.\-]+)[\)]*", set_velocity), # x: vel (100, 200)
    (r"([a-zA-Z0-9]+): show v ([0-9]+)[s]", show_velocity), # X: show vel Ns
    (r"([a-zA-Z0-9]+): show vel ([0-9]+)[s]", show_velocity), # X: show vel Ns
    (r"([a-zA-Z0-9]+): show velo ([0-9]+)[s]", show_velocity), # X: show vel Ns
    (r"([a-zA-Z0-9]+): distance ([A-Za-z0-9]+)", show_distance), # X: distance Y
    (r"([a-zA-Z0-9]*):?[ ]*dist ([A-Za-z0-9]+)", show_distance), # X: distance Y
    (r"([a-zA-Z0-9]+): time ([a-zA-Z0-9]+)", show_interception_time), # X: show Y
    (r"([a-zA-Z0-9]+): pos ([0-9]+)[s]", show_position), # X: pos Ns")
    (r"([\+]+)", zoom),
    (r"([\-]+)", zoom),
    (r"quit", lambda m: sys.exit()),
    (r"exit", lambda m: sys.exit()),
    (f"ls", lambda m: os.system("ls")),
    (f"who", lambda m: os.system("who")),
    (r"reset", reset),
    (r"su", lambda _: set_prompt("# ")),
    (r"exit", lambda _: set_prompt("> ")),
    (r"\?", lambda _: print("\n".join([command for (command, _) in commands if command not in hide]))),
    (r"moria", lambda _: print("Sorry, games are not allowed right now.")),
    (r"scan", lambda _: print("You see nothing special.")),
    (r".*", lambda _: print("I am sorry, Dave. I cannot do that.")),
)

def print_prompt():
    global prompt
    print((datetime.datetime.now() + datetime.timedelta(2000)).strftime("%Y-%m-%d %H:%M:%S") + prompt, end="")

def sigint_handler(signum, frame):
    print(LIGHT_WHITE)
    sys.exit(1)

signal.signal(signal.SIGINT, sigint_handler)

show(None)
print_prompt()
sys.stdout.flush()
for line in sys.stdin:
    for (regexp, action) in commands:
        match = re.match(regexp, line)
        if match:
            action(match)
            break
    print_prompt()
    sys.stdout.flush()


# Lots about courses and burn sequences
# do what is needed to fire torpedoes
#
# drop burn "programs"
#
# X: torpedo Y
# add xxx
# remove xxx
#
# auto correct interception (lambda as burn sequence) OR simply various course constants(?)
# X: counter torpedo Y
#
# save and load stuff
# do something at Ctrl-C (save state?)
#
# repeat tick [step] / stop
# tick +X [and -X (if su)]
# run / stop
# step
# <return> steps
#
# -----------------------------------------------------------------------
# show "*" interception points
# X: lay course: flip/and/burn, patrol A-B-C, orbit Y, intercept Y
# visualize gate size
# short commands
# X: command (default X to me)
# <return> repeats
# how many dots to print in a traj?
# get/create scaled images of crafts
# unify syntax
#
# ------------------------------------------------------
# astroid, debris
# exhaust bloom
# orbits,sun, planets, moon, gravity
# repeat scale+/- until interupted
# lock: Enter password to unlock
# X: EW(?) / Sensor detection
# scan
# weired error messages: Silly, from wargames, please report to section 0-0-0
# arglebarleboggle
# command editing, history
# visualize stuff outside map
# voice commands
# boot sequence
# PROXIMITY ALERT (red flashing)
