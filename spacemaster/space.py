import sys
import os
import re
import math
from math import sqrt, atan2, degrees, ceil, floor
from functools import cache
import datetime
import random
import signal
from copy import deepcopy
import time
import uuid

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

BG_LIGHT_CYAN = "\033[1;46m"
BG_CYAN = "\033[1;106m"
# https://i.sstatic.net/9UVnC.png
# LIGHT: (BG_BLACK, BG_RED, BG_GREEN, BG_YELLOW, BG_BLUE, BG_MAGENTA, BG_CYAN, BG_WHITE) = range(40,48)
# Bright versions starts at 100 (ends at 107)

DEFAULT_COLOUR = END # LIGHT_WHITE

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

interceptions_to_be_resolved = set()

random.seed(42)
heroes = Craft("Heroes", (-1000, 500), (0, 0), LIGHT_WHITE, "x", "x", None, 2)
gate = Craft("Gate", (0, 0), (0, 0), CYAN, "o", "o", None, 2)
donnager = Craft("Donnager", (1000, 1000), (0, 0), RED, "D", "D", "Donnager_Render_1.png", 2)
nathan_hale = Craft("Nathan Hale", (400, 600), (0, 0), LIGHT_BLUE, "N", "N", None, 2)
crafts = {craft.key: craft for craft in [heroes, gate, donnager, nathan_hale]}

generic_torpedo = Craft("Torpedo", (0, 0), (0, 0), LIGHT_WHITE, "t", "t", None, 15)
generic_missile = Craft("Missile", (0, 0), (0, 0), LIGHT_WHITE, None, ",", None, 15)   # None to replaced by uuid

km_to_m = 1000
for craft in crafts.values():
    craft.position = (craft.position[0] * km_to_m, craft.position[1] * km_to_m)

prompt = scale = center = None

def reset_view(match):
    global prompt, scale, center
    prompt = "> "
    scale = 50000
    center = (0, 0)
    for craft in crafts.values():
        craft.show_trajectory = True
    if match is not None:
        show(None)

reset_view(None)

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
        solution = -b / (2 * a)
        return [solution] if solution >= 0 else None
    solution1 = (-b + math.sqrt(foo)) / (2 * a)
    solution2 = (-b - math.sqrt(foo)) / (2 * a)
    solutions = []
    if solution1 > 0:
        solutions.append(solution1)
    if solution2 > 0:
        solutions.append(solution2)
    return None if len(solutions) == 0 else solutions

def view_craft_from_file(match):
    craft = get_craft(match.group(1))
    if craft:
        os.system(f"eog -g {craft.image}")

def get_craft(name, default="x"):
    if name == "":
        name = default
    if name in crafts:
        return crafts[name]
    print(f"{name} is lost in space")

def plot_trajectories(what):
    for craft in crafts.values():
        if craft.show_trajectory:
            for t in range(0, 10000):
                what[craft.get_position(t)] = craft.colour + "." + DEFAULT_COLOUR

def show(match):
    me = get_craft("x")
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
        (ddx, ddy) = craft.get_acceleration()
        acc = sqrt(ddx * ddx + ddy * ddy)
        print(f"{craft.get_visual()}: {speed:>10}  {acc:>4.1f} m/s2", end="")
        if craft != me:
            print(f"  {get_distance_as_text(me, craft)}", end="")
            time = get_interception_time(me, craft)
            if time:
                print(f"  tti={time}s", end="")
                #if time < 10:
                #    print(RED + BLINK + "  PROXIMITY ALERT" + DEFAULT_COLOUR, end="")
                if get_distance(me.get_position(), craft.get_position()) < 100000:
                    print(RED + BLINK + "  PROXIMITY ALERT" + DEFAULT_COLOUR, end="")
        print()
    print(RED + "\n".join([f"Resolve interception between {c1} and {c2}" for (c1, c2) in interceptions_to_be_resolved]) + DEFAULT_COLOUR)
    print()

def set_interception_course(me, target):
    me = get_craft(me)
    target = get_craft(target)
    if me is None or target is None:
        return None
    (x1, y1) = me.position
    (x2, y2) = target.position
    (dx1, dy1) = me.velocity
    (dx2, dy2) = target.velocity
    (ddx2, ddy2) = target.get_acceleration()
    for t in range(1, 36000):
        ddx1 = 2 * ((x2 - x1) / (t * t) + (dx2 - dx1) / t)
        ddy1 = 2 * ((y2 - y1) / (t * t) + (dy2 - dy1) / t)
        (ddx1, ddy1) = (ddx1 + ddx2, ddy1 + ddy2)
        g = sqrt(ddx1 * ddx1 + ddy1 * ddy1) / 9.81
        if g <= me.max_g:
            break
    if g > me.max_g:
        print(f"Unable to plot interception course with less than {me.max_g}g (or in less than 10h).")
        return None
    me.set_acceleration((ddx1, ddy1))
    me.set_course_handler(lambda craft: set_interception_course(craft.key, target.key))  # craft is also me, btw
    show(None)
    print(f"{me.get_visual()}: burn {g:.1f}g ({ddx1:.1f}, {ddy1:.1f}) (tti {t} seconds)")
    return True

def get_distance(a, b):
    (x1, y1) = a
    (x2, y2) = b
    xx = x1 - x2
    yy = y1 - y2
    return sqrt(xx * xx + yy * yy)

def get_interception_time(me, target):
    (x1, y1) = me.get_position(0)
    (dx1, dy1) = me.get_velocity(0)
    (ddx1, ddy1) = me.get_acceleration()
    (x2, y2) = target.get_position(0)
    (dx2, dy2) = target.get_velocity(0)
    (ddx2, ddy2) = target.get_acceleration()
    a = (ddx1 - ddx2) / 2
    b = (dx1 - dx2)
    c = (x1 - x2)
    foo = solve(a, b, c)
    a = (ddy1 - ddy2) / 2
    b = (dy1 - dy2)
    c = (y1 - y2)
    bar = solve(a, b, c)
    # print("foo:", foo, "bar:", bar)
    if foo is None or bar is None:
        return None
    if foo is True and bar is True:
        return 0
    if foo is True:
        return int(floor(min(bar)))
    if bar is True:
        return int(floor(min(foo)))
    foo = map(lambda x: int(floor(x)), foo)
    bar = map(lambda x: int(floor(x)), bar)
    times = [t for t in foo if t in bar]
    # print("times:", times)
    if len(times) == 0:
        return None
    time = floor(min(times))
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

def set_burn(match):
    craft = get_craft(match.group(1))
    (ddx, ddy) = (float(match.group(2)), float(match.group(3)))
    if not craft:
        return
    g = sqrt(pow((ddx / 9.81), 2) + pow((ddy / 9.81), 2))
    craft.set_acceleration((ddx, ddy))
    craft.set_course_handler(None)
    show(None)
    print(f"{craft.get_visual()}: burning ({ddx:.2f}, {ddy:.2f}) ({g:.2f}g)" + (". Here comes The Juice!" if g >= 2 else ""))

def burn_brake_Xg(match):
    me = get_craft(match.group(1))
    burn_brake = match.group(2)
    g = int(match.group(3))
    if burn_brake == "brake":
        g = -g
    (dx, dy) = me.get_velocity(0)
    n = sqrt(dx * dx + dy * dy)
    if n == 0:
        print(f"In which direction? Try burn (x,y).")
        return
    (dx, dy) = (dx / n, dy / n)  # unit vector
    (ddx, ddy) = (dx * g / 9.81, dy * g / 9.81)
    me.set_acceleration((ddx, ddy))
    me.set_course_handler(None)
    show(None)
    what = "burning" if g > 0 else "braking"
    print(f"{me.get_visual()}: {what} {abs(g)}g")

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
    print(f"{craft.get_visual()}: velocity {velocity:.0f} m/s in {time} seconds")

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
    me = get_craft(match.group(1))
    target = get_craft(match.group(2))
    if me is None or target is None:
        return
    print(f"distance from {me.get_visual()} to {target.get_visual()}: {get_distance_as_text(me, target)}")

def remove_craft(match):
    craft = get_craft(match.group(1))
    if craft:
        visual = craft.get_visual()
        del crafts[craft.key]
        show(None)
        print(f"{visual} disappears in a puff of antimatter")

def generate_torpedo_key():
    global crafts
    base = list(range(ord('0'), ord('9') + 1)) + list(range(ord('A'), ord('Z') + 1)) + list(range(ord('a'), ord('z') + 1))
    found = False
    while not found:
        for key in base:
            if chr(key) not in crafts:
                return chr(key)
    return None

def fire_torpedo(match):
    global generic_torpedo
    me = get_craft(match.group(1))
    target = get_craft(match.group(2))
    if me is None or target is None:
        return
    torpedo = deepcopy(generic_torpedo)
    key = generate_torpedo_key()
    torpedo.set_key(key)
    torpedo.set_visual(key)
    torpedo.set_ident("Torpedo " + key)
    torpedo.set_position(me.get_position())
    torpedo.set_velocity(me.get_velocity(0))
    torpedo.show_trajectory = False
    crafts[torpedo.key] = torpedo
    if not set_interception_course(torpedo.key, target.key):
        print(f"Unable to target lock {target.get_visual()}")
        return
    show(None)
    print(f"{me.get_visual()} fires torpedo at {target.get_visual()}: {torpedo.get_visual()}")

def fire_missile(match):
    global generic_missile
    me = get_craft(match.group(1))
    target = get_craft(match.group(2))
    if me is None or target is None:
        return
    missile = deepcopy(generic_missile)
    while True:
        key = str(uuid.uuid4())[:2]  # hack
        if key not in crafts:
            break
    missile.set_key(key)
    missile.set_ident("Missile " + key)
    missile.set_position(me.get_position())
    missile.set_velocity(me.get_velocity(0))
    missile.show_trajectory = False
    crafts[missile.key] = missile
    if not set_interception_course(missile.key, target.key):
        print(f"Unable to target lock {target.get_visual()}")
        return
    show(None)
    print(f"{me.get_visual()} fires missile at {target.get_visual()}")

def resolved(match):
    global interceptions_to_be_resolved
    interceptions_to_be_resolved = set()
    show(None)
    print("Resolved")

def tick(seconds):
    interception = False
    for _ in range(0, seconds):
        [ craft.tick(1) for craft in crafts.values() ]
        for craft1 in crafts.values():
            for craft2 in crafts.values():
                if craft1 != craft2 and get_distance(craft1.get_position(), craft2.get_position()) < 100:
                    interception = True
                    interceptions_to_be_resolved.add(tuple(sorted((craft1.key, craft2.key))))
        if interception:
            break
    [ craft.adjust_course() for craft in crafts.values() ]
    # show(None)

def tick_handler(match):
    tick(1 if match.group(1) == "" else int(match.group(1)))

is_running = False
def run(match):
    global is_running
    is_running = True
    while is_running:
        tick(1)
        time.sleep(1)
        show(None)

hide = ["su", "exit", ".*", "\\?"]

error_msgs = (
    "I am sorry Dave, I cannot do that.",
    "Segmentation fault (warp core dumped).",
    "Silly.",
    "Shall we play a game?",
    "You will disarm all your weapons and escort us to Sector 001, where we will begin assimilating your culture and technology.",
)

commands = (
    (r"show", show),
    (r"scale ([0-9]+)", set_scale),
    (r"center ([a-zA-Z0-9])", set_center),
    (r"view ([A-Za-z0-9]+)", view_craft_from_file),
    (r"info ([a-zA-Z0-9]+)", info),
    (r"traj ([a-zA-Z0-9]+)", toggle_trajectory),
    (r"remove ([a-zA-Z0-9]+)", remove_craft),
    (r"resolved", resolved),
    (r"([a-zA-Z0-9]+): intercept ([a-zA-Z0-9]+)", lambda m: set_interception_course(m.group(1), m.group(2))),
    (r"([a-zA-Z0-9]+): burn \(*([0-9\.\-]+)[, ]*([0-9\.\-]+)\)", set_burn),  # X: burn (0.8, 1.0)
    (r"([a-zA-Z0-9]*):?[ ]*(burn) [\(]*([0-9\.\-]+)[g]", burn_brake_Xg),  # X: burn Xg
    (r"([a-zA-Z0-9]*):?[ ]*(brake) [\(]*([0-9\.]+)[g]", burn_brake_Xg),  # X: brake Xg
    (r"([a-zA-Z0-9]+): vel [\(]*([0-9\.\-]+)[, ]*([0-9\.\-]+)[\)]*", set_velocity),  # x: vel (100, 200)
    (r"([a-zA-Z0-9]+): show v ([0-9]+)[s]", show_velocity),  # X: show vel Ns
    (r"([a-zA-Z0-9]+): show vel ([0-9]+)[s]", show_velocity),  # X: show vel Ns
    (r"([a-zA-Z0-9]+): show velo ([0-9]+)[s]", show_velocity),  # X: show vel Ns
    (r"([a-zA-Z0-9]*):?[ ]*distance ([A-Za-z0-9]+)", show_distance),  # X: distance Y
    (r"([a-zA-Z0-9]*):?[ ]*dist ([A-Za-z0-9]+)", show_distance),
    (r"([a-zA-Z0-9]+): time ([a-zA-Z0-9]+)", show_interception_time),  # X: show Y
    (r"([a-zA-Z0-9]+): show pos ([0-9]+)[s]", show_position),  # X: pos Ns")
    (r"([a-zA-Z0-9]*):?[ ]*torp[edo]* ([A-Za-z0-9]+)", fire_torpedo),  # [X: ]torpedo Y
    (r"([a-zA-Z0-9]*):?[ ]*mis[sile]* ([A-Za-z0-9]+)", fire_missile),  # [X: ]missile Y")
    (r"tick[ ]*(\-?[0-9]*)", tick_handler),
    (r"run", run),
    (r"([\+]+)", zoom),
    (r"([\-]+)", zoom),
    (r"quit", lambda m: sys.exit()),
    (r"exit", lambda m: sys.exit()),
    (f"ls", lambda m: os.system("ls")),
    (f"who", lambda m: os.system("who")),
    (r"reset", reset_view),
    (r"su", lambda _: set_prompt("# ")),
    (r"exit", lambda _: set_prompt("> ")),
    (r"\?", lambda _: print("\n".join([command for (command, _) in commands if command not in hide]))),
    (r"moria", lambda _: print("Sorry, games are not allowed right now.")),
    (r"scan", lambda _: print("You see nothing special.")),
    (r".*", lambda _: print(error_msgs[random.randint(1, len(error_msgs)) if random.randint(0, 10) == 0 else 0])),
)

def print_prompt():
    global prompt
    print((datetime.datetime.now() + datetime.timedelta(2000)).strftime("%Y-%m-%d %H:%M:%S") + prompt, end="")

def sigint_handler(signum, frame):
    global is_running
    if is_running:
        is_running = False
        return
    print()
    print("Bye")
    print(LIGHT_WHITE)
    sys.exit(1)

signal.signal(signal.SIGINT, sigint_handler)

show(None)
print_prompt()
sys.stdout.flush()
for line in sys.stdin:
    if line == "\n":
        tick(1)
        show(None)
    else:
        for (regexp, action) in commands:
            match = re.match(regexp, line)
            if match:
                action(match)
                break
    print_prompt()
    sys.stdout.flush()

# git
# move Craft and ... to craft.py
# save and load stuff (capture errors, Ctrl-C too)
# No need to resolve interception between torpedo/missile with the one firing them
# ability to remove missiles and (other two characters objects)
# add xxx
#
# max g as param to intercept command / max speed to intercept command / end-speed at intercept
#
# set run-step
# set regular course
# show time when ticking
# brake Xg, burn Xg [bearing +/- degrees]
# show scale: |...........| == X km
# Gate size (and other objects)
# make all commands default to my_craft
# missiles do not auto correct course?
# -----------------------------------------------------------------------
# ring gate is 2 AU outside Uranus' orbit
# inside the ring space / slow zone
# Ring station
# 1373 gates
# roughly 1M km i diameter
# https://expanse.fandom.com/wiki/Ring_Entities
# change reality when passing through gate!
# sensor flickers
# max speed
# -----------------------------------------------------------------------
# max speeds (torpedoes and missiles go crazy)
# visualize overlapping crafts
# cancel interception course if craft is removed
# break tick on promixity alert
# don't clear screen when updating (no problem: does not flicker)
# missile/torpedo/(crafts) factory
# craft: stock of torpedoes, counter missiles
# Incorporate resolution rolls for torpedo impact, counter missiles (and PDCs)
# cancel intecept course after reaching target?
# slow down when closing in on target to avoid overshooting [less relevant for torps]
# curseses
# show "*" interception points
# X: lay course: flip/and/burn, patrol A-B-C, orbit Y, intercept Y
# visualize gate size
# short commands
# X: command (default X to me)
# <return> repeats
# how many dots to print in a traj?
# get/create scaled images of crafts
# unify syntax
# let craft decide what to show in overview (will always allow hiding stuff)
#
#
# ------------------------------------------------------
# astroid, debris
# exhaust bloom
# orbits, sun, planets, moon, gravity (see ~/Download/planet_distance_chart.pdf)
# repeat scale+/- until interupted
# lock: Enter password to unlock
# X: EW(?) / Sensor detection
# scan
# command editing, history
# visualize stuff outside map
# voice commands
# boot sequence
