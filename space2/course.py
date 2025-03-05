from common import *
import view
import sys

class Course:
    def __init__(self):
        pass

class Orbit(Course):
    center = None
    distance = None
    orbit_time = None

    def __init__(self, center, distance, orbit_time):
        self.center = center
        self.distance = distance
        self.orbit_time = orbit_time
        super().__init__(*args)

class Target(Course):
    def __init__(self, *args):
        super().__init__(*args)


def time(dist, max_g):
    dist = dist * 1000
    max_a = max_g * 9.81
    half_dist = dist / 2
    # s = 1/2 * a * t^2 => t = sqrt(2s / a)
    half_time = sqrt(2 * half_dist / max_a)
    time = 2 * half_time
    print(f"Time to flip-and-burn {view.format_distance(dist / 1000)} at max {max_g}g: {view.format_time(time, short=False)}")

time(10 * AU, 2)

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
