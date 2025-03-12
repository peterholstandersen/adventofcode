from common import *
from utils import *
import universe as u

def format_time(time, short=True):
    second = (1, "s", "second")
    minute = (60, "m", "minute")
    hour   = (60 * minute[0], "h", "hour")
    day    = (24 * hour[0], "d", "day")
    month  = (30 * day[0], "M", "month")
    year   = (12 * month[0], "Y", "year")
    for (x, short_unit, long_unit) in (year, month, day, hour, minute, second):
        if time >= x:
            break
    n = time / x
    number = (f"{n:,.1f}" if n < 10 else f"{n:,.0f}")
    if number[-2:] == ".0":
        number = f"{n:,.0f}"
    if number != "1":
        long_unit += "s"
    unit = short_unit if short else long_unit
    return number + " " + unit

def format_distance(dist):
    if abs(dist) >= AU / 10:
        dist = dist / AU
        unit = " AU"
    else:
        unit = " km"
        if abs(dist) >= 1000:
            dist = dist / 1000
            unit = "K km"
        if abs(dist) >= 1000:
            dist = dist / 1000
            unit = "M km"
    number = f"{dist:,.1f}"
    if number[-2:] == ".0":
        number = f"{dist:,.0f}"
    return number + unit

def format_acceleration(acc, as_g=False):
    if as_g:
        # as g: two significant digits for easy reading
        acc = acc / 9.81
        a = f"{acc:.2g}"
        b = float(a)
        number = f"{b:,.2f}".rstrip("0").rstrip(".")
        if number == "-0":
            number = "0"
        return number + " g"
    # as m/s2: at most one decimal place. \u00B2 is 2 superscript. Show with more significant figures to appear more "scientific"
    unit = " m/s\u00B2"
    if abs(acc) >= 1000:
        acc = acc / 1000
        unit = " km/s\u00B2"
    if abs(acc) >= 10:
        acc = round(acc)
    number = f"{acc:,.1f}".rstrip("0").rstrip(".")
    if number == "-0":
        number = "0"
    return number + unit

class View:
    track = None       # If track is a string, the center is updated to the position of the object before showing
    center = None      # Coordinates
    scale = None
    enhance = None

    def __init__(self, center, scale, enhance):
        self.track = None
        self.center = center
        self.scale = scale
        self.enhance = enhance

    def _get_visual(self, universe, size_cl):
        offset_cl = (size_cl[0] // 2, size_cl[1] // 2)
        # (min_x, max_y) is correct since line 0 represents the maximum y value
        (min_x, max_y) = cl_to_xy((0, 0), offset_cl, self.center, self.scale)
        (max_x, min_y) = cl_to_xy(size_cl, offset_cl, self.center, self.scale)
        visual = dict()
        for body in universe.bodies.values():
            visual.update(body.get_visual(size_cl, offset_cl, self.center, self.scale, self.enhance))
        return visual

    def _get_text(self, universe):
        out = ""
        time_text = universe.clock.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        center_text = f"Center ({format_distance(self.center[0])}, {format_distance(self.center[1])})" if self.track is None else f"Tracking {self.track}"
        out += f"{time_text}   {center_text}   Scale 1: {format_distance(self.scale)}   Enhance = {self.enhance}\n"
        f = lambda body: " " + body.course.view(universe.clock.timestamp.timestamp()) if body.course else ""
        out += "\n".join([f"{body.colour_visual}: {body.name}{f(body)}" for body in universe.bodies.values() if body.visual != "."]) # hack
        return out

    def update_center(self, universe):
        if self.track:
            body = universe.bodies.get(self.track)
            if body:
                self.center = body.position
            else:
                print(f"{self.track} is lost in space, stopped tracking")
                self.track = None

    def show(self, universe, size_cl=None):
        universe.update()
        self.update_center(universe)
        if size_cl:
            (c, l) = size_cl
        else:
            (c, l) = os.get_terminal_size()
        text = self._get_text(universe)
        l = l - 5 - text.count("\n")
        visual = self._get_visual(universe, (c, l))
        out = visual_to_string(visual, (c, l))
        out += text
        os.system("clear")
        print(out)
        sys.stdout.flush()

def visual_to_string(visual, size_cl):
    out = ""
    for l in range(0, size_cl[1]):
        for c in range(0, size_cl[0]):
            out += visual[(c, l)] if (c, l) in visual else " "
        out += "\n"
    return out

# =================================================================================================================

# Planet m  Mercury 0.4  LIGHT_RED     88
# Planet v  Venus   0.7  YELLOW       225
# Planet e  Earth   1.0  LIGHT_BLUE   365
# Planet M  Mars    1.5  RED          687
# Planet c  Ceres   2.8  DARK_GRAY   1682
# Planet J  Jupiter 5.2  YELLOW      4333
# Planet S  Saturn  9.6  YELLOW     10759
# Planet U  Uranus 19.2  LIGHT_CYAN 30687
# Planet N  Neptune 30.0 LIGHT_BLUE 60190
# Planet p  Pluto   39.5 DARK_GRAY  90560

def test_format_acceleration():
    for as_g in [False, True]:
        for sign in [-1, 1]:
            print(format_acceleration(0, as_g))
            print(format_acceleration(sign * 0.0001, as_g))
            print(format_acceleration(sign * 0.001, as_g))
            print(format_acceleration(sign * 0.01, as_g))
            print(format_acceleration(sign * 0.02, as_g))
            print(format_acceleration(sign * 0.1, as_g))
            print(format_acceleration(sign * 1, as_g))
            print(format_acceleration(sign * 1.1, as_g))
            print(format_acceleration(sign * 1.55, as_g))
            print(format_acceleration(sign * 10, as_g))
            print(format_acceleration(sign * 11, as_g))
            print(format_acceleration(sign * 15, as_g))
            print(format_acceleration(sign * 20, as_g))
            print(format_acceleration(sign * 100, as_g))
            print(format_acceleration(sign * 1110, as_g))
            print(format_acceleration(sign * 22220, as_g))
            print(format_acceleration(sign * 333330, as_g))
            print(format_acceleration(sign * 0.05 * 9.81, as_g))
        print()

def test_format_time():
    year = 30 * 24 * 3600 * 12
    test_time = [(1, "1 s", "1 second"), (60, "1 m", "1 minute"), (3600, "1 h", "1 hour"), (24 * 3600, "1 d", "1 day"),
                 (30 * 24 * 3600, "1 M", "1 month"), (year, "1 Y", "1 year"), (year * 1.5, "1.5 Y", "1.5 years"),
                 (year * 10, "10 Y", "10 years")]
    for (t, short, long) in test_time:
        print(f"{t:>10}   {short:<6}", end="")
        ok = verify(format_time(t), short, silent=True)
        print(" OK" if ok else " ERROR")
    for (t, short, long) in test_time:
        print(f"{t:>10}   {long:<10}", end="")
        ok = verify(format_time(t, short=False), long, silent=True)
        print(" OK" if ok else " ERROR")

def create_test_view():
    return View((0, 0), 0.3 * AU, 4)

def run_all_tests():
    test_format_acceleration()
    test_format_time()
    (universe, clock) = u.create_test_universe()
    view = create_test_view()
    view.show(universe, (80, 8))

if __name__ == "__main__":
    run_all_tests()