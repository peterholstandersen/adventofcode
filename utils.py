import time

class Timer:
    def __init__(self):
        pass

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, *args):
        print("time:", time.time() - self.start)

class ansi:
    green = "\u001b[32m"
    white = "\u001b[37m"
    bold = "\u001b[1m"
    reset = "\u001b[0m"
    reverse = "\u001b[7m"
    top = "\u001b[0;0H"
