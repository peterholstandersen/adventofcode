import sys
import os
import re
import math
from math import sqrt, atan2, degrees, ceil, floor
from functools import cache

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
    show_trajectory = True
    def __init__(self, ident, position, velocity, colour, character):
        self.ident = ident
        self.position = position
        self.velocity = velocity
        self.colour = colour
        self.character = character
        self.burn = []                    # list of ((ddx, ddy), t)

    def get_visual(self):
        return self.colour + self.character + DEFAULT_COLOUR

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
        return f"{self.ident}: pos={self.position} velocity={self.velocity} burn={self.burn} traj={self.show_trajectory}"

heroes = Craft("Heroes", (-1000, 500), (0, 0), LIGHT_WHITE, "x")
heroes.show_trajectory = True
gate = Craft("Gate", (0, 0), (0, 0), CYAN, "o")
donnager = Craft("Donnager", (1000, 1000), (0, 0), RED, "D")
nathan_hale = Craft("Nathan Hale", (400, 600), (0, 0), LIGHT_BLUE, "N")
crafts = { craft.character: craft for craft in [heroes, gate, donnager, nathan_hale] }

prompt = "> "
scale = 50
center = (0, 0)

# solve 2nd degree quation a*x2 + b*x + c = 0 ... returns [0] true for all x
def solve(a, b, c):
    if a == 0 and b == 0:
        return [0] if c == 0 else None
    if a == 0:
        return -c / b
    foo = b * b - 4 * a * c
    if foo < 0:
        return None
    if foo == 0:
        return [-b / (2 * a)]
    bar = math.sqrt(foo)
    return [ (-b + bar) / (2 * a), (-b - bar) / (2 * a)]

def view(match):
    file = match.group(1)
    os.system(f"eog {file}.png")

def get_craft(name):
    if name in crafts:
        return crafts[name]
    print("cannot find", name)
    return None

def plot_trajectories(what):
    for craft in crafts.values():
        if craft.show_trajectory:
            for t in range(0, 500):
                what[craft.get_position(t)] = craft.colour + "." + DEFAULT_COLOUR

def show(match):
    [ craft.cache_clear() for craft in crafts.values() ]
    size = (150, 50)
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
        speed = f"{speed:.0f} {unit}"
        (ddx, ddy) = craft.get_acceleration(1)
        acc = sqrt(ddx * ddx + ddy * ddy)
        print(f"{craft.get_visual()}: {speed:>8}  {acc:>4.1f} m/s2")

def calculate_interception_course(me, target):
    # https://stackoverflow.com/questions/29919156/calculating-intercepting-vector
    # https://ideone.com/x1jVMn
    # https://www.reddit.com/r/uboatgame/comments/1etr0ff/simple_picture_guide_for_calculating_an_intercept/?rdt=64572
    # https://interceptcourse.app/
    me = get_craft(me)
    target = get_craft(target)
    if me is None or target is None:
        return None
    (x1, y1) = me.position
    (x2, y2) = target.position
    (dx1, dy1) = me.velocity
    (dx2, dy2) = target.velocity
    (ddx2, ddy2) = target.get_acceleration(1)
    max_g = 2 # TODO
    for t in range(1, 1000):
        ddx1 = 2 * ((x2 - x1) / (t * t) + (dx2 - dx1) / t) # + 1/2 * ddx * t * t
        ddy1 = 2 * ((y2 - y1) / (t * t) + (dy2 - dy1) / t ) # + 1/2 * ddy * t * t
        (ddx1, ddy1) = (ddx1 + ddx2, ddy1 + ddy2)
        g = sqrt(ddx1 * ddx1 + ddy1 * ddy1) / 9.81
        if g <= max_g:
            break
    burn = [((ddx1, ddy1), t)]
    me.set_burn(burn)
    me.show_trajectory = True
    show(None)
    print(f"{me.get_visual()}: burn {burn} {g:.2f}g {t} seconds")

def get_distance(a, b):
    (x1, y1) = a
    (x2, y1) = b
    xx = x1 - x2
    yy = y1 - y2
    return sqrt(xx * xx + yy * yy)

def show_interception_time(match):
    me = get_craft(match.group(1))
    target = get_craft(match.group(2))
    if me is None or target is None:
        return
    for time in range(0, 1000):
        ...
    # HERTIL



# def tick(crafts):
#     return [ ((x + x1, y + y1), (x1, y1), visual) for ((x, y), (x1, y1), visual) in crafts]

def set_prompt(p):
    global prompt
    prompt = p

def set_scale(match):
    global scale
    scale = int(match.group(1))
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

def add_trajectory(match):
    name = match.group(1)
    craft = get_craft(name)
    if craft:
        craft.show_trajectory = True
        print("added", craft.get_visual())
        show(None)

def set_burn_vector(match):
    print("set_burn_vector")
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

hide = ["su", "exit", ".*", "\\?"]

commands = (
    (r"view ([a-z]+)", view),
    (r"crafts", lambda _: print(crafts)),
    (r"scale ([0-9]+)", set_scale),
    (r"center ([a-zA-Z0-9])", set_center),
    # (r"([a-zA-Z0-9]): torpedo ([a-zA-Z0-9])", fire_torpedo),
    (r"info ([a-zA-Z0-9]+)", info),
    (r"show", show),
    (r"traj ([a-zA-Z0-9]+)", add_trajectory),
    (r"([a-zA-Z0-9]+): intercept ([a-zA-Z0-9]+)", lambda m: calculate_interception_course(m.group(1), m.group(2))),
    # (r"([a-zA-Z0-9]+): burn_deg ([0-9]+)g ([0-9]+)s ([0-9]+)", set_burn), # X: burn Ng Ms direction
    (r"([a-zA-Z0-9]+): burn [\(]*([0-9\.\-]+)[, ]*([0-9\.\-]+)[\)]* ([0-9]+)[s]?", set_burn_vector), # X: burn (0.8, 1.0) Ns
    (r"([a-zA-Z0-9]+): vel [\(]*([0-9\.\-]+)[, ]*([0-9\.\-]+)[\)]*", set_velocity), # x: vel (100, 200)
    (r"([a-zA-Z0-9]+): show v ([0-9]+)[s]", show_velocity), # X: show vel Ns
    (r"([a-zA-Z0-9]+): show vel ([0-9]+)[s]", show_velocity), # X: show vel Ns
    (r"([a-zA-Z0-9]+): show velo ([0-9]+)[s]", show_velocity), # X: show vel Ns
    (f"([a-zA-Z0-9]+): time ([a-zA-Z0-9]+)", show_interception_time), # X: show Y
    (r"reset", reset),
    (r"su", lambda _: set_prompt("# ")),
    (r"exit", lambda _: set_prompt("> ")),
    (r"\?", lambda _: print("\n".join([command for (command, _) in commands if command not in hide]))),
    (r".*", lambda _: print("I am sorry, Dave. I cannot do that.")),
)

show(None)
print(prompt, end="")
sys.stdout.flush()
for line in sys.stdin:
    for (regexp, action) in commands:
        match = re.match(regexp, line)
        if match:
            action(match)
            break
    # print(prompt + line)
    print(prompt, end="")
    sys.stdout.flush()


# interception time
#
# auto correct interception
# variable max_g
#
# X: fire torpedo [at] Y
# query speed at time, velocity V km/s, max acceleration Xg
#
# show "*" interception points
# calculate time of interception/impact
#
#
# show trajectory +X, -X, reset
# show speed X
#
# add object (craft, torp)
# X: set bearing N
# X: set velocity N
# X: set velocity (dx, dy)
# X: show trajectory
#
# X: remove
# X: lay course: flip/and/burn, patrol A-B-C, orbit Y, intercept Y
# X: intercept course (max g)
# X: change acceleration
# X: counter torpedo Y
# X: trajectory
#
# display time
# display time-to-impact
# run [step] / stop
# center X / coords
# colours
# save and load stuff
# capture Ctrl-C
# tick +X [and -X (if su)]
# traj on/off
# visualize stuff outside map
# log-view / lin-view
# history
# visualize gate size
# X: EW(?)
# X: blow up
# astroid, debris
# PROXIMITY ALERT (red flashing)
# weired error messages: Silly, from wargames, games are not allowed right now, please report to section 0-0-0
# arglebarleboggle
# ls, who
# lock: Enter password to unlock
# scale [ +n | -n ]
# repeat until interupted, e.g., scale -1
#
# short commands
#
# update view command
#
# X: command (default X to me)
# command editing, history
#
# X: show info (velocity, acceleration, transponder code, ...)
# generate transponder code
# bigger elements, orbits, objects (sun, planets, moon), gravity
# patroling courses
# boot sequence
#
# print entire burn sequence -- and name
# unify syntax
#
