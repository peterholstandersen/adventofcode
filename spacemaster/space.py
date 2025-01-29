import sys
import os
import re
import math
from math import sqrt, atan2, degrees
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
    show_trajectory = False
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
    def get_velocity(self, time):
        (dx, dy) = self.velocity
        for t in range(0, time + 1):
            if t == time:
                return (dx, dy)
            (ddx, ddy) = self.get_acceleration(t)
            (dx, dy) = (dx + ddx, dy + ddy)

    @cache
    def get_position(self, time):
        # s = v * t + 1/2 a + t^2
        (x, y) = self.position
        (dx, dy) = self.velocity
        for t in range(0, time):
            (x, y) = (x + dx, y + dy)
            (dx, dy) = self.get_velocity(t)
        return (x, y)

    def __str__(self):
        return f"{self.ident}: pos={self.position} velocity={self.velocity} burn={self.burn} traj={self.show_trajectory}"

heroes = Craft("Heroes", (-1000, 500), (0, 0), LIGHT_WHITE, "x")
heroes.burn = [ ((10, 0), 12), ((0, 0), 0), ((-10, 0), 12) ] # flip and burn
heroes.show_trajectory = True
gate = Craft("Gate", (0, 0), (0, 0), CYAN, "o")
donnager = Craft("Donnager", (1000, 1000), (-50, -50), RED, "D")
nathan_hale = Craft("Nathan Hale", (400, 600), (20, 15), LIGHT_BLUE, "N")
crafts = { craft.character: craft for craft in [heroes, gate, donnager, nathan_hale] }

prompt = "> "
scale = 50
center = (0, 0)

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
        if not craft.show_trajectory:
            continue
        (x, y) = craft.position
        (dx, dy) = craft.velocity
        for t in range(0, 500):
            what[craft.get_position(t)] = craft.colour + "." + DEFAULT_COLOUR

def show(match):
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

show(None)
sys.exit(1)

def tick(crafts):
    return [ ((x + x1, y + y1), (x1, y1), visual) for ((x, y), (x1, y1), visual) in crafts]

def set_prompt(p):
    global prompt
    prompt = p

def set_scale(match):
    global scale
    scale = int(match.group(1))
    show(None)

def set_center(match):
    global center
    matches = [ (x, y) for ((x, y), (_, _), visual) in crafts if match.group(1) in visual ]
    if len(matches) == 1:
        center = matches[0]
        print("center", match.group(1), center)
        show(None)
    else:
        print("cannot find", match.group(1))

def intercept(crafts, me, target):
    # Better
    # https://www.reddit.com/r/uboatgame/comments/1etr0ff/simple_picture_guide_for_calculating_an_intercept/?rdt=64572
    # https://interceptcourse.app/
    (my_pos, my_velocity, _) = get_craft(me)
    (target_pos, target_velocity, _) = get_craft(target)

    target_new_pos = add(target_pos, target_velocity)
    my_new_position = add(my_pos, my_velocity)

    dist1 = distance(my_pos, target_new_pos)
    dist2 = distance(my_new_position, target_new_pos)
    if min(dist1, dist2) < my_velocity:
        my_new_position = target_new_pos
        my_new_velcoity = sub(target_new_pos, my_position)
    else:
        my_velocity = add(my_velocity, max_acceleration)

def fire_torpedo(match):
    shooter = match.group(1)
    target = match.group(2)
    ((x1, y1), (dx, dy), _) = get_craft(shooter)
    torpedo = ((x1, x2), lambda crafts: intercept(crafts, "t", target), "t")   # TODO: unique torps ids
    # add torpedo to "crafts" (TODO: rename)
    # need courses

def info(match):
    x = get_craft(match.group(1))
    if x is None:
        return
    print(x)
    ((x, y), (dx, dy), visual) = x
    velocity = sqrt(dx * dx + dy * dy)
    bearing = round(degrees(atan2(dx, dy)))
    if bearing < 0:
        bearing = bearing + 360
    print(f"velocity: {velocity:.1f} km/s")
    print("bearing:", bearing)

def add_trajectory(match):
    global trajectories
    name = match.group(1)
    x = get_craft(match.group(1))
    if x:
        print("added", x[VISUAL])
        trajectories.add(name)
    # show(None)

def set_course(match):
    me = get_craft(match.group(1))
    target = get_craft(match.group(2))
    print(f"{me[VISUAL]}: setting course for {target[VISUAL]}")

def set_burn(match):
    me = get_craft(match.group(1))
    g = int(match.group(2))
    seconds = int(match.group(2))
    direction = int(match.group(3)) % 360
    if not me:
        return
    gs = "gs" if g > 1 else "g"
    print(f"{me[VISUAL]}: burning {g}{gs} for {seconds}s" + (". Here comes The Juice!" if g >= 2 else ""))

hide = ["su", "exit", ".*", "\\?"]

commands = (
    (r"view ([a-z]+)", view),
    (r"crafts", lambda _: print(crafts)),
    (r"scale ([0-9]+)", set_scale),
    (r"center ([a-zA-Z0-9])", set_center),
    (r"([a-zA-Z0-9]): torpedo ([a-zA-Z0-9])", fire_torpedo),
    (r"info ([a-zA-Z0-9]+)", info),
    (r"show", show),
    (r"t ([a-zA-Z0-9]+)", add_trajectory),
    (r"([a-zA-Z0-9]+): course ([a-zA-Z0-9]+)", set_course),
    (r"([a-zA-Z0-9]+): burn ([0-9]+)g ([0-9]+)s ([0-9]+)", set_burn), # X: burn Ng Ms direction
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


# X: burn Ng direction
#
# X: course Y
#
# trajectory +X, -X, reset
# view speed X
#
# X: fire torpedo [at] Y
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
# transponder codes
#
# short commands
#
# trajectory colours
# update view command

