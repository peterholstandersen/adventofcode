from common import *
from utils import *
import universe as u
import view as v
import course

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
    default_craft = None
    show = None            # update the view in postcmd
    msg = None             # msg to print after updating the view in postcmd
    _aliases = None

    def __init__(self, universe, view, default_craft, *args):
        super().__init__(*args)
        self.universe = universe
        self.view = view
        self.default_craft = default_craft
        self._init_aliases()

    def _init_aliases(self):
        # Create 2 and 3 letter aliases for all commands (when unique)
        commands = [method_name[3:] for method_name in dir(Command) if method_name.startswith("do_") and method_name != "do_exit"]
        shorts2 = [command[:2] for command in commands]
        shorts3 = [command[:3] for command in commands]
        self._aliases = {command[:2] : command for command in commands if shorts2.count(command[:2]) == 1 and len(command) > 2}
        self._aliases.update({command[:3] : command for command in commands if shorts3.count(command[:3]) == 1 and len(command) > 3})

    intro = "Hello Universe. Type help or ? to list commands."
    prompt = '> '

    # Helper functions
    def _set_scale(self, scale):
        self.view.scale = round(scale)
        self.msg = f"Scale set to {v.format_distance(self.view.scale)}"

    def _complete_names(self, text, line, begidx, endidx):
        last_words = line.partition(' ')[2]     # all words after the first space
        offset = len(last_words) - len(text)
        return [name[offset:] for name in self.universe.bodies if name.startswith(last_words)]

    def _get_body(self, arg):
        candidates = self.universe.find_bodies(arg)
        if len(candidates) == 0:
            self.msg = f"Cannot find {arg}."
            return None
        elif len(candidates) == 1:
            return candidates[0]
        else:
            if len(candidates) == 2:
                text = candidates[0].name + " or " + candidates[1].name
            else:
                names = [body.name + ", " for body in candidates]
                text = ("".join(names[:-1])) + "or " + candidates[-1].name
            self.msg = "Did you mean " + text + "?"
            self.show = False
            return None

    def _parse_position(self, arg, usage):
        # ident, x, and y specifies the absolute position
        # center A   => ident=A, x=None, y=None
        # center 1,2 => ident=None, x=1, y=2
        #
        # dx, dy, degrees and dist specifies a relative position (if any)
        # center A rel (1,2)  => dx=1, dy=2, degrees=None, dist=None
        # center A rel 10d 20 => dx=None, dy=None, degrees=10, dist=20
        match = re.match(rf"{ABS_POS}\s*{REL_POS}?", arg)
        if not match:
            self.msg = f"usage: {usage}"
            return None
        ident = match.group(1)
        (x, y, dx, dy, degrees, dist) = tuple(map(safe_float, match.groups()[1:]))
        if ident is not None:
            body = self._get_body(ident)
            if not body:
                return None
            (x ,y) = body.position
        if dx and dy:
            (x, y) = (x + dx, y + dy)
        elif degrees and dist:
            x += sin(radians(degrees)) * dist
            y += cos(radians(degrees)) * dist
        return (round(x), round(y))

    # cmd module functions for tab-completion of space object names in command arguments
    complete_center = _complete_names
    complete_track = _complete_names

    def do_reset(self, arg):
        """Reset view"""
        self.view.center = (0, 0)
        self.view.scale = 0.3 * AU
        self.view.enhance = 4

    def do_scale(self, arg):
        """Scale the view. Usage: scale <positive number>."""
        n = safe_float(arg)
        if n is None or n <= 0:
            self.msg = self.do_scale.__doc__
        else:
            self._set_scale(round(n))

    def do_zoom(self, arg):
        """
Adjust scale by zooming in or out. Type 'zoom' followed by any number of plusses (+) or minusses (-).
For example, 'zoom +++'. The keyword 'zoom' may be omitted, e.g., '++++' has the same effect as 'zoom ++++'.
        """
        if len(arg) > 0 and (all([char == "+" for char in arg]) or all([char == "-" for char in arg])):
            n = len(arg)
            factor = max(50 - n * 10, 10) / 100
            factor = pow(factor, n)
            scale = self.view.scale * factor if arg[0] == "+" else self.view.scale / factor
            self._set_scale(max(scale, 1))
        else:
            self.msg = f"usage: zoom followed by any number of plusses (+) or minusses (-). For example, zoom +++"

    def do_enhance(self, arg):
        """usage: enhance <positive number>. Make space objects appear larger."""
        n = safe_float(arg)
        if n is None or n <= 0:
            self.msg = self.do_enhance.__doc__
        else:
            self.view.enhance = round(n)
            self.msg = f"Enhancement set to {self.view.enhance}"

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
        usage = "center <absolute_pos> [ rel <relative_pos> ]"
        xy = self._parse_position(arg, usage)
        if xy is None:
            return
        self.view.track = None
        self.view.center = xy
        self.msg = f"Center set to ({v.format_distance(self.view.center[0])}, {v.format_distance(self.view.center[1])})"

    def do_course(self, arg):
        """
Usage: course <absolute_pos> [ rel <realative_pos> ] [vel[ocity] <vector>] [max] [Ng]"

Set course to a point in space. It may be specified as coordinates or a particular space object (target).
Optionally, use "rel" to set the target to a position relative to a fixed position.
Optionally, use "vel (dx,dy)" or "velocity (dx,dy)" to specificy the desired velocity when reaching the target. Defaults to (0,0).
Optionally, use "max Ng" to specificy the maximum amount of gs allowed. Defaults to 1g.

Examples:
course e rel (100,100) velocity (0,100) max 10g
course e rel (100,100) vel (0,100) 10g
        """
        self.show = False
        if self.default_craft is None:
            self.msg = "Default craft is not set"
            return
        usage = "course <absolute_pos> [ rel <realative_pos> ] [vel[ocity] <vector>] [max] [Ng]"
        if len(arg) == 0:
            self.msg = usage
            return
        end_pos = self._parse_position(arg, "Unable to determine target position. Usage: " + usage)
        if not end_pos:
            return
        start_pos = self.default_craft.position
        start_velocity = self.default_craft.velocity
        match = re.match(rf".*vel.*\s+{COORDS}.*", arg)
        end_velocity = (float(match.group(1)), float(match.group(2))) if match else (0, 0)
        match = re.match(r".*([0-9]+)\s*g.*", arg)
        max_acc = float(match.group(1)) * 9.81 if match else 9.81
        print(f"start_pos={start_pos}  end_pos={end_pos}  start_vel={start_velocity}  end_vel={end_velocity}  max_acc={max_acc} ... calculating course ...")
        new_course = course.compute_course(start_pos, end_pos, start_velocity, end_velocity, max_acc)
        if not new_course:
            print(f"Unable to plot course, sorry.")
            return
        (burn_duration, brake_duration, burn, brake) = new_course
        now = self.universe.clock.timestamp.timestamp()
        self.default_craft.course = course.BurnSequence(self.default_craft, [(now, now + burn_duration, burn), (now + burn_duration, now + burn_duration + brake_duration, brake)])
        self.msg = str(self.default_craft.course)

    def do_track(self, arg):
        """Track a space object. For example, track J"""
        usage = "usage: track <space object>"
        if len(arg) == 0:
            self.show = False
            self.msg = usage
            return
        body = self._get_body(arg)
        if body:
            self.view.track = body.name
            self.view.update_center(self.universe)
            self.msg = f"Tracking {self.view.track}"

    def do_tick(self, arg):
        """Usage: tick <seconds>. Jump forward in time. Does not start the universe clock (nor stops it)"""
        step = safe_float(arg)
        if step is None:
            self.msg = "usage: tick <seconds>"
            self.show = False
            return
        self.universe.clock.timestamp += datetime.timedelta(seconds=round(step))

    def do_run(self, arg):
        """Usage: run <seconds>. Start the universe clock in increments of <seconds>"""
        self.show = False
        usage = "usage: run <seconds>"
        step = safe_float(arg)
        if step is None:
            self.msg = usage
        elif self.universe.clock.start(datetime.timedelta(seconds=round(step)), lambda: self.view.show(self.universe)):
            self.msg = "The Universe starts moving" + (". You feel like a God" if randint(1, 100) == 1 else "")
        else:
            self.msg = f"Internal error: Failed to start clock. clock_thread.is_alive()={self.universe.clock.thread.is_alive()}"

    def do_stop(self, arg):
        """Stop the universe clock"""
        self.show = False
        if len(arg) > 0:
            self.msg = "The 'stop' command does not take any arguments"
        elif self.universe.clock.stop():
            self.msg = f"The Universe stops" +  (". You feed like a God" if randint(1, 100) == 1 else "")
        else:
            self.msg = f"Internal error: Failed to stop clock. clock_thread.is_alive()={self.universe.clock.thread.is_alive()}"

    def do_exit(self, arg):
        """Leave the universe"""
        self.show = False
        self.msg = "You escape the Universe"
        return True

    def do_help(self, arg):
        """Help yourself"""
        self.show = False
        super().do_help(arg)

    def emptyline(self):
        # if not defined, it will repeart the last command. We just want to update the view (which is handled in postcmd)
        return

    def default(self, line):
        # This method is called if the command does not match any of the defined commands.
        if line[0] == "+" or line[0] == "-":
            self.do_zoom(line)
        else:
            self.show = False
            self.msg = f"Unrecognized command '{line}'. Try 'help'"

    def precmd(self, line):
        self.msg = None
        self.show = True
        (command, _, rest) = line.partition(' ')
        if command in self._aliases:
            line = self._aliases[command] + " " + rest
        line = line.strip().replace("(", "").replace(")", "")
        line = re.sub(rf"{NUMBER}\s*{UNIT}", lambda match: str(interpret_distance(*match.groups())) + " ", line)
        return line.strip()

    def postcmd(self, stop, line):
        if self.show and is_running_in_terminal() and not self.universe.clock.is_running():
            self.view.show(self.universe)
        if self.msg:
            print(self.msg)
        return stop

# ==================================================================================================

def test_onecmd(commmand, line):
    quoted_line = "'" + line + "'"
    print(f"onecmd {quoted_line:<30} # ", end="")
    line = command.precmd(line)
    stop = command.onecmd(line)
    command.postcmd(stop, line)

def run_all_tests(command, universe, view):
    to_test = [
        ("zoom", ["+", "-", "++++", "----", ""]),
        ("scale", ["1", "2", "1.1", "1 2", "", ".", "  1  ", "-1"]),
        ("sc", ["1", "2"]),
        ("sca", ["1", "2"]),
        ("enhance", ["10", "-20", "30", "-1"]),
        ("center", ["v", "0", "m", "m rel (1,2)", "m rel 90d 3 km", "m rel 180d 4", "m rel 270d 5", "m rel 360 d 6", "m rel 45 d 16", "1,2 rel 3,4", "xx", "(10K,10)"]),
        ("track",  ["m", "0", "", "(1,2)"]),
        ("course", ["*", "Venus", "Venus rel (1,2)", "Venus rel 90d 3 km"]),
    ]
    cmds = [ keyword + " " + arg for (keyword, args) in to_test for arg in args]
    [ test_onecmd(command, text) for text in cmds ]

if __name__ == '__main__':
    (universe, clock) = u.create_test_universe(start_thread=False)
    view = v.View((0, 0), AU // 10, 1)
    #do_run(universe, view, 10)
    #do_stop(universe, view)
    default_craft = universe.bodies.get("Heroes")
    command = Command(universe, view, default_craft)
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
