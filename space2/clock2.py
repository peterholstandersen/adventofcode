from common import *
import datetime
import time
from utils import *

class Clock2:
    def __init__(self, universe_time):
        self._last_update = time.time()       # current time as seconds
        self._factor = 0
        self._universe_time = universe_time  # universe time as seconds

    def _update_time(self):
        now = time.time()
        wall_clock_delta = now - self._last_update
        self._last_update = now
        self._universe_time += self._factor * wall_clock_delta

    def start_thread(self):
        pass

    def is_running(self):
        return self._factor != 0

    def terminate(self):
        pass

    def tick(self, seconds):
        if self.is_running():
            return None
        self._universe_time += seconds

    def start(self, factor, hook=None):
        self._factor = factor
        self._last_update = time.time()

    def stop(self):
        self._update_time()
        self._factor = 0

    def get_time(self):
        self._update_time()
        return self._universe_time

    def run(self):
        pass

# ===============================================

def make_clock(wall_clock=datetime.datetime(2030, 8, 20, 16, 49, 7, 652303), start_thread=False):
    clock = Clock2(wall_clock.timestamp())
    return clock

if __name__ == "__main__":
    print("Hej Univers")
    clock = make_clock()
    if not is_running_in_terminal():
        sys.exit()
    print("commands: start, stop, exit (or blank)")
    for line in sys.stdin:
        line = line.strip()
        print(f"line = '{line}'")
        if line == "":
            print(clock.get_time())
        elif line == "start":
            clock.start(20)
        elif line == "stop":
            clock.stop()
        elif line == "exit":
            sys.exit()
        else:
            print("unknown command. try start, stop or exit.")
        print("type command>")
