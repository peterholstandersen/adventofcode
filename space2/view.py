from common import *
from utils import *
import universe

class View:
    rlock = threading.RLock()
    _center = None
    _scale = None
    zoom = None
    def __init__(self, center, scale, zoom):
        self._center = center
        self._scale = scale
        self.zoom = zoom

    @property
    def scale(self):
        with self.rlock:
            return self._scale

    @property
    def center(self):
        with self.rlock:
            return self._center

    @scale.setter
    def scale(self, value):
        # print(f"scale: set {value}")
        with self.rlock:
            self._scale = value

    @center.setter
    def center(self, value):
        # print(f"center: set {value}")
        with self.rlock:
            self._center = value

    def get_visual(self, universe, size_cl):
        offset_cl = (size_cl[0] // 2, size_cl[1] // 2)
        # (min_x, max_y) is correct since line 0 represents the maximum y value
        (min_x, max_y) = cl_to_xy((0, 0), offset_cl, self._center, self.scale)
        (max_x, min_y) = cl_to_xy(size_cl, offset_cl, self._center, self.scale)
        bbox_xy = ((min_x, min_y), (max_x, max_y))
        visual = dict()
        for body in universe._bodies.values():
            visual.update(body.get_visual(bbox_xy, size_cl, offset_cl, self._center, self.scale, self.zoom))
        return visual

    def show(self, universe):
        (c, l) = os.get_terminal_size()
        l -= 4
        visual = self.get_visual(universe, (c, l))
        out = visual_to_string(visual, (c, l))
        print(out)

def visual_to_string(visual, size_cl):
    out = ""
    for l in range(0, size_cl[1]):
        for c in range(0, size_cl[0]):
            out += visual[(c, l)] if (c, l) in visual else " "
        out += "\n"
    return out

# ===========================================================================

# Planet m  Mercury 0.4  LIGHT_RED     88
# Planet v  Venus   0.7  YELLOW       225
# Planet e  Earth   1.0  LIGHT_BLUE   365
# Planet M  Mars    1.5  RED          687
# Planet c  Ceres   2.8  DARK_GRAY   1682
# Planet J  Jupiter 5.2  YELLOW      4333
# Planet S  Saturn  9.6  YELLOW     10759
# Planet U  Uranus 19.2  LIGHT_CYAN 30687
# Planet N  Neptune 30.0 LIGHT_BLUE 60190
# Planet p  Pluto   39.5 DARK_GRAY  90560

def run_all_tests():
    uni = universe.create_test_universe()
    view = View((0, 0), AU // 150, 4)
    try:
        size_cl = os.get_terminal_size()
        size_cl = (size_cl[0], size_cl[1] - 2)
    except OSError:
        size_cl = (80, 4)
    print("size_cl:", size_cl)
    visual = view.get_visual(uni, size_cl)
    out = visual_to_string(visual, size_cl)
    print(out, end="")

if __name__ == "__main__":
    run_all_tests()