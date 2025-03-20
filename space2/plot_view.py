from common import *
from utils import *
import universe as u
import sys
import itertools
import matplotlib.animation as animation
import matplotlib.pyplot as plt

class PlotView3D:
    def __init__(self, universe, start_thread=False):
        self.focal_length = 0.3
        self.elev = 20
        self.azim = 45
        self.universe = universe
        self.fig, self.ax = plt.subplots(1, 1, figsize=(16, 16), subplot_kw={"projection": "3d"})
        self.fig.tight_layout()
        self.ax.set_proj_type('persp', focal_length=self.focal_length)
        self.fig.set_facecolor('black')
        self.ax.set_facecolor('black')
        self.ax.grid(False)
        self.ax.xaxis.set_pane_color("black")
        self.ax.yaxis.set_pane_color("black")
        self.ax.zaxis.set_pane_color("black")
        self.ax.view_init(elev=self.elev, azim=self.azim)

        # zoom_factor, scale, enhance
        self.zoom_factor = 3 # view +/- 3 AU from Sun
        self.scale = self.zoom_factor * AU
        self.enhance = self.zoom_factor * AU / 500
        self.width = self.scale
        self.height = self.scale
        self.depth = self.scale // 2
        self.ax.set_xlim((-self.width / 2, self.width / 2))
        self.ax.set_ylim((-self.height / 2, self.height / 2))
        self.ax.set_zlim((-self.depth / 2, self.depth / 2))
        self.ax.grid(False)

        self.draw_bodies()
        self.animation = animation.FuncAnimation(fig=self.fig, func=self.update_all, interval=50, cache_frame_data=False)
        plt.show()

    def _get_plot_size(self, radius):
        size = radius / self.scale * self.enhance / self.zoom_factor
        if size > 1:
            size = size ** 0.5
        if size > 100 / self.zoom_factor:
            size = 100 / self.zoom_factor
        if size < 1 / self.zoom_factor:
            size = 1 / self.zoom_factor
        return size

    def draw_bodies(self, frame=0):
        plt.cla()
        self.ax.grid(False)
        for (sx, sy, sz) in itertools.product([-1,1], [-1,1], [-1,1]):
            self.ax.plot(sx * self.width / 2, sy * self.height / 2, sz * self.depth / 2, marker="o", markersize=0.01, color="#000000")

        for body in self.universe.bodies.values():
            (x, y) = body.position
            z = 0
            size = self._get_plot_size(body.radius)
            if abs(x) <= self.width and abs(y) <= self.height and abs(z) <= self.depth:
                self.ax.plot(x, y, z, marker="o", markersize=size, color=body.rgb_colour)

        random.seed(1000)
        for degree in range(0, 360):
            distance = random.randint(round(2.5 * AU), round(3.2 * AU))
            offset = (frame / (5*16)) * (3.2 * AU)**3 / distance**3
            z = random.randint(-round(0.1 * AU), round(0.1 * AU))
            (x, y) = (math.sin(math.radians(degree - offset)), math.cos(math.radians(degree - offset)))
            (x, y) = (x * distance, y * distance)
            z = 0
            radius = 100
            size = self._get_plot_size(radius)
            if size > 0.3 / self.zoom_factor:
                size = 0.3 / self.zoom_factor
            size = 1
            self.ax.plot(x, y, z, marker="o", markersize=size, color="#505050")

    def update_all(self, frame):
        self.universe.update()
        self.draw_bodies(frame)

# ==================================

def create_plot_view_3d(universe):
    return PlotView3D(universe)

def test_plot_view_3d():
    (universe, clock) = u.create_test_universe(start_thread=False)
    clock.start(86400 // 4)
    x = create_plot_view_3d(universe)

if __name__ == "__main__":
    test_plot_view_3d()
