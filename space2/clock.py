from common import *

class Clock:
    _step = 1
    _running_event = None
    _terminate = False
    _hook = None
    thread = None
    timestamp = None

    def __init__(self, universe_time):
        self._running_event = threading.Event()
        self._running_event.clear()
        self.timestamp = universe_time
        self.thread = threading.Thread(target=self.run)

    def start_thread(self):
        print("clock: start_thread")
        self.thread.start()

    def is_running(self):
        return self.thread.is_alive() and self._running_event.is_set()

    def terminate(self):
        print("clock: terminate")
        if not self.thread.is_alive():
            print("clock: thread is not running")
            return
        self._terminate = True
        self._running_event.set()
        print("clock: waiting for thread to terminate")
        self.thread.join()
        print("clock: thread terminated")

    def start(self, step, hook):
        if not self.thread.is_alive():
            print("clock: thread is not alive")
            return False
        self._step = step
        self._hook = hook
        self._running_event.set()
        return True

    def stop(self):
        if not self.thread.is_alive():
            print("clock: thread is not alive")
            return False
        self._running_event.clear()
        self._hook = None
        return True

    def run(self):
        while not self._terminate:
            if self._running_event.is_set():
                self.timestamp += self._step
                if self._hook:
                    self._hook()
                time.sleep(1)
            else:
                self._running_event.wait(600)

# ===============================================

def make_clock(timestamp, start_thread=False):
    clock = Clock(timestamp)
    if start_thread:
        clock.start_thread()
    return clock

if __name__ == "__main__":
    print("Hej Univers")
    timestamp = datetime.datetime(2030, 8, 20, 16, 49, 7, 652303)
    clock = make_clock(timestamp, True)
    print("type command>")
    for line in sys.stdin:
        line = line.strip()
        print(f"line = '{line}'")
        if line == "start":
            clock.start(datetime.timedelta(seconds=10))
        elif line == "stop":
            clock.stop()
        elif line == "exit":
            print("stopping thread")
            clock.terminate()
            print("DONE")
            sys.exit()
        else:
            print("unknown command. try start, stop or exit.")
        print("type command>")
