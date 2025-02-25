from common import *

def make_crafts():
    return 1

def make_bodies():
    return 2

def make_world():
    crafts = make_crafts()
    bodies = make_bodies()
    world = World(crafts, bodies)
    return world

if __name__ == "__main__":
    verify(1, 1)
    print("TEST")
    world = make_world()