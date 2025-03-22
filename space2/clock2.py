from common import *
import universe as u
import time

class Clock2:
    def __init__(self, universe_time):
        self._last_update = time.time()       # current wall-clock time as seconds
        self._factor = 0
        self._universe_time = universe_time   # current universe time as seconds

    def _update_time(self):
        now = time.time()
        wall_clock_delta = now - self._last_update
        self._last_update = now
        self._universe_time += self._factor * wall_clock_delta

    def is_running(self):
        return self._factor != 0

    # Advance universe clock -- if it is not running already
    def tick(self, seconds):
        if self.is_running():
            return None
        self._universe_time += seconds

    def set_factor(self, factor):
        if factor < 0:
            print("The Universe answers: If I Could Turn Back Time ... If I could find a way ... I'd take back those words that have hurt you ...")
            return
        self._update_time()
        self._factor = factor

    def stop(self):
        self.set_factor(0)

    def get_time(self):
        self._update_time()
        return self._universe_time

# ===============================================

def run_all_tests():
    print("Hello Univers")
    universe = u.big_bang()
    clock = universe.clock
    #if not is_running_in_terminal():
    #    sys.exit()
    print("init:", clock.get_time())
    print("same:", clock.get_time())
    clock.set_factor(1000000)
    print("new: ", clock.get_time())
    clock.stop()
    print("new: ", clock.get_time())
    print("same:", clock.get_time())
    clock.set_factor(-1)

if __name__ == "__main__":
    run_all_tests()
