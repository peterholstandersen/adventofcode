import time

class Timer:
    def __init__(self):
        pass

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, *args):
        print("time:", time.time() - self.start)