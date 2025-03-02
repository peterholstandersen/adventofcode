from common import *
from utils import *
import universe as u
import view as v

def interpret_distance(number, prefix, unit):
    number = float(number)
    if prefix == "K": number = number * 1000
    if prefix == "M": number = number * 1e+06
    if unit == "AU": number = number * AU
    if unit == "ly": number = number * LIGHT_YEAR
    return str(f"{number:.0f}")

IDENT = r"([a-zA-Z0-9_*+]+)"
NUMBER = r"([+-]?[0-9]+\.?[0-9]*)"
UNIT = r"(K|M|)\s*(ly|AU|km|)"

COORDS = rf"\(?{NUMBER}\s*,\s*{NUMBER}\)?"
ABS_POS = rf"(?:{IDENT}|{COORDS})"
REL_POS1 = rf"(?:rel\s*{COORDS})"
REL_POS2 = rf"(?:rel\s*{NUMBER}\s*d\s*{NUMBER})"
REL_POS = rf"(?:{REL_POS1}|{REL_POS2})"

class Command(cmd.Cmd):
    universe = None
    view = None
    msg = None
    show = None

    def __init__(self, universe, view, *args):
        self.universe = universe
        self.view = view
        super().__init__(*args)

    intro = "Hello Universe. Type help or ? to list commands."
    prompt = '> '

    def do_show(self, arg):
        self.view.show(self.universe)

    def do_scale(self, arg):
        """usage: scale <positive number>"""
        n = safe_float(arg)
        if n is None or n <= 0:
            self.msg = self.do_scale.__doc__
        else:
            view.scale = round(n)
            self.msg = f"Scale set to {view.scale} km"

    def do_zoom(self, arg):
        if len(arg) > 0 and (all([char == "+" for char in arg]) or all([char == "-" for char in arg])):
            n = len(arg)
            factor = max(50 - n * 10, 10) / 100
            factor = pow(factor, n)
            scale = view.scale * factor if arg[0] == "+" else view.scale / factor
            view.scale = max(round(scale), 1)
            self.msg = f"Scale set to {view.scale} km"
        else:
            self.msg = f"usage: zoom followed by any number of plusses (+) or minusses (-). For example, zoom +++"

    def do_enhance(self, arg):
        """usage: enhance <positive number>"""
        n = safe_float(arg)
        if n is None or n <= 0:
            self.msg = self.do_enhance.__doc__
        else:
            view.enhance = round(n)
            self.msg = f"Enhancement set to {view.enhance}"

    def do_center(self, arg):
        """
Center the view at a particular point in space. It may be specified as coordinates or a particular space object (target).
Optionally, use "rel" to set the viewing center to a position relative to a fixed position. The viewing center will
stay fixed even as the space objects move. Use the 'track' command to keep a specific object at the center of the view.

center <absolute_pos> [ rel <relative_pos> ]
<absolute_pos> = <coords> or <target>
<relative_pos> = <coords>
<relative_pos> = <angle> d <distance>

Examples:
    center (100M, 100M)               # (100 million km, 100 million km)
    center *                          # center view at the space object *
    center * rel (1 AU, -2 AU)        # center view at (1 AU, -2 AU) relative to *
    center D rel (100K, 100K)         # center view at (100.000 km, 100.000 km) relative to D
        """
        # ident, x, and y specifies the absolute position
        # center A   => ident=A, x=None, y=None
        # center 1,2 => ident=None, x=1, y=2
        #
        # dx, dy, degrees and dist specifies a relative position (if any)
        # center A rel (1,2)  => dx=1, dy=2, degrees=None, dist=None
        # center A rel 10d 20 => dx=None, dy=None, degrees=10, dist=20
        usage = "center <absolute_pos> [ rel <relative_pos> ]"
        match = re.match(rf"{ABS_POS}\s*{REL_POS}?$", arg)
        if not match:
            self.msg = f"usage: {usage}"
            return
        ident = match.group(1)
        (x, y, dx, dy, degrees, dist) = tuple(map(safe_float, match.groups()[1:]))
        if ident is not None:
            xy = universe.get_body_position(ident)
            if not xy:
                self.msg = f"Cannot find {ident}. Usage: {usage}"
                return
            else:
                (x, y) = xy
        if dx and dy:
            (x, y) = (x + dx, y + dy)
        elif degrees and dist:
            x += sin(radians(degrees)) * dist
            y += cos(radians(degrees)) * dist
        view.track = None
        view.center = (round(x), round(y))
        self.msg = f"Center set to {view.center}"

    def do_track(self, arg):
        usage = "usage: track <space object>. For example, track J"
        if len(arg) == 0:
            self.msg = usage
        body = universe.bodies.get(arg)
        if body is None:
            self.msg = f"Cannot find {arg}. " + usage
        else:
            view.track = arg
            view.center = body.position
            self.msg = f"Tracking {body.visual}"

    def do_run(self, arg):
        usage = "usage: run <seconds>"
        step = safe_float(arg)
        if step is None:
            self.msg = usage
            return
        if universe.clock.start(datetime.timedelta(seconds=round(step)), lambda: view.show(universe)):
            self.show = False
            self.msg = "The Universe starts moving" + (". You feed like a God" if randint(1, 100) == 1 else "")
        else:
            self.show = False
            self.msg = f"Internal error: Failed to start clock. clock_thread.is_alive()={universe.clock.thread.is_alive()}"

    def do_stop(self, arg):
        if len(arg) > 0:
            self.show = False
            self.msg = "The 'stop' command does not take any arguments"
        elif universe.clock.stop():
            self.show = False
            self.msg = f"The Universe stops" +  (". You feed like a God" if randint(1, 100) == 1 else "")
        else:
            self.show = False
            self.msg = f"Internal error: Failed to stop clock. clock_thread.is_alive()={universe.clock.thread.is_alive()}"

    def do_exit(self, arg):
        """Leave the universe"""
        print("You escape the Universe")
        return True

    def emptyline(self):
        # if not defined, it will repeart the last command, we just want to do the show command (if postcmd)
        return

    def default(self, line):
        if line[0] == "+" or line[0] == "-":
            self.do_zoom(line)
        else:
            self.msg = f"Unrecognized command '{line}'. Try 'help'"

    def precmd(self, line):
        self.msg = None
        self.show = True
        aliases = { a[0:2] + " " : a for a in ["show", "scale", "enhance"] }
        if line[0:3] in aliases:
            line = aliases[line[0:3]] + " " + line[3:]
        line = line.strip().replace("(", "").replace(")", "")
        line = re.sub(rf"{NUMBER}\s*{UNIT}", lambda match: str(interpret_distance(*match.groups())) + " ", line)
        return line.strip()

    def postcmd(self, stop, line):
        if self.show and is_running_in_terminal():  # TODO: and clock is not running?
            view.show(universe)
        if self.msg:
            print(self.msg)
        return stop

# ==================================================================================================

def test_onecmd(commmand, line):
    quoted_line = "'" + line + "'"
    print(f"onecmd {quoted_line:<25} # ", end="")
    line = command.precmd(line)
    stop = command.onecmd(line)
    command.postcmd(stop, line)

def run_all_tests(command, universe, view):
    to_test = [
        ("zoom", ["+", "-", "++++", "----", ""]),
        ("scale", ["1", "2", "1.1", "1 2", "", ".", "  1  ", "-1"]),
        ("enhance", ["10", "-20", "30", "-1"]),
        ("center", ["0", "m", "m rel (1,2)", "m rel 90d 3 km", "m rel 180d 4", "m rel 270d 5", "m rel 360 d 6", "m rel 45 d 16", "1,2 rel 3,4", "xx", "(10K,10)"]),
        ("track",  ["m", "0", "", "(1,2)"])
    ]
    cmds = [ keyword + " " + arg for (keyword, args) in to_test for arg in args]

    [ test_onecmd(command, text) for text in cmds ]

if __name__ == '__main__':
    (universe, clock) = u.create_test_universe(start_thread=False)
    view = v.View((0, 0), AU // 10, 1)
    #do_run(universe, view, 10)
    #do_stop(universe, view)
    command = Command(universe, view)
    if is_running_in_terminal():
        universe.clock.start_thread()
        # command_thread = threading.Thread(target=command.cmdloop)
        # command_thread.start()
        command.cmdloop()
        print("done")
    else:
        run_all_tests(command, universe, view)
    clock.terminate()
    print("bye bye")
