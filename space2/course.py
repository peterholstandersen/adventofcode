from common import *
from sympy import Symbol, N
from sympy.solvers import nonlinsolve
import julian
import datetime
import mpmath
import universe as u
import view as v

def compute_course1(start_point, end_point, start_velocity, end_velocity, a1x):
    mpmath.mp.dps = 3
    t1 = Symbol("t1", positive=True, real=True)
    t2 = Symbol("t2", positive=True, real=True)
    (sx, sy) = (end_point[0] - start_point[0], end_point[1] - start_point[1])
    if sx <= 0:
        print(f"sx={sx} <= 0: not handled yet")
        return
    # we fix the burn and brake acceleration for the x-axis and compute the needed burn and brake acc for the y-axis
    # without any limit for the total acceration
    #
    # 1 (start)           2                  3 (end)
    # +-------------------+------------------+
    # |>>>>>>>burn>>>>>>>>|<<<<<brake<<<<<<<<|
    #
    # (a1x, a1y) is the acceration from 1->2
    # (a2x, a2y) is the acceration from 2->3
    # (v1x, v1y) is the velocity at 1 (start velocity)
    # (v2x, v2y) is the velocity at 2
    # (v3x, v3y) is the velocity at 3 (actual end velocity)
    # (v4x, v4y) is the desired end velocity at 3
    # (s1x, s1y) is the distance from 1->2
    # (s2x, s2y) is the distance from 2->3
    # (sx, sy) is the distance from 1->3 (total distance travelled) -- given by start and end positions

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
    solution = nonlinsolve((f1, f2, f3, f4), (t1, t2, a1y, a2y))   # find t1,t2,a1y,a2y for f1,f2,f3,f4 = 0
    for sol in solution:
        values = {}
        ns = [ var.evalf(subs=values) for var in sol ]
        # only accept real numbers and positive numbers for t1 and t2
        if all([n.is_real for n in ns]) and ns[0] >= 0 and ns[1] >= 0:
            xs = "  ".join([f"{float(n):.1f}" for n in ns])
            burn = (N(a1x), N(ns[2]))
            brake = (N(a2x), N(ns[3]))
            return (ns[0], ns[1], burn, brake)

def compute_course(start_point, end_point, start_velocity, end_velocity, max_acc):
    # find the fastest solution for with acceleration <= max_acc
    high = max_acc
    low = 0.01
    valid_solutions = []
    while abs(high - low) > 0.01:
        mid = (high + low) / 2
        x_acceleration = mid
        course = compute_course1(start_point, end_point, start_velocity, end_velocity, mid)
        if course is None:
            high = mid
            continue
        f = lambda x: float(round(x, 1))            # x is a Float, must be converted to float
        g = lambda xy: (f(xy[0]), f(xy[1]))
        h = lambda xy: sqrt(xy[0]**2 + xy[1]**2)
        (t1, t2, burn, brake) = course
        (t1, t2, burn, brake) = (f(t1), f(t2), g(burn), g(brake))
        course = (t1, t2, burn, brake)
        # print(f"mid={mid:.1f}  t1={t1:.1f}  t2={t2:.1f}  burn=({burn[0]:.1f},{burn[1]:.1f}) ({b1:.1f})  brake=({brake[0]:.1f},{brake[1]:.1f}) ({b2:.1f})")
        if h(burn) <= max_acc and h(brake) <= max_acc:
            valid_solutions.append(course)
            low = mid
        else:
            high = mid
    if len(valid_solutions) == 0:
        return None
    valid_solutions = list(sorted(valid_solutions, key=lambda course: course[0] + course[1]))
    return valid_solutions[0]

class Course:
    # base class
    def __init__(self):
        pass

class Orbit(Course):
    center = None
    N = i = w = a = e = M = dM = None

    def __init__(self, center, N, i, w, a, e, M, dM, *args):
        self.center = center
        self.N = math.radians(N)
        self.i = math.radians(i)
        self.w = math.radians(w)
        self.a = a * AU
        self.e = e
        self.M = math.radians(M)
        self.dM = math.radians(dM)
        super().__init__(*args)

    def calculate_position1(self, d):
        sin = math.sin
        cos = math.cos
        atan2 = math.atan2

        N = self.N
        i = self.i
        w = self.w
        a = self.a
        e = self.e
        M = self.M + d * self.dM

        # https://stjarnhimlen.se/comp/tutorial.html

        # perihelion: point closest to the sun

        # To describe the position in the orbit, we use three angles: Mean Anomaly, True Anomaly, and Eccentric Anomaly.
        # They are all zero when the planet is in perihelion:
        # Mean Anomaly (M): This angle increases uniformly over time, by 360 degrees per orbital period.
        # It's zero at perihelion. It's easily computed from the orbital period and the time since last perihelion.
        #
        # True Anomaly (v): This is the actual angle between the planet and the perihelion, as seen from the central
        # body (in this case the Sun). It increases non-uniformly with time, changing most rapidly at perihelion.
        #
        # Eccentric Anomaly (E): This is an auxiliary angle used in Kepler's Equation, when computing the True Anomaly
        # from the Mean Anomaly and the orbital eccentricity.
        # Note that for a circular orbit (eccentricity=0), these three angles are all equal to each other.

        # Now we must solve Kepler's equation M = e * sin(E) - E, where we know M, the mean anomaly, and the e the
        # eccentricity, and we want to find E, the eccentricity anomaly. We start by computing a first approximation
        # of E:

        E0 = M + e * sin(M) * (1.0 * e * sin(M))

        # Some experiments show that 3-4 iterations is enough
        count = 0
        while True:
            count += 1
            if count > 100:
                print("Kepler's equation does not converge. Eccentricity is probably close to one:", e)
                sys.exit(1)
            E1 = E0 - (E0 - e * sin(E0) - M) / (1 - e * cos(E0))
            if abs(E1 - E0) < math.radians(1E-06):
                break
            E0 = E1
        E = E1

        # The planet's distance and true anomaly
        xv = a * (cos(E) - e)
        yv = a * math.sqrt(1.0 - e**2) * sin(E)
        v = atan2(yv, xv)
        r = math.sqrt(xv**2 + yv**2)

        # The planet's position in 3d space
        xh = r * (cos(N) * cos(v + w) - sin(N) * sin(v + w) * cos(i))
        yh = r * (sin(N) * cos(v + w) + cos(N) * sin(v + w) * cos(i))
        zh = r * (sin(v + w) * sin(i))

        r_check = sqrt(xh * xh + yh * yh + zh * zh) # must equal r except for rounding errors
        if abs(r - r_check) > 0.001:
            print("must be (nearly) equal", r, r_check, abs(r - r_check))
            print(self)
            sys.exit()

        return (xh, yh, zh)

    def calculate_position(self, universe, _, __, now):
        center_xyz = universe.get_body_position(self.center)
        if center_xyz is None:
            print(f"{self.center} is lost in space.")
            return None
        julian_day = julian.to_jd(datetime.datetime.fromtimestamp(now), fmt="jd")
        return self.calculate_position1(julian_day)

    def view(self, now=0):
        return ""

    def __str__(self):
        return f"Orbit({self.center}, a={self.a / AU})"

class BurnSequence(Course):
    body = None
    sequence = None

    def __init__(self, body, sequence, *args):
        self.body = body
        gaps = []
        for ((_, end_time_1, _), (start_time_2, _, _)) in zip(sequence, sequence[1:]):
            if end_time_1 != start_time_2:
                gaps.append((end_time_1, start_time_2, (0, 0)))
        self.sequence = sorted(sequence + gaps)
        super().__init__(*args)

    def calculate_position(self, universe, body, last_update, now):
        # TODO: calculate position based on burn sequence
        return self.body.pos

    def view(self, now):
        sequence2 = [ (max(now, t1), t2, acc) for (t1, t2, acc) in self.sequence if t2 > now ]
        f = lambda acc: f"({v.format_acceleration(acc[0])}, {v.format_acceleration(acc[1])})"
        g = lambda acc: f"[{v.format_acceleration(sqrt(acc[0]**2 + acc[1]**2), as_g=True)}]"
        fg = lambda acc: "on the float" if acc == (0, 0) else f(acc) + " " + g(acc)
        return ", ".join([ f"{v.format_time(t2 - t1, short=False)} {fg(acc)}" for (t1, t2, acc) in sequence2 ])

    def __str__(self):
        return self.view(0)

# ===================================================================

def test_burn_durations(sequence, last_update, now):
    result = []
    for (t1, t2, value) in sequence:
        if t2 <= last_update or now <= t1:
            continue
        t1 = max(t1, last_update)
        t2 = min(t2, now)
        result.append((t2 - t1, value))
    return result

def flip_and_burn_time(dist, max_g):
    dist = dist * 1000
    max_a = max_g * 9.81
    half_dist = dist / 2
    # s = 1/2 * a * t^2 => t = sqrt(2s / a)
    half_time = sqrt(2 * half_dist / max_a)
    time = 2 * half_time
    print(f"Time to flip-and-burn {v.format_distance(dist / 1000)} at max {max_g}g: {v.format_time(time, short=False)}")

if __name__ == "__main__":
    print(test_burn_durations([], 10, 20))
    print(test_burn_durations([(6, 17, (1, 1))], 0, 15))
    print(test_burn_durations([(2, 5, (1, 1)), (5, 9, (2, 2)), (9, 12, (1, 0))], 3, 100))
    flip_and_burn_time(10 * AU, 2)
    burn_sequence = BurnSequence(None, [(10, 1000000, (1, 1)), (2000000, 2500000, (2, 3))])
    print(burn_sequence.sequence)
    print(burn_sequence)
    print(burn_sequence.view(500000))
    print(burn_sequence.view(1900000))
    # print(doit(start_point=(0,0), end_point=(1000, 100), start_velocity=(0,0), end_velocity=(0, 100), max_acc=10))
    universe = u.big_bang()
    universe.update()
    # heroes = universe.bodies.get("Heroes")
    mercury = universe.bodies.get("Mercury")
    print(mercury.course)
    print("Mercury pos:", mercury.position)
    universe.update()
    universe.clock.set_factor(10000)
    print("Sleep 100ms")
    time.sleep(0.1)
    universe.update()
    print("Mercury pos:", mercury.position)
