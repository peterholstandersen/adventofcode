from common import *
from craft import *

simulated_time = datetime.datetime.now() + datetime.timedelta(2000)
interceptions_to_be_resolved = set()
# crafts = make_planets()
crafts = dict()
prompt = scale = center = None
is_running = False
savefile = "space-" + str(int(time.time())) + ".pickle"
save_frequency = 10
next_save = time.time() + save_frequency
locked = False
show_lock_sequence_on_generic_error = False
tactical_scale = 2000000
navigation_scale = AU // 10
exit_on_ctrl_c = True
inside_ring = False
exit_on_error = False
tick_on_return = 1
autocenter = None

def reset_view(match):
    global crafts, prompt, scale, center
    prompt = "> "
    # scale = navigation_scale
    scale = tactical_scale
    center = (21.2 * AU, 0) # gate
    for craft in crafts.values():
        craft.show_trajectory = True
    set_day(crafts, simulated_time.timestamp() // 86400)
    if match is not None:
        show(None)

def set_scale_and_center(s, c):
    global scale, center, autocenter
    scale = s
    me = get_craft(c)
    if me:
        center = (int(me.get_position()[0]), int(me.get_position()[1]))
        if c == "x":
            autocenter = "x"
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

def get_craft(name, default="x"):
    if name == "":
        name = default
    if name in crafts:
        return crafts[name]
    print(f"{name} is lost in space")

def plot_trajectories(what):
    what.update({ craft.get_position(t): craft.colour + "." + DEFAULT_COLOUR for craft in crafts.values() if craft.show_trajectory for t in range(0, 10000) })

def make_view_text(crafts):
    out = ""
    out += f"center {autocenter if autocenter else center}   scale 1:{scale}    |----------| = {scale * 10 // 1000} km\n"
    me = get_craft("x")
    if me is None:
        out += "\n"
        return out
    for (dict_key, craft) in crafts.items():
        if scale < AU / 1000 and isinstance(craft, Planet):
            continue
        visual = craft.get_visual() if len(dict_key) == 1 else dict_key # hack
        speed = craft.get_speed()
        unit = "m/s"
        if speed > 1000:
            speed = speed / 1000
            unit = "km/s"
        speed = f"{speed:.1f} {unit}"
        (ddx, ddy) = craft.get_acceleration()
        acc = sqrt(ddx * ddx + ddy * ddy)
        out += f"{visual}: {craft.ident:<20} {speed:>10}  {acc:>4.1f} m/s2"
        if craft != me:
            out += f"  {distance_as_text(me, craft)}"
            time = get_interception_time(me, craft)
            if time:
                out += f"  tti={time}s"
                if distance(me.get_position(), craft.get_position()) < 100000:
                    out += RED + BLINK + "  PROXIMITY ALERT" + DEFAULT_COLOUR
        out += "\n"
    out += RED + "\n".join([f"Resolve interception between {c1} and {c2}" for (c1, c2) in interceptions_to_be_resolved]) + DEFAULT_COLOUR
    return out


def show(match):
    global scale, center
    view_text = make_view_text(crafts)
    center_xy = center
    (columns, lines) = os.get_terminal_size()
    size_cl = (columns, lines - view_text.count("\n") - 4)
    offset_cl = (size_cl[0] // 2, size_cl[1] // 2)
    cl_to_xy = lambda cl: ((cl[0] - offset_cl[0]) * scale + center_xy[0], (offset_cl[1] - cl[1]) * scale - center_xy[1])
    xy_to_cl = lambda xy: ((xy[0] - center_xy[0]) // scale + offset_cl[0], (- xy[1] + center_xy[1]) // scale + offset_cl[1])
    what_xy = dict()
    plot_trajectories(what_xy)
    what_xy.update({ craft.position: craft.get_visual() for craft in crafts.values() })
    what_cl = dict()
    what_cl.update({ xy_to_cl(xy): visual for (xy, visual) in what_xy.items() if "." in visual })         # dots first
    what_cl.update({ xy_to_cl(xy): visual for (xy, visual) in what_xy.items() if "." not in visual })     # anything else overrides dots
    out = ""
    for line in range(0, size_cl[1]):
        for col in range(0, size_cl[0]):
            if inside_ring:
                (x, y) = cl_to_xy((col, line))
                if sqrt(x * x + y * y) > 1000000000:
                    out += BG_CYAN + " " + DEFAULT_COLOUR
                    continue
            out += what_cl[(col, line)] if (col, line) in what_cl else " "
        out += "\n"
    os.system("clear")
    print(out + view_text)
    sys.stdout.flush()

def set_course_helper(me, x2, y2, target=None):
    # TODO: a biiiiiiiiiit more complicated than this
    (x1, y1) = me.get_position()
    (dx, dy) = (x2 - float(x1), y2 - float(y1))
    distance = sqrt(dx * dx + dy * dy)
    if distance == 0:
        print("Already there")
        return
    (dx, dy) = (dx / distance, dy / distance)  # unit vector
    g = 1
    (dx, dy) = (dx * g * 9.81, dy * g * 9.81)
    me.set_acceleration((dx, dy))
    #if target:
    #    me.set_course_handler(adjust_flip_and_burn_course, target.key)
    #else:
    #    me.set_course_handler(adjust_flip_and_burn_course, (x2, y2))
    show(None)
    print(f"{me.get_visual()} burning {g}g for ({int(x2)}, {int(y2)})")

def set_course(match):
    me = get_craft(match.group(1))
    x2 = float(match.group(2))
    y2 = float(match.group(3))
    set_course_helper(me, x2, y2)

def set_course_target(match):
    me = get_craft(match.group(1))
    target = get_craft(match.group(2))
    (x2, y2) = target.get_position()
    set_course_helper(me, x2, y2, target)

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

def distance(a, b):
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
    dist = distance(pos1, pos2)
    if False:
        print("time:", time, "pos1:", pos1, "pos2:", pos2, "dist:", dist)
    pos1a = me.get_position(time + 1)
    pos2a = target.get_position(time + 1)
    dist1 = distance(pos1a, pos2a)
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
    global center, autocenter
    craft = get_craft(match.group(1))
    if craft:
       center = craft.position
       autocenter = "x" if craft.key == "x" else None
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
    (ddx, ddy) = (dx * g * 9.81, dy * g * 9.81)
    me.set_acceleration((ddx, ddy))
    me.set_course_handler(None)
    show(None)
    what = "burning" if g > 0 else "braking"
    print(f"{me.get_visual()}: {what} {abs(g)}g")

def set_position(match):
    craft = get_craft(match.group(1))
    if not craft:
        return
    craft.set_position((float(match.group(2)), float(match.group(3))))
    show(None)

def set_velocity(match):
    craft = get_craft(match.group(1))
    if not craft:
        return
    craft.set_velocity((float(match.group(2)), float(match.group(3))))
    show(None)

def format_distance(dist):
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

def distance_as_text(me, target):
    return format_distance(int(round(distance(me.get_position(0), target.get_position(0)))))

def show_distance(match):
    me = get_craft(match.group(1))
    target = get_craft(match.group(2))
    if me is None or target is None:
        return
    print(f"distance from {me.get_visual()} to {target.get_visual()}: {distance_as_text(me, target)}")

def view_craft_from_file(match):
    if match.group(1) == "":
        print("View a movie or ...?")
        return
    target = get_craft(match.group(1))
    if target and target.image:
        options = "-f -g" if isinstance(target, Star) else "-g"  # -f full screen
        os.system(f"eog {options} ships/{target.image}") # -g disable gallery
    else:
        print("You see nothing special.")

def add_craft(match):
    global crafts
    key = match.group(1)
    name = match.group(2)
    if key in crafts:
        print(f"There can only be one {crafts[key].get_visual()}")
        return
    craft = make_craft(crafts, name, key)
    if craft:
        crafts[key] = craft
        min_x = int(min([craft.position[0] for craft in crafts.values()]))
        max_x = int(max([craft.position[0] for craft in crafts.values()]))
        min_y = int(min([craft.position[1] for craft in crafts.values()]))
        max_y = int(max([craft.position[1] for craft in crafts.values()]))
        craft.set_position((randint(min_x, max_x), randint(min_y, max_y)))
        show(None)
        print(f"{craft.get_visual()} appears in a puff of matter")

def remove_craft(match):
    global crafts
    craft = get_craft(match.group(1))
    if craft:
        visual = craft.get_visual()
        [ other.set_course_handler(None) for other in crafts.values() if other.target == craft.key ]
        del crafts[craft.key]
        show(None)
        print(f"{visual} disappears in a puff of antimatter")

def fire_torpedo(match):
    global generic_torpedo
    me = get_craft(match.group(1))
    target = get_craft(match.group(2))
    if me is None or target is None:
        return
    torpedo = deepcopy(generic_torpedo)
    key = generate_unique_key(crafts, "0")
    torpedo.set_key(key)
    torpedo.set_visual(key)
    torpedo.set_ident("Torpedo " + key)
    torpedo.set_position(me.get_position())
    torpedo.set_velocity(me.get_velocity(0))
    torpedo.show_trajectory = False
    torpedo.target = target
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
    missile.target = target
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
    global simulated_time, center, autocenter
    interception = False
    for _ in range(0, seconds):
        [craft.tick(1) for craft in crafts.values()]
        simulated_time += datetime.timedelta(seconds=1)
        check = [(c1, c2) for c1 in crafts.values() for c2 in crafts.values() if
                 c1 != c2 and distance(c1.get_position(), c2.get_position()) < 100]
        for (craft1, craft2) in check:
            if (isinstance(craft1, Craft) and isinstance(craft2, Craft)) or (
                    isinstance(craft1, Weapon) and craft1.target == craft2):
                interception = True
                interceptions_to_be_resolved.add(tuple(sorted((craft1.key, craft2.key))))
        if interception:
            break
    [craft.adjust_course() for craft in crafts.values()]
    if autocenter:
        center_object = get_craft(autocenter)
        if center_object:
            center = center_object.get_position()
        else:
            autocenter = None
    show(None)
    return interception

def tick_handler(match):
    global prompt, tick_on_return
    if match.group(1) != "":
        tick_on_return = int(match.group(1))
    if tick_on_return > 1:
        prompt = f". Hit <return> for another 'tick {tick_on_return}'> "
    else:
        prompt = "> "
    # tick(tick_on_return if match.group(1) == "" else int(match.group(1)))
    tick(tick_on_return)

def fast_forward(step):
    global is_running, simulated_time, crafts
    is_running = True
    while is_running:
        simulated_time += datetime.timedelta(seconds=step)
        set_day(crafts, simulated_time.timestamp() // 86400)
        [craft.tick(step) for craft in crafts.values()]
        print_prompt()
        sys.stdout.flush()
        time.sleep(0.1)
        show(None)
    save(None)

def run(match):
    global is_running
    step = int(match.group(1)) if match.group(1) != "" else 1
    if step > 100:
        fast_forward(step)
        return
    is_running = True
    while is_running:
        if tick(step):
            is_running = False
            break
        print_prompt()
        sys.stdout.flush()
        time.sleep(0.5)
        show(None)
    save(None)

# noinspection PyBroadException
def save(match, quiet=False):
    global savefile, next_save, save_frequency
    filename = "save/" + (match.group(1) if match and match.group(1) != "" else savefile)
    if filename[-7:] != ".pickle":
        filename = filename + ".pickle"
    try:
        with open(filename, "wb") as file:
            crafts_copy = copy.deepcopy(crafts)
            pickle.dump(crafts_copy, file)
        if not quiet:
            print("Saved", filename)
        next_save = time.time() + save_frequency
        return True
    except:
        print(f"Error save to {filename}")
        return False

def load_pickle(filename):
    global savefile, crafts
    filename = "save/" + (match.group(1) if match and match.group(1) != "" else savefile)
    if filename[-7:] != ".pickle":
        filename = filename + ".pickle"
    try:
        with open(filename, "rb") as file:
            crafts.update(pickle.load(file))
        show(None)
        print("Loaded", filename)
    except:
        print(f"Error loading {filename}")

def load_text(match):
    global crafts
    expr = r"[0-9Kkm\s.AU\+\-\*\/]+"
    ident = r"[A-Za-z0-9_\*\+\.]+"
    num = r"[0-9.]+"
    filename = "crafts/" + (match if type(match) == str else match.group(1))
    craftz = []
    stars = []
    try:
        with open(filename, "r") as file:
            for line in file:
                # Star * Sun (0, 0) (0, 0) RED 696
                match = re.match(rf"Star\s+({ident})\s+({ident})\s+\(({expr}),\s+({expr})\)\s+\(({expr}),\s+({expr})\)\s+({ident})\s+({num})\s+({ident})", line)
                if match:
                    stars.append(match.groups())
                match = re.match(r"Planet\s+([A-Za-z0-9]+)\s+([A-Za-z0-9]+)\s+([0-9.]+)\s+([A-Z_]+)\s+([0-9]+)", line)
                if match:
                    # orbit is hard-coded in craft.py
                    (key, name, dist, colour, orbit) = match.groups()
                    crafts[key] = Planet(name, (float(dist) * AU, 0), (0, 0), eval(colour), key, key, None, None)
                    continue
                # Craft B Behemoth  (21.2 * AU + 1000000, 600000) (0, 0) RED 2
                match = re.match(rf"Craft\s+({ident})\s+({ident})\s+\(({expr}),\s+({expr})\)\s+\(({expr}),\s+({expr})\)\s+({ident})+\s({num})", line)
                if match:
                    craftz.append(match.groups())
    except FileNotFoundError:
        print(f"{filename} not found")
        return
    for (key, name, x, y, dx, dy, colour, size, image) in stars:
        crafts[key] = Star(name, (eval(x), eval(y)), (eval(dx), eval(dy)), eval(colour), key, key, image, None)
    for (key, name, x, y, dx, dy, colour, max_g) in craftz:
        craft = make_craft(crafts, name, key, colour)
        x = x.replace("K", "*1000").replace("km", "* 1000")
        y = y.replace("K", "*1000").replace("km", "* 1000")
        craft.set_position((eval(x), eval(y)))  # TODO: catch error
        craft.set_velocity((eval(dx), eval(dy)))
        craft.colour = eval(colour)
        crafts[craft.key] = craft

def clear(match):
    global crafts
    if save(None, quiet=False):
        crafts = dict()
        show(None)
        print("The world disappears in a magic puff of purple smoke")
    else:
        print("Could not delete the world")

def do_password():
    global locked
    locked = True
    print("Enter password to unlock: ", end="")
    sys.stdout.flush()
    for line in sys.stdin:
        if line.strip() == "password":
            break
        print("Enter password to unlock: ", end="")
        sys.stdout.flush()
    locked = False

def save_and_exit():
    save(None)
    print("Bye.")
    sys.exit()

error_msgs = (
    "I am sorry Dave, I cannot do that.",
    "Segmentation fault (warp core dumped).",
    "Silly.",
    "Shall we play a game?",
    "You will disarm all your weapons and escort us to Sector 001, where we will begin assimilating your culture and technology.",
    "Does not compute. Destory Robinson family."
)

# huba = [ "view", "info", "trajectory", "remove", "intercept <target>", "burn <direction>", "burn <n>g", "brake <n>g",
#         "position <pair>", "velocity <pair>", "distance <target>", "torpedo <target>", "missile <target>" ]

hide = [".*"]

commands = (
    (r"show", show),
    (r"scale ([0-9]+)", set_scale),
    (r"center ([a-zA-Z0-9\*])+", set_center),
    (r"add ([a-zA-Z0-9]) ([a-zA-Z0-9]+)", add_craft),
    (r"tac[tical]*", lambda _: set_scale_and_center(tactical_scale, "x")),
    (r"nav[igation]*", lambda _: set_scale_and_center(navigation_scale, "*")),
    (r"resolved", resolved),
    (r"save[ ]*([a-zA-Z0-9\.\-]*)", save),
    (r"load[ ]*([a-zA-Z0-9\.\-]*)", load_text),
    (r"unp[ickle]*[ ]*([a-zA-Z0-9\.\-]*)", load_pickle),
    (r"clear", clear),
    (r"tick[ ]*(\-?[0-9]*)", tick_handler),
    (r"run[ ]*([0-9]*)", run),
    (r"([\+]+)", zoom),
    (r"([\-]+)", zoom),
    (r"error", lambda _: 1 // 0),
    (f"ls", lambda m: os.system("ls -F ships craftsG528672")),
    (f"ships", lambda m: os.system("ls -F ships")),
    (f"who", lambda m: os.system("who")),
    (r"reset", reset_view),
    (r"su", lambda _: lock(5)),
    (r"\?", lambda _: print("\n".join([command for (command, _) in commands if command not in hide]))),
    (r"moria", lambda _: print("Sorry, games are not allowed right now.")),
    (r"scan", lambda _: print("You see nothing special.")),
    (r"info ([a-zA-Z0-9]+)", info),
    (r"remove ([a-zA-Z0-9]+)", remove_craft),
    (r"view ([A-Za-z0-9\*\+]+)", view_craft_from_file),
    (r"lock", lambda _: do_password()),
    (r"exit", lambda _: save_and_exit()),
    (r"quit", lambda _: save_and_exit()),
    (r"([a-zA-Z0-9]*):?[ ]*time ([a-zA-Z0-9]+)", show_interception_time),
    (r"([a-zA-Z0-9]*):?[ ]*traj[ectory]*", toggle_trajectory),
    (r"([a-zA-Z0-9]*):?[ ]*remove", remove_craft),
    (r"([a-zA-Z0-9]*):?[ ]*view", view_craft_from_file),
    (r"([a-zA-Z0-9]*):?[ ]*inter[cept]* ([a-zA-Z0-9]+)", lambda m: set_interception_course(m.group(1), m.group(2))),
    (r"([a-zA-Z0-9]*):?[ ]*course ([a-zA-Z0-9]+)", set_course_target),
    (r"([a-zA-Z0-9]*):?[ ]*course \(*([0-9\.\-]+)[, ]*([0-9\.\-]+)\)*", set_course),
    (r"([a-zA-Z0-9]*):?[ ]*burn \(*([0-9\.\-]+)[, ]*([0-9\.\-]+)\)+", set_burn),
    (r"([a-zA-Z0-9]*):?[ ]*(burn) ([0-9\.\-]+)[g]", burn_brake_Xg),
    (r"([a-zA-Z0-9]*):?[ ]*(brake) ([0-9\.]+)[g]", burn_brake_Xg),
    (r"([a-zA-Z0-9]*):?[ ]*pos[ition]* \(*([0-9\.\-]+)[, ]*([0-9\.\-]+)\)*", set_position),
    (r"([a-zA-Z0-9]*):?[ ]*vel[ocity]* \(*([0-9\.\-]+)[, ]*([0-9\.\-]+)\)*", set_velocity),
    (r"([a-zA-Z0-9]*):?[ ]*dist[ance]* ([A-Za-z0-9]+)", show_distance),
    (r"([a-zA-Z0-9]*):?[ ]*torp[edo]* ([A-Za-z0-9]+)", fire_torpedo),
    (r"([a-zA-Z0-9]*):?[ ]*mis[sile]* ([A-Za-z0-9]+)", fire_missile),
    (r".*", lambda _: print(error_msgs[random.randint(1, len(error_msgs) - 1) if random.randint(0, 10) == 0 else 0])),
)

def print_prompt():
    global prompt
    print(simulated_time.strftime("%Y-%m-%d %H:%M:%S") + prompt, end="")

def sigint_handler(signum, frame):
    global is_running
    if is_running:
        is_running = False
        return
    if locked:
        print()
        return
    if exit_on_ctrl_c:
        print(LIGHT_WHITE)
        print("Bye")
        sys.exit(1)
    else:
        print("\nUse 'exit' to quit.")

def dotdotdot(text, pause):
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
    do_password()

def generic_error(e):
    traceback.print_exc()
    if show_lock_sequence_on_generic_error:
        save(None, quiet=False)
        print()
        time.sleep(5)
        lock(5)
    elif exit_on_error:
        sys.exit()
    else:
        return

load_text("planets") # hack to avoid overlapping keys (planets/stars) does not check
signal.signal(signal.SIGINT, sigint_handler)
reset_view(None)
show(None)
print_prompt()
sys.stdout.flush()

while True:
    for line in sys.stdin:
        if line == "\n":
            tick(tick_on_return)
            show(None)
            if time.time() >= next_save:
                save(None)
        else:
            for (regexp, action) in commands:
                match = re.match(regexp, line)
                if match:
                    try:
                        if "tick" not in line: # ugly
                            tick_on_return = 1
                            prompt = "> "
                        action(match)
                    except Exception as e:
                        generic_error(e)
                    break
        print_prompt()
        sys.stdout.flush()
    print("\nUse 'exit' to quit.")

# make stuff for game session
# course still not nice (must flip-and-burn) and correct for moving target [max speed]
#
# hidden crafts
# max g as param to intercept command / max speed to intercept command / end-speed at intercept
# Gate size (and other objects)
# inside the ring space / slow zone
# test
# make it easier to program
# -----------------------------------------------------------------------
# clean up keys for load_text (planets and stars overrides)
# only show "crafts" in view / tac list
# font with aspect ratio 1
# save word to text file
# add images for planets & sun
# hide crafts from navigation view? toggle planets / toggle etc
# torpedo/missile factories
# unit conversion for all output (acc, center, ...)
# General conversion of units: m, km, 42K km, 42M km, AU (1.496e+11 = 149.600.000 km ~ 150 km) [return as (N, "K")]
# init script
# load/save: narrow exception
# store time in file
# brake/burn Xg with -/+ degrees
# ======= RING ==========
# Ring station
# 1373 gates
# roughly 1M km i diameter
# fun sequences by specification (error, boot, ...)
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
# don't clear screen when updating (no problem: does not flicker)
# craft: stock of torpedoes, counter missiles
# Incorporate resolution rolls for torpedo impact, counter missiles (and PDCs)
# cancel interception course after reaching target?
# slow down when closing in on target to avoid overshooting [less relevant for torps]
# ANSI to move cursor about and lots more
# show "*" interception points
# X: lay course: flip/and/burn, patrol A-B-C, orbit Y, intercept Y
# how many dots to print in a traj?
# let craft decide what to show in overview (will always allow hiding stuff)
# -----------------------------------------------------------------------
# strain warning
# astroid, debris
# exhaust bloom
# repeat scale+/- until interupted  / autoscale
# EW(?) / Sensor detection
# scan
# command editing, history
# visualize stuff outside map
# voice commands
# boot sequence
# client-server / web view