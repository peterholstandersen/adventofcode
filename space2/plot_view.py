from common import *
from utils import *
import universe as u
import sys
import itertools
from matplotlib.colors import LightSource
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import math
import matplotlib.tri as tri

class PlotView3D:
    universe = None
    animation = None
    scale = None
    width = None
    height = None
    depth = None

    def __init__(self):
        self.focal_length = 0.3
        self.elev = 20
        self.azim = 45
        self.fig, self.ax = plt.subplots(1, 1, figsize=(16, 16), subplot_kw={"projection": "3d"})
        self.fig.tight_layout()
        self.ax.set_proj_type('persp', focal_length=self.focal_length)
        self.fig.set_facecolor('black')
        self.ax.set_facecolor('black')
        self.ax.xaxis.set_pane_color("black")
        self.ax.yaxis.set_pane_color("black")
        self.ax.zaxis.set_pane_color("black")
        self.ax.view_init(elev=self.elev, azim=self.azim)
        self.set_scale(3 * AU)

    def start_animation(self):
        self.animation = animation.FuncAnimation(fig=self.fig, func=self.update_all, interval=500, cache_frame_data=False)
        plt.show()

    def set_scale(self, scale):
        self.scale = scale
        self.width = self.scale
        self.height = self.scale
        self.depth = self.scale // 2
        self.ax.set_xlim((-self.width / 2, self.width / 2))
        self.ax.set_ylim((-self.height / 2, self.height / 2))
        self.ax.set_zlim((-self.depth / 2, self.depth / 2))
        self.ax.grid(False)

    def plot_craft(self, pos, size):
        x = np.array([1, 0, 0])
        y = np.array([0, 1, 0])
        z = np.array([0, 0, 1])
        x2 = x / 2
        y2 = y / 2
        z2 = z / 2

        a = np.array([0, 0, 0])
        b = a + x * 3
        c = b + y * 3
        d = c - x * 3
        e = [1.5, 1.5, 4]

        a1 = a - z * 5 + x2 + y2
        b1 = b - z * 5 - x2 + y2
        c1 = c - z * 5 - x2 - y2
        d1 = d - z * 5 + x2 - y2
        f = [1.5, 1.5, -7]

        vertices1 = size * np.array([a, b, c, d, e, a1, b1, c1, d1, f]) + pos
        (A, B, C, D, E, A1, B1, C1, D1, F) = range(0, 10)
        front = np.array([ [A, B, E], [B, C, E], [C, D, E], [D, A, E] ])
        body = np.array([ [A, A1, B1], [B1, B, A], [B, B1, C1], [B, C1, C], [C, C1, D1], [C, D1, D], [A, A1, D1], [A, D1, D] ])
        aft = np.array([ [A1, B1, F], [B1, C1, F], [C1, D1, F], [D1, A1, F] ])

        self.ax.plot_trisurf(vertices1[:, 0], vertices1[:, 1], vertices1[:, 2], triangles=front, color='#909090', alpha=1)
        self.ax.plot_trisurf(vertices1[:, 0], vertices1[:, 1], vertices1[:, 2], triangles=body, color='#808080', alpha=1)
        self.ax.plot_trisurf(vertices1[:, 0], vertices1[:, 1], vertices1[:, 2], triangles=aft, color='#fc272f', alpha=1)

    def draw_bodies(self, frame=0):
        plt.cla()
        self.ax.grid(False)
        for (sx, sy, sz) in itertools.product([-1,1], [-1,1], [-1,1]):
            self.ax.plot(sx * self.width / 2, sy * self.height / 2, sz * self.depth / 2, marker="o", markersize=1, color="#000000")

        for body in self.universe.bodies.values():
            (x, y) = body.position
            z = 0
            if abs(x) <= self.width / 2 and abs(y) <= self.height / 2 and abs(z) <= self.depth / 2:
                if x == 0 and y == 0:
                    shade = False
                    ls = None
                else:
                    shade = True
                    if x == 0:
                        degrees = 90 if y > 0 else 270
                    else:
                        degrees = math.degrees(math.atan(y / x))
                        if x < 0:
                            degrees += 180
                    degrees = - degrees - 90
                    xy = math.sqrt(x ** 2 + y ** 2)
                    altdeg = math.degrees(math.atan(-z / xy)) if xy != 0 else (-90 if z > 0 else 90)
                    ls = LightSource(azdeg=degrees, altdeg=altdeg)
                # enhance: 0.05: tiny, 0.1: small, 0.2: medium-large, 0.3: large, 0.4: very large
                size = body.radius ** 0.22 * 1_000_000
                if size > 40_000_000:
                    size = 40_000_000
                if body.name == "Heroes":
                    # print("Heroes at", x, y, z, size)
                    self.plot_craft((x, y, z), size=size)
                    continue
                resolution = round(size/self.scale * 1000)
                if resolution > 120:
                    resolution = 120
                elif resolution < 20:
                    resolution = 20
                # print(f"{body.name:<10}  {body.radius:>8} km  size: {size:.1f}   size/scale: {size/self.scale:.3f}   resolution={resolution}")
                u = np.linspace(0, 2 * np.pi, resolution)
                v = np.linspace(0, np.pi, resolution)
                x = size * np.outer(np.cos(u), np.sin(v)) + x
                y = size * np.outer(np.sin(u), np.sin(v)) + y
                z = size * np.outer(np.ones(np.size(u)), np.cos(v)) + z
                self.ax.plot_surface(x, y, z, color=body.rgb_colour, linewidth=0, antialiased=False, lightsource=ls, shade=shade)

        self.ax.set_aspect('equal')
        return

        random.seed(1000)
        for degree in range(0, 360):
            distance = random.randint(round(2.5 * AU), round(3.2 * AU))
            offset = (frame / (5*16)) * (3.2 * AU)**3 / distance**3
            z = random.randint(-round(0.1 * AU), round(0.1 * AU))
            (x, y) = (math.sin(math.radians(degree - offset)), math.cos(math.radians(degree - offset)))
            (x, y) = (x * distance, y * distance)
            z = 0
            if abs(x) <= self.width / 2 and abs(y) <= self.height / 2 and abs(z) <= self.depth / 2:
                self.ax.plot(x, y, z, marker="o", markersize=1, color="#505050")

        self.ax.set_aspect('equal')

    def update_all(self, frame):
        if not self.universe.alive:
            print("The Universe is no more")
            sys.exit()
        self.universe.update()
        self.draw_bodies(frame)

# ==================================

def test_plot_view():
    universe = u.big_bang()
    universe.clock.set_factor(86400 // 5)
    universe.plot_view.start_animation()

if __name__ == "__main__":
    test_plot_view()
