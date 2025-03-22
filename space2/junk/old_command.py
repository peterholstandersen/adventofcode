from common import *
from utils import *
import universe as u
import view as v

ident = r"([a-zA-Z0-9_*+]+)"
number = r"([+-]?[0-9]+\.?[0-9]*)"

def interpret_distance(number, prefix, unit):
    number = float(number)
    if prefix == "K": number = number * 1000
    if prefix == "M": number = number * 1e+06
    if unit == "AU": number = number * AU
    if unit == "ly": number = number * LIGHT_YEAR
    return str(f"{number:.0f}")

def preprocess(line):
    unit = r"(K|M|)\s*(ly|AU|km|)"
    line = line.strip().replace("(", "").replace(")", "")
    line = re.sub(rf"{number}\s*{unit}", lambda match: str(interpret_distance(*match.groups())) + " ", line)
    return line.strip()

def do_show(universe, view):
    view.show(universe)

def do_scale(universe, view, number):
    number = round(float(number))
    if number <= 0:
        return f"Scale must be a positive number"
    view.scale = number
    return f"Scale set to {view.scale} km"

def do_zoom(universe, view, command):
    scale = view.scale
    n = len(command)
    factor = max(50 - n * 10, 10) / 100
    factor = pow(factor, n)
    scale = scale * factor if command[0] == "+" else scale / factor
    view.scale = max(round(scale), 1)
    return f"Scale set to {view.scale} km"

def do_enhance(universe, view, arg):
    n = safe_float(arg)
    if n:
        view.enhance = n
        return f"Enhancement set to {n}"
    else:
        return f"Syntax error. Try enhance <number>"

def do_center(universe, view, ident, x, y, dx, dy, degrees, dist):
    # ident, x, and y specifies the absolute position
    # center A   => ident=A, x=None, y=None
    # center 1,2 => ident=None, x=1, y=2
    #
    # dx, dy, degrees and dist specifies a relative position (if any)
    # center A rel (1,2)  => dx=1, dy=2, degrees=None, dist=None
    # center A rel 10d 20 => dx=None, dy=None, degrees=10, dist=20
    (x, y, dx, dy, degrees, dist) = tuple(map(safe_float, (x, y, dx, dy, degrees, dist)))
    if ident is not None:
        xy = universe.get_body_position(ident)
        if not xy:
            return f"Cannot find {ident}"
        else:
            (x, y) = xy
    if dx and dy:
        (x, y) = (x + dx, y + dy)
    elif degrees and dist:
        x += sin(radians(degrees)) * dist
        y -= cos(radians(degrees)) * dist
    view._track = None
    view.center = (round(x), round(y))
    return f"Center set to {view.center}"

def do_track(universe, view, ident):
    if not ident in universe.bodies:
        return f"Cannot find {ident}"
    view._track = ident
    view.center = universe[ident].position
    return f"Tracking {body.visual}"

def do_run(universe, view, step):
    step = float(step)
    if universe.clock.set_factor(datetime.timedelta(seconds=step), lambda : view.show(universe)):
        return "clock started"
    return f"fail to start clock. alive={universe.clock.thread.is_alive()}"

def do_stop(universe, view):
    if universe.clock.stop():
        return "clock stopped"
    return "failed to stop clock"

def get_commands():
    coords = rf"\(?{number}\s*,\s*{number}\)?"
    absolute_position = rf"(?:{ident}|{coords})"
    relative_position1 = rf"(?:rel\s*{coords})"
    relative_position2 = rf"(?:rel\s*{number}\s*d\s*{number})"
    relative_position = rf"(?:{relative_position1}|{relative_position2})"

    commands = (
        (r"^\s*$", do_show),
        (r"sh[ow]*", do_show),
        (rf"sc[ale]*\s+{number}$", do_scale),
        (rf"([+]+|[-]+)", do_zoom),
        (rf"en[hance]* {number}", do_enhance),
        (rf"ce[nter]*\s+{absolute_position}\s*{relative_position}?\s*$", do_center),
        (rf"tr[ack]*\s+{ident}\s*$", do_track),
        (rf"ru[n]*\s+{number}$", do_run),
        (rf"st[op]*\s*$", do_stop),
        ("exit", lambda u, v: sys.exit()),
     )
    return commands

def prompt():
    print("> ", end="")
    sys.stdout.flush()

def convert_numbers(text):
    try:
        return float(text)
    except (ValueError, TypeError):
        return text

def handle_command(universe, view, commands, line):
    # print(f"{line:<20} ", end="")
    line = preprocess(line)
    # print(f"{line:<30} ", end="")
    for (pattern, action) in commands:
        match = re.match(pattern, line)
        if match:
            return action(universe, view, *match.groups())
    print("Unknown command. Try help.")

def inner_command_loop(universe, view):
    commands = get_commands()
    while True:
        prompt()
        for line in sys.stdin:
            result = handle_command(universe, view, commands, preprocess(line))
            if result:
                view.show(universe)
                print(result)
                sys.stdout.flush()
            prompt()
        print("\nUse 'exit' to leave the universe.")

def command_loop(universe, view):
    while True:
        try:
            inner_command_loop(universe, view)
        except KeyboardInterrupt:
            print("\nUse 'exit' to leave the universe.")
        except Exception as e:
            traceback.print_exc()

# ===============================================================================================================

def run_all_tests(universe, view):
    verify(preprocess("."), ".")
    verify(preprocess("10M"), "10000000")
    verify(preprocess("(10K km, 1)"), "10000 , 1")
    commands = get_commands()
    to_test = [
        ("scale", ["42", "42.1 km", "-42.1 km", "1 AU", "1K km", "1M", "1K AU", "1ly", "1Kly", "1M  ly"]),
        ("center", ["0", "m rel 90d 1 km", "1,2 rel 3,4", "m", "xx", "1,1", "(10K,10)"]),
    ]
    cmds = [ command + " " + arg for (command, args) in to_test for arg in args]
    cmds += ["+", "-", "++", "--", "++++", "----"]
    test = lambda command: handle_command(universe, view, commands, command)
    [ print(f"{cmd:<25} # {test(cmd)}") for cmd in cmds ]

def is_running_in_terminal():
    try:
        os.get_terminal_size()
    except OSError:
        return False
    else:
        return True

if __name__ == "__main__":
    (universe, clock) = u.big_bang(start_thread=True)
    view = v.View((0, 0), AU // 10, 1)
    do_run(universe, view, 10)
    do_stop(universe, view)
    if is_running_in_terminal():
        command_loop(universe, view)
    else:
        run_all_tests(universe, view)
    clock.terminate()
