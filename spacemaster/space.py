from common import *
from craft import *

simulated_time = datetime.datetime.now() + datetime.timedelta(2000)
interceptions_to_be_resolved = set()
crafts = dict()
prompt = scale = center = None
is_running = False
savefile = "space-" + str(int(time.time())) + ".pickle"
save_frequency = 10
next_save = time.time() + save_frequency
locked = False
show_lock_sequence_on_generic_error = True
tactical_scale = 2000000
navigation_scale = AU // 10
exit_on_ctrl_c = False
inside_ring = False
exit_on_error = False
autocenter = None

def reset_view(match):
    global crafts, prompt, scale, center
    prompt = "> "
    # scale = tactical_scale
    # center = (21.2 * AU, 0)  # gate
    scale = navigation_scale
    center = (0, 0)
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
    out += f"{get_time_text()}   Center {autocenter if autocenter else center}   Scale # = {format_distance(scale)}\n"
    me = get_craft("x")
    if me is None:
        out += "\n"
        return out
    for (dict_key, craft) in crafts.items():
        if dict_key != "x":
            if scale < AU / 1000 and (isinstance(craft, Planet) or isinstance(craft, Star)):
                continue
            if scale > AU / 1000 and (isinstance(craft, Craft) or isinstance(craft, Weapon)):
                continue
        visual = craft.get_visual() if len(dict_key) == 1 else dict_key # hack
        speed = craft.get_speed()
        unit = "m/s"
        if speed > 1000:
            speed = speed / 1000
            unit = "km/s"
        speed = f"{speed:.0f} {unit}"
        (ddx, ddy) = craft.get_acceleration()
        acc = sqrt(ddx * ddx + ddy * ddy)
        out += f"{visual}: {craft.ident:<16} {speed:>15} {acc/9.81:>3.0f} g"
        if craft != me:
            out += f"  {distance_as_text(me, craft):>10}"
            time = get_interception_time(me, craft)
            if time:
                out += f"  tti={time}s"
            if distance(me.get_position(), craft.get_position()) <= 1000000: # 1000 km
                out += RED + BLINK + "  PROXIMITY ALERT" + DEFAULT_COLOUR
        out += "\n"
    out += RED + "\n".join([f"Resolve interception between {c1} and {c2}" for (c1, c2) in interceptions_to_be_resolved]) + DEFAULT_COLOUR
    return out

def show(match):
    global scale, center
    view_text = make_view_text(crafts)
    center_xy = center
    try:
        (columns, lines) = os.get_terminal_size()
    except OSError:
        (columns, lines) = (80, 10)
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
        me.set_course_handler(None, None)
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
        print(f"{me.get_visual()} intercepts {target.get_visual()} in {time} seconds at speed {me.get_speed(time)} m/s")
    else:
        print(f"{me.get_visual()} will not intercept {target.get_visual()}")

def show_projection(match):
    me = get_craft(match.group(1))
    time = int(match.group(2))
    if me is None:
        return
    print(f"In {time} seconds {me.visual} will be at {me.get_position(time)} at speed {me.get_speed(time)} m/s")

def flip_and_burn(match):
    me = get_craft(match.group(1))
    target = get_craft(match.group(2))
    if me is None or target is None:
        return
    dist = distance(me.get_position(), target.get_position())
    time = sqrt(dist / 9.81) * 2
    print(f"Distance from {me.visual} to {target.visual} is {format_distance(dist)}. Flip-and-burn at 1g takes {format_time(time, short=False)} seconds assuming start and velocity is 0 m/s.")

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

def set_center_coords(match):
    global center
    center = tuple(map(int, match.groups()))
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

def set_relative_position(match):
    craft = get_craft(match.group(1))
    target = get_craft(match.group(2))
    if not craft or not target:
        return
    rad = math.radians(int(match.group(3)))
    try:
        dist = eval(match.group(4).replace("M", "* 1000000").replace("K", "* 1000").replace("km", "* 1000"))
    except:
        print(f"Unable to evaluate: {match.group(4)}")
        return
    (x, y) = target.get_position()
    (x1, y1) = (round(x + math.sin(rad) * dist), round(y + math.cos(rad) * dist))
    craft.set_position((x1, y1))
    show(None)
    print(f"{craft.visual}: setting position to ({x1}, {y1})")

def set_velocity(match):
    craft = get_craft(match.group(1))
    if not craft:
        return
    craft.set_velocity((float(match.group(2)), float(match.group(3))))
    show(None)

def format_time(time, short=True):
    second = (1, "s", "second")
    minute = (60, "m", "minute")
    hour = (3600, "h", "hour")
    day = (24 * 3000, "d", "day")
    month = (30 * day[0], "m", "month")
    year = (12 * month[0], "y", "year")
    for (x, short_unit, long_unit) in (year, month, day, hour, minute, second):
        if time >= x:
            break
    n = time / x
    if n < 10:
        number = f"{n:,.1f}"
        if number[-1] == "0":
            number = f"{n:,.0f}"
    else:
        number = f"{n:,.0f}"
    if short:
        out = number + " " + short_unit
    else:
        out = number + " " + long_unit + ("s" if number != "1" else "")
    return out

def format_distance(dist):
    if dist * 10  >= AU:
        dist = dist / AU
        unit = " AU"
    else:
        unit = " m"
        if dist >= 1000:
            dist = dist / 1000
            unit = " km"
        if dist >= 1000:
            dist = dist / 1000
            unit = "K km"
        if dist >= 1000:
            dist = dist / 1000
            unit = "M km"
    number = f"{dist:,.1f}"
    if number[-1] == "0":
        number = f"{dist:,.0f}"
    return number + unit

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

def toggle_ring(match):
    global scale, center, inside_ring
    if match.group(1) == "ding":
        inside_ring = not inside_ring
        if inside_ring:
            scale = 33 * 1000 * 1000
            center = (0, 0)
        else:
            set_scale_and_center(navigation_scale, "*")
        show(None)

def do_eval(match):
    if match.group(1) == "":
        print("Nothing to evaluate")
        return
    try:
        x = eval(match.group(1))
        print(f"Result: {x}")
    except:
        traceback.print_exc()

def do_system_command(match):
    if match.group(1) == "":
        print("No command")
        return
    if "rm" in match.group(1):
        print("I dont think so!")
        return
    try:
        os.system(match.group(1))
    except:
        traceback.print_exc()

def tick(seconds):
    global simulated_time, center, autocenter
    interception = False
    crafts_to_check = [ craft for craft in crafts.values() if isinstance(craft, Craft) or isinstance(craft, Weapon) ]
    pairs = [ (c1, c2) for c1 in crafts_to_check for c2 in crafts_to_check if c1 != c2 ]
    pairs = [ (c1, c2) for (c1, c2) in pairs if (isinstance(c1, Craft) and isinstance(c2, Craft)) or (isinstance(c1, Weapon) and c1.target == c2) ]
    for _ in range(0, seconds):
        [craft.tick(1) for craft in crafts.values()]
        simulated_time += datetime.timedelta(seconds=1)
        for (c1, c2) in pairs:
            if distance(c1.get_position(), c2.get_position()) < 100:
                interception = True
                interceptions_to_be_resolved.add(tuple(sorted((c1.key, c2.key))))
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
    tick(1 if match.group(1) == "" else int(match.group(1)))

def fast_forward(match):
    global is_running, simulated_time, crafts
    try:
        total = eval(match.group(1).replace("d", "* 24 * 3600").replace("h", "* 3600").replace("m", "* 60"))
        step = eval(match.group(2).replace("d", "* 24 * 3600").replace("h", "* 3600").replace("m", "* 60"))
    except:
        print("usage: ff <time> <time>, where <time> = <num>[dhm]")
        return
    is_running = True
    while is_running and total > 0:
        simulated_time += datetime.timedelta(seconds=step)
        total -= step
        set_day(crafts, simulated_time.timestamp() // 86400)
        [craft.tick(step) for craft in crafts.values()]
        show(None)
        time.sleep(0.1)
    save(None)

def run(match):
    global is_running
    step = int(match.group(1)) if match.group(1) != "" else 1
    if step > 100:
        print("Too big a step, try fast forward (ff total step) instead.")
        return
    is_running = True
    while is_running:
        if tick(step):
            is_running = False
            break
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

def load_text(match, exit_on_duplicates=False):
    global crafts
    expr = r"[0-9Kkm\s.AU\+\-\*\/]+"
    ident = r"[A-Za-z0-9_\*\+\.]+"
    num = r"[0-9.]+"
    filename = "crafts/" + (match if type(match) == str else match.group(1))
    craftz = []
    stars = []
    duplicates = False
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
        if key in crafts:
            print(f"{crafts[key].visual} already exists")
            duplicates = True
            continue
        crafts[key] = Star(name, (eval(x), eval(y)), (eval(dx), eval(dy)), eval(colour), key, key, image, None)
    for (key, name, x, y, dx, dy, colour, max_g) in craftz:
        if key in crafts:
            print(f"{crafts[key].visual} already exists")
            duplicates = True
            continue
        craft = make_craft(crafts, name, key, colour)
        x = x.replace("K", "*1000").replace("km", "* 1000")
        y = y.replace("K", "*1000").replace("km", "* 1000")
        craft.set_position((eval(x), eval(y)))  # TODO: catch error
        craft.set_velocity((eval(dx), eval(dy)))
        craft.colour = eval(colour)
        craft.max_g = float(max_g)
        crafts[craft.key] = craft
    if duplicates: # for startup testing
        if exit_on_duplicates:
            sys.exit(1)
        else:
            time.sleep(1)
    show(None)

def clear(match):
    global crafts
    if save(None, quiet=False):
        crafts = dict()
        show(None)
        print("The world disappears in a puff of purple haze")
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
    "Does not compute. Destory Robinson family.",
    "Look into my eye."
)

who = """
sloane      tty7         2030-08-14 09:01 (:0)
tjubangwoof pts/0        2030-08-14 09:17 (:0)
david       pts/1        2030-08-14 08:59 (:0)
arthur?     pts/2        2030-08-14 09:17 (:0)
avatar      cargo/1      2025-01-05 23:59 (:0)
"""[1:-1]

hide = [ ".*", "\?(.*)", ":(.*)", "ring" ]

print_help =  lambda _: print("\n".join([command for (command, _) in commands if command not in hide]))

commands = (
    (r"show", show),
    (r"scale ([0-9]+)", set_scale),
    (r"center ([a-zA-Z0-9\*])+", set_center),
    (r"center \(*([0-9\.\-]+)[, ]*([0-9\.\-]+)\)*", set_center_coords),
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
    (r"ff\s+([0-9hdm]+)\s+([0-9hdm]+)", fast_forward),
    (r"([\+]+)", zoom),
    (r"([\-]+)", zoom),
    (r"error$", lambda _: 1 // 0),
    (f"ships$", lambda m: os.system("ls -F ships")),
    (f"who$", lambda _: print(who)),
    (r"reset_view$", reset_view),
    (r"su$", lambda _: lock(5)),
    (r"help$", print_help),
    (r"^\?$", print_help),
    (r"mori$a", lambda _: print("Sorry, games are not allowed right now.")),
    (r"scan$", lambda _: print("You see nothing special.")),
    (r"info ([a-zA-Z0-9]+)", info),
    (r"remove ([a-zA-Z0-9]+)", remove_craft),
    (r"view ([A-Za-z0-9\*\+]+)", view_craft_from_file),
    (r"ring\s+(.*)", toggle_ring),
    (r"lock$", lambda _: do_password()),
    (r"exit$", lambda _: save_and_exit()),
    (r"quit$", lambda _: save_and_exit()),
    (r"([a-zA-Z0-9]*):?[ ]*flip[andburn\-]*\s+([A-Za-z0-9\*\+]+)", flip_and_burn),
    (r"([a-zA-Z0-9]*):?[ ]*pro[ject]*\s+([0-9]+)", show_projection),
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
    (r"([a-zA-Z0-9]*):?[ ]*pos[ition]* ([a-zA-Z0-9\+\*]+)\s+([0-9]+)\s+([0-9\+\-KMkm\s]+)", set_relative_position),
    (r"([a-zA-Z0-9]*):?[ ]*vel[ocity]* \(*([0-9\.\-]+)[, ]*([0-9\.\-]+)\)*", set_velocity),
    (r"([a-zA-Z0-9]*):?[ ]*dist[ance]* ([A-Za-z0-9]+)", show_distance),
    (r"([a-zA-Z0-9]*):?[ ]*torp[edo]* ([A-Za-z0-9]+)", fire_torpedo),
    (r"([a-zA-Z0-9]*):?[ ]*mis[sile]* ([A-Za-z0-9]+)", fire_missile),
    (r"\?(.*)", do_eval),
    (r":(.*)", do_system_command),
    (r".*", lambda _: print(error_msgs[random.randint(1, len(error_msgs) - 1) if random.randint(0, 10) == 0 else 0])),
)


def get_time_text():
    return simulated_time.strftime("%Y-%m-%d %H:%M:%S")

def print_prompt():
    global prompt
    print(prompt, end="")
    # print(simulated_time.strftime("%Y-%m-%d %H:%M:%S") + prompt, end="")

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

def command_loop():
    while True:
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
            if time.time() >= next_save:
                save(None)
            print_prompt()
            sys.stdout.flush()
        print('\nUse "exit" to leave the world.')

reset_view(None)
signal.signal(signal.SIGINT, sigint_handler)
load_text("planets", True) # hacK: load first to avoid overlapping keys (planets/stars) does not check
# load_text("mcrn", True)
reset_view(None) # hack to update planet updates
scale = 0.7 * AU
show(None)
print_prompt()
sys.stdout.flush()

while True:
    try:
        command_loop()
    except Exception as e:
        generic_error(e)

# make stuff for game session
# adjust traj for scale
# inside the ring space / slow zone
#
# does "pos z 1 AU" actually work?
# -----------------------------------------------------------------------
# ======= RING ==========
# Ring station
# 1373 gates
# roughly 1M km i diameter
# https://expanse.fandom.com/wiki/Ring_Entities
# change reality when passing through gate!
# sensor flickers when in ring space
# max speed
# unit interpretation of input
# fun use of ANSI codes
# max g as param to intercept command / max speed to intercept command / end-speed at intercept
# lay course (must flip-and-burn) and correct for moving target [max speed in ring (otherwise speed of light)], time XXX should show speed a time XXX
# Gate size (and other objects)
# only show "crafts" in view / tac list
# save word to text file
# add images for planets & sun
# hide crafts from navigation view? toggle planets / toggle etc
# unit conversion for all output (acc, center, ...)
# init script
# load/save: narrow exception
# store time in file
# brake/burn Xg with -/+ degrees
# font with aspect ratio 1
# torpedo/missile factories
# fun sequences by specification (error, boot, ...)
# hidden crafts / planets / other
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