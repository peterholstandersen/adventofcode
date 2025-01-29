import sys
import os
import re
import math
from math import sqrt, atan2, degrees

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

POSITION = 0
VELOCITY = 1
VISUAL = 2

gate = ((0, 0), (0, 0), CYAN + "o" + LIGHT_WHITE)
heroes = ((2000, 2000), (-100, 0), LIGHT_WHITE + "x" + LIGHT_WHITE)
donnager = ((1000, 1000), (-50, -50), RED + "D" + LIGHT_WHITE)
unn = ((400, 600), (0, 0), LIGHT_BLUE + "N" + LIGHT_WHITE)
crafts = (gate, heroes, donnager, unn)

prompt = "> "
scale = 100
center = (0, 0)
trajectories = []

def view(match):
    file = match.group(1)
    os.system(f"eog {file}.png")

def get_object(name):
    global crafts
    matches = [ x for x in crafts if name in x[VISUAL] ]
    target = None
    if len(matches) > 1:
        print("multiple targets found", name)
    elif len(matches) == 0:
        print("cannot find", name)
    else:
        target = matches[0]
    return target

def plot_trajectories(what):
    global crafts, scale, center, trajectories
    for name in trajectories:
        craft = get_object(name)
        if not craft:
            continue
        ((x, y), (dx, dy), visual) = craft




def show(match):
    global crafts, scale, center, trajectories
    size = (150, 50)
    offset = (size[0] // 2, size[1] // 2)
    what = dict()
    plot_trajectories(what)
    what = { ((x - center[0]) // scale + offset[0], (y - center[1]) // scale + offset[1]): visual for ((x, y), _, visual) in crafts }
    out = ""
    for y in range(size[1], -1, -1):
        for x in range(0, size[0]):
            out += what[(x, y)] if (x, y) in what else " "
        out += "\n"
    os.system("clear")
    print(out)
    print("scale:", scale)
    print("center:", center)

def tick(crafts):
    return [ ((x + x1, y + y1), (x1, y1), visual) for ((x, y), (x1, y1), visual) in crafts]

def set_prompt(p):
    global prompt
    prompt = p

def set_scale(match):
    global scale
    scale = int(match.group(1))

def set_center(match):
    global center
    matches = [ (x, y) for ((x, y), (_, _), visual) in crafts if match.group(1) in visual ]
    if len(matches) == 1:
        center = matches[0]
        print("center", match.group(1), center)
    else:
        print("cannot find", match.group(1))

def intercept(crafts, me, target):
    # Better
    # https://www.reddit.com/r/uboatgame/comments/1etr0ff/simple_picture_guide_for_calculating_an_intercept/?rdt=64572
    # https://interceptcourse.app/
    (my_pos, my_velocity, _) = get_object(me)
    (target_pos, target_velocity, _) = get_object(target)

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
    ((x1, y1), (dx, dy), _) = get_object(shooter)
    torpedo = ((x1, x2), lambda crafts: intercept(crafts, "t", target), "t")   # TODO: unique torps ids
    # add torpedo to "crafts" (TODO: rename)
    # need courses

def info(match):
    x = get_object(match.group(1))
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
    x = get_object(match.group(1))
    trajectories.add(x)
    show(None)

hide = ["su", "exit", ".*", "\\?"]

commands = (
    (r"view ([a-z]+)", view),
    (r"crafts", lambda _: print(crafts)),
    (r"scale ([0-9]+)", set_scale),
    (r"center ([a-zA-Z0-9])", set_center),
    (r"([a-zA-Z0-9]): torpedo ([a-zA-Z0-9])", fire_torpedo),
    (r"info ([a-zA-Z0-9]+)", info),
    (r"show", show),
    (r"t X", add_trajectory),
    (r"su", lambda _: set_prompt("# ")),
    (r"exit", lambda _: set_prompt("> ")),
    (r"\?", lambda _: print("\n".join([command for (command, _) in commands if command not in hide]))),
    (r".*", lambda _: print("I am sorry, Dave. I cannot do that.")),
)

# show(None)
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

# trajectory +X, -X, reset
#
# X: fire torpedo [at] Y
#
# add object (craft, torp)
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