from common import *
from sympy import Symbol, pprint, Rational, S, sin, cos, pi, Point, N
from sympy.solvers import solve, nsolve, nonlinsolve, solveset, linsolve
import mpmath
import universe as u
import view as v

import sys

def compute_course(start_point, end_point, start_velocity, end_velocity, a1x):
    mpmath.mp.dps = 3
    t1 = Symbol("t1", positive=True, real=True)
    t2 = Symbol("t2", positive=True, real=True)
    (sx, sy) = (end_point[0] - start_point[0], end_point[1] - start_point[1])
    if sx <= 0:
        print(f"sx={sx} <= 0: not handled yet")
        return
    (a1x, a1y) = ( a1x, Symbol("a1y", real=True))
    (a2x, a2y) = (-a1x, Symbol("a2y", real=True))
    (v1x, v1y) = start_velocity
    (v4x, v4y) = end_velocity
    v2x = v1x + t1 * a1x
    v2y = v1y + t1 * a1y
    v3x = v2x + t2 * a2x
    v3y = v2y + t2 * a2y
    s1x = (a1x/2)*t1**2 + v1x*t1
    s2x = (a2x/2)*t2**2 + v2x*t2
    s1y = (a1y/2)*t1**2 + v1y*t1
    s2y = (a2y/2)*t2**2 + v2y*t2
    f1 = s1x + s2x - sx
    f2 = s1y + s2y - sy
    f3 = v3x - v4x
    f4 = v3y - v4y

    solution = nonlinsolve((f1, f2, f3, f4), (t1, t2, a1y, a2y))
    for sol in solution:
        values={}
        ns = [ var.evalf(subs=values) for var in sol ]
        if all([n.is_real for n in ns]) and ns[0] >= 0 and ns[1] >= 0:
            xs = "  ".join([f"{float(n):.1f}" for n in ns])
            burn = (N(a1x), N(ns[2]))
            brake = (N(a2x), N(ns[3]))
            return (ns[0], ns[1], burn, brake)

def doit(start_point, end_point, start_velocity, end_velocity, max_acc):
    #max_acc = 10
    #start_point = (0, 0)
    #end_point = (1000, 100)
    #start_velocity = (0, 0)
    #end_velocity = (0, 100)
    high = max_acc
    low = 0.01
    oks = []
    while abs(high - low) > 0.05:
        mid = (high + low) / 2
        x_acceleration = mid
        course = compute_course(start_point, end_point, start_velocity, end_velocity, mid)
        if course:
            (t1, t2, burn, brake) = course
            t1 = round(t1, 1)
            t2 = round(t2, 1)
            course = (t1, t2, (round(burn[0], 1), round(burn[1], 1)), (round(brake[0], 1), round(brake[1], 1)))
            (t1, t2, burn, brake) = course
            b1 = sqrt(burn[0] * burn[0] + burn[1] * burn[1])
            b2 = sqrt(brake[0] * brake[0] + brake[1] * brake[1])
            #print(f"mid={mid:.1f}  t1={t1:.1f}  t2={t2:.1f}  burn=({burn[0]:.1f},{burn[1]:.1f}) ({b1:.1f})  brake=({brake[0]:.1f},{brake[1]:.1f}) ({b2:.1f})", end="  ")
            if b1 <= max_acc and b2 <= max_acc:
                oks.append(course)
                low = mid
            else:
                high = mid
        else:
            high = mid
    oks = list(sorted(oks, key=lambda a: a[0] + a[1]))
    (t1, t2, (bu1, bu2), (br1, br2)) = oks[0]
    return (float(t1), float(t2), (float(bu1), float(bu2)), (float(br1), float(br2)))

class Course:
    def __init__(self):
        pass

class Orbit(Course):
    center = None
    distance = None
    orbit_time = None

    def __init__(self, center, distance, orbit_time, *args):
        self.center = center
        self.distance = distance
        self.orbit_time = orbit_time
        super().__init__(*args)

    def calculate_position(self, universe, _, __, now):
        # print("Updating", self.__str__())
        center_xy = universe.get_body_position(self.center)
        if center_xy is None:
            print(f"{self.center} is lost in space.")
            return None
        else:
            (x, y) = center_xy
            day = now.timestamp() / 86400
            angle = math.radians(360) - math.radians(360) * (float(day % self.orbit_time) / float(self.orbit_time))
            dx = math.sin(angle) * self.distance
            dy = math.cos(angle) * self.distance
            return (x + dx, y + dy)

    def view(self, now=0):
        return "" # f"orbiting {self.center}"

    def __str__(self):
        return f"Orbit({self.center}, {v.format_distance(self.distance)}, {self.orbit_time} days)"

def get_burn_durations(sequence, last_update, now):
    result = []
    for (t1, t2, value) in sequence:
        if t2 <= last_update or now <= t1:
            continue
        t1 = max(t1, last_update)
        t2 = min(t2, now)
        result.append((t2 - t1, value))
    return result

class BurnSequence(Course):
    body = None
    sequence = None

    def __init__(self, body, sequence, *args):
        self.body = body
        gaps = []
        for ((_, t2a, __), (t1b, ___, ____)) in zip(sequence, sequence[1:]):
            if t2a != t1b:
                gaps.append((t2a, t1b, (0, 0)))
        self.sequence = sorted(sequence + gaps)
        super().__init__(*args)

    def calculate_position(self, universe, body, last_update, now):
        # TODO
        pos = self.body.pos
        return (0, 0)

    def view(self, now):
        sequence2 = [ (max(now, t1), t2, acc) for (t1, t2, acc) in self.sequence if t2 > now ]
        f = lambda acc: f"({v.format_acceleration(acc[0])}, {v.format_acceleration(acc[1])})"
        g = lambda acc: f"[{v.format_acceleration(sqrt(acc[0]**2 + acc[1]**2), as_g=True)}]"
        fg = lambda acc: "on the float" if acc == (0, 0) else f(acc) + " " + g(acc)
        return ", ".join([ f"{v.format_time(t2 - t1, short=False)} {fg(acc)}" for (t1, t2, acc) in sequence2 ])

    def __str__(self):
        return self.view(0)

# ===================================================================

def flip_and_burn_time(dist, max_g):
    dist = dist * 1000
    max_a = max_g * 9.81
    half_dist = dist / 2
    # s = 1/2 * a * t^2 => t = sqrt(2s / a)
    half_time = sqrt(2 * half_dist / max_a)
    time = 2 * half_time
    print(f"Time to flip-and-burn {v.format_distance(dist / 1000)} at max {max_g}g: {v.format_time(time, short=False)}")

def test_it():
    course = Target((100, 100), 9.81)
    print(course)

if __name__ == "__main__":
    print(get_burn_durations([], 10, 20))
    print(get_burn_durations([(6, 17, (1, 1))], 0, 15))
    print(get_burn_durations([(2, 5, (1, 1)), (5, 9, (2, 2)), (9, 12, (1, 0))], 3, 100))
    flip_and_burn_time(10 * AU, 2)
    burn_sequence = BurnSequence(None, [(10, 1000000, (1, 1)), (2000000, 2500000, (2, 3))])
    print(burn_sequence.sequence)
    print(burn_sequence)
    print(burn_sequence.view(500000))
    print(burn_sequence.view(1900000))
    # print(doit(start_point=(0,0), end_point=(1000, 100), start_velocity=(0,0), end_velocity=(0, 100), max_acc=10))
    (universe, clock) = u.create_test_universe(start_thread=False)
    universe.update()
    heroes = universe.bodies.get("Heroes")
    earth = universe.bodies.get("Earth")
    print(earth.course)
    now = clock.timestamp
    print("Earth position:", earth.position)
    clock.start(datetime.timedelta(days=1), lambda: universe.update())
    #time.sleep(3)
    #print("Earth pos +3d: ", earth.position)
    clock.terminate()
