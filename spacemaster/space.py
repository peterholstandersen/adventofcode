from common import *
from craft import *

interceptions_to_be_resolved = set()
crafts = make_crafts()
prompt = scale = center = None
is_running = False
savefile = "space-" + str(int(time.time())) + ".pickle"
save_frequency = 10
next_save = time.time() + save_frequency
locked = False

development_mode = True
# development_mode = False

def reset_view(match):
    global prompt, scale, center
    prompt = "> "
    scale = 50000
    center = (0, 0)
    for craft in crafts.values():
        craft.show_trajectory = True
    if match is not None:
        show(None)

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
    solution1 = (- b + math.sqrt(foo)) / (2 * a)
    solution2 = (- b - math.sqrt(foo)) / (2 * a)
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
    what.update({ craft.get_position(t): craft.colour + "." + DEFAULT_COLOUR for craft in crafts.values() if craft.show_trajectory for t in range(0, 10000) })

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
    print(f"scale 1:{scale}    |----------| = {scale * 10 // 1000} km")
    print("center:", center)
    for (dict_key, craft) in crafts.items():
        visual = craft.get_visual() if len(dict_key) == 1 else dict_key # hack
        speed = craft.get_speed()
        unit = "m/s"
        if speed > 1000:
            speed = speed / 1000
            unit = "km/s"
        speed = f"{speed:.1f} {unit}"
        (ddx, ddy) = craft.get_acceleration()
        acc = sqrt(ddx * ddx + ddy * ddy)
        print(f"{visual}: {speed:>10}  {acc:>4.1f} m/s2", end="")
        if craft != me:
            print(f"  {get_distance_as_text(me, craft)}", end="")
            time = get_interception_time(me, craft)
            if time:
                print(f"  tti={time}s", end="")
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
    me.set_course_handler(set_interception_course, target.key)
    show(None)
    # print(f"{me.get_visual()}: burn {g:.1f}g ({ddx1:.1f}, {ddy1:.1f}) (tti {t} seconds)")
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
        print("time:", time, "pos1:", pos1, "pos2:", pos2, "dist:", dist)
    pos1a = me.get_position(time + 1)
    pos2a = target.get_position(time + 1)
    dist1 = get_distance(pos1a, pos2a)
    if False:
        print("time:", time + 1, "pos1a:", pos1a, "pos2a:", pos2a, "dist1:", dist1)
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
    i = len(what)
    factors = [80, 70, 60, 50, 40, 30, 20, 10]
    if i >= len(factors):
        i = len(factors) - 1
    factor = factors[i]
    if "-" in what:
        for _ in what:
            scale = 100 * scale // factor
    if "+" in what:
        for _ in what:
            scale = factor * scale // 100
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

def set_position(match):
    craft = get_craft(match.group(1))
    if not craft:
        return
    (x, y) = (float(match.group(2)), float(match.group(3)))
    craft.set_position((x, y))
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
    print(f"{craft.get_visual()}: velocity {velocity:.0f} m/s in {time} seconds")

def show_position(match):
    me = get_craft(match.group(1))
    time = int(match.group(2))
    if not me:
        return
    print(f"{me.get_visual()} is at {me.get_position(time)} in {time} seconds")

def as_text(dist):
    if dist > 1.496e+11:
        dist = dist / 1.496e+11
        unit = " AU"
        return f"{dist:.1f}{unit}"
    unit = " m"
    if dist > 1000:
        dist = dist / 1000
        unit = " km"
    if dist > 1000:
        dist = dist / 1000
        unit = "K km"
    if dist > 1000:
        dist = dist / 1000
        unit = "M km"
    return f"{dist:.1f}{unit}"

def get_distance_as_text(me, target):
    return as_text(int(round(get_distance(me.get_position(0), target.get_position(0)))))

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
    torpedo.silence_interception_with.add(me.key)
    me.silence_interception_with.add(torpedo.key)
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
    missile.silence_interception_with.add(me.key)
    me.silence_interception_with.add(missile.key)
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
                if craft1 == craft2 or get_distance(craft1.get_position(), craft2.get_position()) > 100 or craft1.silence_interception(craft2) or craft2.silence_interception(craft1):
                    continue
                interception = True
                interceptions_to_be_resolved.add(tuple(sorted((craft1.key, craft2.key))))
        if interception:
            break
    [ craft.adjust_course() for craft in crafts.values() ]
    # show(None)

def tick_handler(match):
    tick(1 if match.group(1) == "" else int(match.group(1)))

def run(match):
    global is_running
    is_running = True
    while is_running:
        tick(1)
        time.sleep(1)
        show(None)

# noinspection PyBroadException
def save(match, quiet=False):
    global savefile
    filename = "save/" + (match.group(1) if match and match.group(1) != "" else savefile)
    if filename[-7:] != ".pickle":
        filename = filename + ".pickle"
    try:
        with open(filename, "wb") as file:
            crafts_copy = copy.deepcopy(crafts)
            # [ craft.set_course_handler(None) for craft in crafts_copy.values() ]
            pickle.dump(crafts_copy, file)
        if not quiet:
            print("Saved", filename)
    except:
        print(f"Error save to {filename}")

# noinspection PyBroadException
def load(filename):
    global savefile
    filename = "save/" + (match.group(1) if match and match.group(1) != "" else savefile)
    if filename[-7:] != ".pickle":
        filename = filename + ".pickle"
    try:
        with open(filename, "rb") as file:
            crafts = pickle.load(file)
        show(None)
        print("Loaded", filename)
        # print("Autocorrection of interception courses cancelled (including missiles and torpedoes)")
    except:
        print(f"Error loading {filename}")

hide = ["su", "exit", ".*", "\\?"]

error_msgs = (
    "I am sorry Dave, I cannot do that.",
    "Segmentation fault (warp core dumped).",
    "Silly.",
    "Shall we play a game?",
    "You will disarm all your weapons and escort us to Sector 001, where we will begin assimilating your culture and technology.",
)

def add_craft(match):
    key = match.group(1)
    name = match.group(2)
    craft = make_craft(key, name)
    if craft:
        crafts[key] = craft
        show(None)
        print(f"{craft.get_visual()} appears in a puff of matter")

commands = (
    (r"show", show),
    (r"scale ([0-9]+)", set_scale),
    (r"center ([a-zA-Z0-9])", set_center),
    (r"view ([A-Za-z0-9]+)", view_craft_from_file),
    (r"info ([a-zA-Z0-9]+)", info),
    (r"traj ([a-zA-Z0-9]+)", toggle_trajectory),
    (r"add ([a-zA-Z0-9]) ([a-zA-Z0-9]+)", add_craft),
    (r"remove ([a-zA-Z0-9]+)", remove_craft),
    (r"resolved", resolved),
    (r"save[ ]*([a-zA-Z0-9\.\-]*)", save),
    (r"load[ ]*([a-zA-Z0-9\.\-]*)", load),
    (r"([a-zA-Z0-9]+): intercept ([a-zA-Z0-9]+)", lambda m: set_interception_course(m.group(1), m.group(2))),
    (r"([a-zA-Z0-9]+): burn \(*([0-9\.\-]+)[, ]*([0-9\.\-]+)\)", set_burn),  # X: burn (0.8, 1.0)
    (r"([a-zA-Z0-9]*):?[ ]*(burn) [\(]*([0-9\.\-]+)[g]", burn_brake_Xg),  # X: burn Xg
    (r"([a-zA-Z0-9]*):?[ ]*(brake) [\(]*([0-9\.]+)[g]", burn_brake_Xg),  # X: brake Xg
    (r"([a-zA-Z0-9]+): pos [\(]*([0-9\.\-]+)[, ]*([0-9\.\-]+)[\)]*", set_position),  # x: pos (100, 200)
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
    (r"error", lambda _: 1 // 0),
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
    if locked:
        print()
        return
    print()
    print("Bye")
    print(LIGHT_WHITE)
    sys.exit(1)

def dotdotdot(text, pause):
    #print(text, end=" ")
    for t in text + " ":
        print(chr(7), end="")
        print(t, end="")
        sys.stdout.flush()
        time.sleep(0.1)
    for _ in range(0, pause * 3):
        # print(".", end="")
        sys.stdout.flush()
        time.sleep(0.1)
    print()
    sys.stdout.flush()
    time.sleep(1)

def lock(pause=0):
    global locked
    locked = True
    print(RED, end="")
    dotdotdot("SECURITY ALERT", pause)
    dotdotdot("HACKING ATTEMPT DETECTED", pause)
    dotdotdot("INTRUSION PROTOCOL A-1734 ACTIVATED", pause)
    print(chr(7), end="")
    print()
    time.sleep(2)
    print(chr(7), end="")
    print()
    time.sleep(1)
    print(chr(7), end="")
    print()
    time.sleep(1)
    print(chr(7), end="")
    print(BLINK + "LOCKED")
    time.sleep(1)
    print(END)
    print()
    print("Enter password to unlock: ", end="")
    sys.stdout.flush()
    for line in sys.stdin:
        if line.strip() == "password":
            return
        print("Enter password to unlock: ", end="")
        sys.stdout.flush()
    locked = False

def generic_error(e):
    # print("internal error:", e)
    traceback.print_exc()
    if development_mode:
        sys.exit()
    save(None, quiet=False)
    print()
    time.sleep(5)
    lock(5)

signal.signal(signal.SIGINT, sigint_handler)
reset_view(None)

show(None)
print_prompt()
sys.stdout.flush()
for line in sys.stdin:
    if line == "\n":
        tick(1)
        show(None)
        if time.time() >= next_save:
            save(None)
            next_save = time.time() + save_frequency
    else:
        for (regexp, action) in commands:
            match = re.match(regexp, line)
            if match:
                try:
                    action(match)
                except Exception as e:
                    generic_error(e)
                break
    print_prompt()
    sys.stdout.flush()

# add: more crafts, torpedo/missiles, clean up use of "key" (read from file)
#
# max g as param to intercept command / max speed to intercept command / end-speed at intercept
# set regular course
#
# Gate size (and other objects)
#
# set run-step
# show time when ticking / store time in file
# brake/burn Xg with -/+ degrees
#
# General conversion of units: m, km, 42K km, 42M km, AU (1.496e+11 = 149.600.000 km ~ 150 km) [return as (N, "K")]
# unit conversion for all output (acc, center, ...)
#
# load/save: narrow exception
# -----------------------------------------------------------------------
# load scenarios
# set position more easily
# fun sequences by specification (error, boot, ...)
# make all commands default to my_craft
# ring gate is 2 AU outside Uranus' orbit
# inside the ring space / slow zone
# Ring station
# 1373 gates
# roughly 1M km i diameter
# https://expanse.fandom.com/wiki/Ring_Entities
# change reality when passing through gate!
# sensor flickers when in ring space
# max speed
# unit interpretation of input
# show: remove extra line after listing of crafts
# fun use of ANSI codes
# -----------------------------------------------------------------------
# macro/tactical mode (combat lightning)
# max speeds (torpedoes and missiles go crazy)
# visualize overlapping crafts
# cancel interception course if craft is removed
# don't clear screen when updating (no problem: does not flicker)
# missile/torpedo/(crafts) factory
# craft: stock of torpedoes, counter missiles
# Incorporate resolution rolls for torpedo impact, counter missiles (and PDCs)
# cancel interception course after reaching target?
# slow down when closing in on target to avoid overshooting [less relevant for torps]
# ANSI to move cursor about and lots more
# show "*" interception points
# X: lay course: flip/and/burn, patrol A-B-C, orbit Y, intercept Y
# short commands / unify syntax
# how many dots to print in a traj?
# get/create scaled images of crafts
# let craft decide what to show in overview (will always allow hiding stuff)
# ------------------------------------------------------
# strain warning
# astroid, debris
# exhaust bloom
# orbits, sun, planets, moon, gravity (see ~/Download/planet_distance_chart.pdf)
# repeat scale+/- until interupted  / autoscale
# lock: Enter password to unlock
# X: EW(?) / Sensor detection
# scan
# command editing, history
# visualize stuff outside map
# voice commands
# boot sequence
# client-server / web view