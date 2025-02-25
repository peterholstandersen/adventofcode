from common import *
from utils import *

def get_visual(world, size_cl, center_xy, scale):
    offset_cl = (size_cl[0] // 2, size_cl[1] // 2)
    # (min_x, max_y) is correct since line 0 represents the maximum y value
    (min_x, max_y) = cl_to_xy((0, 0), offset_cl, center_xy, scale)
    (max_x, min_y) = cl_to_xy(size_cl, offset_cl, center_xy, scale)
    bbox_xy = ((min_x, min_y), (max_x, max_y))
    visual = dict()
    for body in world.bodies.values():
        visual.update(body.get_visual(bbox_xy, offset_cl, center_xy, scale))
    return visual

def visual_to_string(visual, size_cl):
    out = ""
    for l in range(0, size_cl[1] + 1):
        for c in range(0, size_cl[0] + 1):
            out += visual[(c, l)] if (c, l) in visual else " "
        out += "\n"
    return out

def test():
    bodies = dict()
    bodies["*"] = SpaceObject("*", "Sun", (0, 0), RED, "*", 696340, "start_sun.png") # 696,340 km radius
    world = World(bodies)
    size_cl = (80, 4)
    visual = get_visual(world, size_cl, (0, 0), 500000)
    out = visual_to_string(visual, size_cl)
    print(out, end="")

if __name__ == "__main__":
    test()