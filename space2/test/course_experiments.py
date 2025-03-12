# from common import *
from sympy.solvers import solve, nsolve, nonlinsolve, solveset, linsolve
import mpmath
from sympy import Symbol, pprint, Rational, S, sin, cos, pi, Point

import sys

def test1():
    a1 = 9.81
    a2 = -9.81
    t = Symbol("t")
    v2 = t * a1
    s = 1000
    r = solve(0.5*a1*(t**2) + 0.5*a2*(t**2) + v2 * t - s, t)
    print(r)
    sys.exit()

def test2():
    mpmath.mp.dps = 3
    a1 = 9.81
    v1 = 0
    t1 = Symbol("t1")
    a2 = -9.81
    t2 = Symbol("t2")
    v2 = v1 + t1 * a1
    s1 = Symbol("s1")
    s2 = Symbol("s2")
    s = 1000
    f1 = 0.5*a1*t1**2 + v1*t1 - s1
    f2 = 0.5*a2*t2**2 + (v1+v2)*t2 - s2
    f3 = v2 - a2*t2
    f4 = s1 + s2 - s
    # f3 = s1 + (s - s1) - s
    print(nsolve((f1, f2, f3, f4), (t1, t2), (10, 12)))
    sys.exit(1)

def test3():
    max_acc = 9.81
    mpmath.mp.dps = 3
    a1 = max_acc
    v1 = 0                # start speed
    t1 = Symbol("t1")     # burn time
    a2 = -max_acc
    t2 = Symbol("t2")     # brake time
    v2 = v1 + t1 * a1     # speed at the end of burn
    v3 = v2 + t2 * a2     # speed at the end of brake
    desired_end_speed = 0
    s = 1000
    s1 = 0.5*a1*t1**2 + v1*t1       # distance traveled during burn time
    s2 = 0.5*a2*t2**2 + (v1+v2)*t2  # distance traveled during brake time
    f1 = s1 + s2 - s                # total distance traveled must equal s
    f2 = v3 - desired_end_speed     # the speed at the end of the brake must equal the desired end speed
    print(nsolve((f1, f2), (t1, t2), (10, 10)))
    print(nonlinsolve((f1, f2), (t1, t2), (10, 10)))

def test4():
    mpmath.mp.dps = 3
    max_acc = 10 # Rational(981, 100)

    t1 = Symbol("t1", positive=True, real=True)
    t2 = Symbol("t2", positive=True, real=True)
    a1x = Symbol("a1x", real=True)
    a1y = Symbol("a1y", real=True)

    a2x = -a1x # Symbol("a2x", real=True)
    a2y = -a1y # Symbol("a2y", real=True)
    a3x = 0 # Symbol("a3x", real=True)
    a3y = Symbol("a3y", real=True)

    v1x = 0   # while testing
    v1y = 0   # while testing

    v2x = v1x + t1 * (a1x + a3x)
    v2y = v1y + t1 * (a1y + a3y)

    v3x = v2x + t2 * (a2x + a3x)
    v3y = v2y + t2 * (a2y + a3y)

    s1x = ((a1x + a3x)/2)*t1**2 + v1x*t1
    s2x = ((a2x + a3x)/2)*t2**2 + (v1x + v2x)*t2

    s1y = ((a1y + a3y)/2)*t1**2 + v1y*t1
    s2y = ((a2y + a3y)/2)*t2**2 + (v1y + v2y)*t2

    (sx, sy) = (1000, 0)

    f1 = s1x + s2x - sx
    f2 = s1y + s2y - sy
    f3 = v3x                            # end speed must be zero
    f4 = v3y                            # end speed must be zero
    f5 = (a1x + a3x) * (a1x + a3x) + (a1y + a3y) * (a1y + a3y) - max_acc * max_acc
    f6 = (a2x + a3x) * (a2x + a3x) + (a2y + a3y) * (a2y + a3y) - max_acc * max_acc

    # solution = linsolve((f1, f2, f3, f4), (t1, t2, a1x, a1y))  # t1**2 is nonlinear, so this does not work
    solution = nonlinsolve((f1, f2, f3, f4, f5, f6), (t1, t2, a1x, a1y, a3x, a3y))
    # solution = solveset((f1, f2, f3, f4), (t1, t2, a1x, a1y), domain=S.Reals)#, (10, 10, 1, 2)) # solveset
    # solution = nsolve((f1, f2, f3, f4), (t1, t2, a1x, a1y), (10, 10, 1, 2))

    print(solution)

    for sol in solution:
        print()
        print("Solution:", sol)
        values={}
        #for foo in sol:
        #    result = foo.evalf(subs=values)
        #    print(result, end="  ")
        #print()
        #continue
        n1 = sol[0].evalf(subs=values)  # t1
        n2 = sol[1].evalf(subs=values)  # t2
        n3 = sol[2].evalf(subs=values)  # a1x
        n4 = sol[3].evalf(subs=values)  # a1y
        n5 = sol[4].evalf(subs=values)  # a3x
        n6 = sol[5].evalf(subs=values)  # a3x
        print(f"t1={n1}  t2={n2}  a1x={n3}  a1y={n4}  a3x={n5}  a3y={n6}", end="  ")
        if n1.is_real and n2.is_real and n3.is_real and n4.is_real and n1 >= 0.0 and n2 >= 0.0:
            print("OK")
        else:
            print("NOT OK")

def test4b():
    mpmath.mp.dps = 3

    t1 = Symbol("t1", positive=True, real=True)
    t2 = Symbol("t2", positive=True, real=True)

    (a1x, a1y) = (  10, Symbol("a1y", real=True))
    (a2x, a2y) = (-a1x, Symbol("a2y", real=True))
    (v1x, v1y) = (0, 0)    # start velocity
    (v4x, v4y) = (0, 0)    # desired end velocity

    v2x = v1x + t1 * a1x
    v2y = v1y + t1 * a1y

    v3x = v2x + t2 * a2x
    v3y = v2y + t2 * a2y

    s1x = (a1x/2)*t1**2 + v1x*t1
    s2x = (a2x/2)*t2**2 + v2x*t2

    s1y = (a1y/2)*t1**2 + v1y*t1
    s2y = (a2y/2)*t2**2 + v2y*t2

    (sx, sy) = (1000, 0)

    f1 = s1x + s2x - sx
    f2 = s1y + s2y - sy
    f3 = v3x - v4x
    f4 = v3y - v4y

    solution = nonlinsolve((f1, f2, f3, f4), (t1, t2, a1y, a2y))

    print(solution)

    for sol in solution:
        values={t2: 1}
        ns = [ var.evalf(subs=values) for var in sol ]
        if all([n.is_real for n in ns]) and ns[0] >= 0 and ns[1] >= 0:
            a1y_value = a1y.evalf(subs=values)
            xs = " ".join([f"{float(n):.1f}" for n in ns])
            burn = (a1x, ns[2])
            brake = (a2x, ns[3])
            print(xs, f"burn={burn}  brake={brake}")
    sys.exit()

def test5():
    mpmath.mp.dps = 3

    t1 = Symbol("t1", positive=True, real=True)
    t2 = Symbol("t2", positive=True, real=True)

    max_acc = 10 # Rational(981, 100)

    a1 = max_acc
    a2 = max_acc
    angle1 = Symbol("angle1", real=True)
    angle2 = Symbol("angle2", real=True)

    a1x = a1 * cos(angle1)
    a1y = a1 * sin(angle1)
    a2x = a2 * cos(angle2)
    a2y = a2 * sin(angle2)

    v1x = 0   # while testing
    v1y = 0   # while testing

    v2x = v1x + t1 * a1x
    v2y = v1y + t1 * a1y

    v3x = v2x + t2 * a2x
    v3y = v2y + t2 * a2y

    s1x = (a1x/2)*t1**2 + v1x*t1
    s2x = (a2x/2)*t2**2 + (v1x + v2x)*t2

    s1y = (a1y/2)*t1**2 + v1y*t1
    s2y = (a2y/2)*t2**2 + (v1y + v2y)*t2

    (sx, sy) = (1000, 0)

    f1 = s1x + s2x - sx
    f2 = s1y + s2y - sy
    f3 = v3x                            # end speed must be zero
    f4 = v3y                            # end speed must be zero
    f5 = angle2 - (pi - angle1)

    print(f1)
    print(f2)
    print(f3)
    print(f4)
    print(f5)

    # solution = solveset((f1, f2, f3, f4), (t1, t2, a1x, a1y), domain=S.Reals)#, (10, 10, 1, 2)) # solveset
    # solution = nsolve((f1, f2, f3, f4), (t1, t2, angle1, angle2), (10, 10, 1, 2))
    solution = nonlinsolve((f1, f2, f3, f4, f5), (t1, t2, angle1, angle2))
    print(solution)

    for sol in solution:
        values={}
        n1 = sol[0].evalf(subs=values)  # t1
        n2 = sol[1].evalf(subs=values)  # t2
        n3 = sol[2].evalf(subs=values)  # angle1
        n4 = sol[3].evalf(subs=values)  # angle2
        print(f"t1={n1}  t2={n2}  angle1={n3}  angle2={n4}", end="  ")
        if n1.is_real and n2.is_real and n3.is_real and n4.is_real and n1 >= 0.0 and n2 >= 0.0:
            print("OK")
        else:
            print("NOT OK")



#test1()
#test2()
#test3()
test4b()
#test5()
sys.exit()

mpmath.mp.dps = 15
x1 = Symbol('x1')
x2 = Symbol('x2')
f1 = 3 * x1**2 - 2 * x2**2 - 1
f2 = x1**2 - 2 * x1 + x2**2 + 2 * x2 - 8
print(nsolve((f1, f2), (x1, x2), (-1, 1)))
sys.exit(1)


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
        # needed_distance_to_brake = solve(a=-self.max_acc, v=velocity, s=None, t=needed_time_to_brake)

        print(f"calculate_position: pos=({x1:.0f},{y1:.0f})  target=({x2:.0f},{y2:.0f})  dist={distance_to_target:.0f}  current_v={velocity:.0f}  needed_t={needed_time_to_brake:.0f}  needed_s={needed_distance_to_brake:.0f}")
        if distance_to_target < needed_distance_to_brake:
            print("Impossible")
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
