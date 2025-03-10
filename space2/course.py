from common import *
from sympy import Symbol, pprint, Rational, S, sin, cos, pi, Point, N
from sympy.solvers import solve, nsolve, nonlinsolve, solveset, linsolve
import mpmath
import universe as u

import sys

def compute_course(start_point, end_point, start_velocity, end_velocity, a1x):
    mpmath.mp.dps = 3
    t1 = Symbol("t1", positive=True, real=True)
    t2 = Symbol("t2", positive=True, real=True)
    (sx, sy) = (end_point[0] - start_point[0], end_point[1] - start_point[1])
    if sx <= 0:
        print("sx <= 0: not handled yet")
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
    # print(solution)
    for sol in solution:
        values={} # {t2: 1}
        ns = [ var.evalf(subs=values) for var in sol ]
        if all([n.is_real for n in ns]) and ns[0] >= 0 and ns[1] >= 0:
            xs = "  ".join([f"{float(n):.1f}" for n in ns])
            burn = (N(a1x), N(ns[2]))
            brake = (N(a2x), N(ns[3]))
            # print(xs, f"burn={burn}  brake={brake}")
            return (ns[0], ns[1], burn, brake)


def doit():
    max_acc = 10
    start_point = (0, 0)
    end_point = (1000, 100)
    start_velocity = (0, 0)
    end_velocity = (0, 100)
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
            print(f"mid={mid:.1f}  t1={t1:.1f}  t2={t2:.1f}  burn=({burn[0]:.1f},{burn[1]:.1f}) ({b1:.1f})  brake=({brake[0]:.1f},{brake[1]:.1f}) ({b2:.1f})", end="  ")
            if b1 <= max_acc and b2 <= max_acc:
                oks.append(course)
                # we might go higher
                low = mid
                print("OK")
            else:
                high = mid
                print("NOT")
        else:
            high = mid
    oks = list(sorted(oks, key=lambda a: a[0] + a[1]))
    print(oks)

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

def my_solve(a, v, s, t):
    if a is None:
        if t == 0 and s == 0:
            return
        if t == 0 and s > 0:
            return math.inf
        a = (2 * (v * t - s)) / (t * t)
        return a
    elif s is None:
        return 1/2 * a * t * t + v * t
        return

class Target(Course):
    body = None
    target_postion = None
    max_acc = None
    end_velocity = 0

    def __init__(self, body, target_position, max_acc, *args):
        self.body = body
        self.target_position = target_position
        self.max_acc = max_acc
        super().__init__(*args)

    def calculate_position(self, last_update, now):
        (x1, y1) = self.body.position
        (x1, y1) = (0, 0)
        (x2, y2) = self.target_position
        (x2, y2) = (0, 1000)

        (dist_x, dist_y) = (x2 - x1, y2 - y1)
        distance_to_target = sqrt(dist_x * dist_x + dist_y * dist_y)

        (dx, dy) = self.body.velocity if self.body.velocity is not None else (0, 0)
        velocity = sqrt(dx * dx + dy * dy)
        needed_time_to_brake = velocity / self.max_acc
        #needed_distance_to_brake = solve(a=-self.max_acc, v=velocity, s=None, t=needed_time_to_brake)

        #print(f"calculate_position: pos=({x1:.0f},{y1:.0f})  target=({x2:.0f},{y2:.0f})  dist={distance_to_target:.0f}  current_v={velocity:.0f}  needed_t={needed_time_to_brake:.0f}  needed_s={needed_distance_to_brake:.0f}")
        #if distance_to_target < needed_distance_to_brake:
        #    print("Impossible")
        return (0,0)

# ===================================================================

def flip_and_burn_time(dist, max_g):
    dist = dist * 1000
    max_a = max_g * 9.81
    half_dist = dist / 2
    # s = 1/2 * a * t^2 => t = sqrt(2s / a)
    half_time = sqrt(2 * half_dist / max_a)
    time = 2 * half_time
    print(f"Time to flip-and-burn {view.format_distance(dist / 1000)} at max {max_g}g: {view.format_time(time, short=False)}")

def test():
    time = 0
    s = 100000
    # s = 149e+9
    a = 0
    v = 1
    end_v = 0
    max_a = 9.81
    # max_a = 1
    step = 10
    count = 100000000
    while (v > end_v or s > 0) and count > 0:
        count -= 1
        time += step
        print(f"{time:.01f}: s: {s:.02f},  v: {v:.02f}  a: {a:.02f}", end="")
        needed_t = max((v - end_v) / max_a, 1)
        # needed acc next second if we burn max this round
        sx = s - (0.5 * max_a * step + v * step)
        vx = v + max_a
        needed_a = 2 * (sx - vx * needed_t) / (needed_t * needed_t)
        print(f"  needed_a (next {step} seconds): {needed_a:.2f}", end="")
        if False and needed_a < -max_a and step > 1:
            time -= step
            step = step / 2
            print(f"  step: {step}")
            continue
        if needed_a > -max_a:
            a = max_a # min(max_a, needed_a)
            print(f"  BURN    {a:.0f}")
        else:
            needed_a = 2 * (s - v * needed_t) / (needed_t * needed_t)
            a = needed_a
            if a < -max_a:
                a = -max_a
            print(f"  BRAKE  {a:.2f}")
        s = s - (0.5 * a * step + v * step)
        v = v + a * step
    print(f"{time}: s: {s:.02f},  v: {v:.02f}  a: {a:.02f}")
    #print(time / 3600)
    #print(time / 3600 / 24)

def test_it():
    course = Target((100, 100), 9.81)
    print(course)

if __name__ == "__main__":
    doit()
    sys.exit()

    (universe, clock) = u.create_test_universe(start_thread=False)
    universe.update()
    heroes = universe.bodies.get("Heroes")
    heroes.course = Target(heroes, (0, 0), 9.81)
    xy = heroes.course.calculate_position(universe.clock.timestamp, universe.clock.timestamp + datetime.timedelta(seconds=1))
    print(xy)
    sys.exit()
    flip_and_burn_time(10 * AU, 2)
    orbit = earth.course
    now = clock.timestamp
    print("Earth position:", earth.position)
    earth.update(0, now)
    print("Earth position:", earth.position)
    clock.start(datetime.timedelta(days=1), lambda: universe.update())
    time.sleep(3)
    clock.terminate()
