from common import *
from utils import *
import universe as u
import sys
import itertools
import matplotlib
from matplotlib.colors import LightSource, ListedColormap, to_rgb, to_hex
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import math
import matplotlib.tri as tri

class PlotView3D:
    universe = None
    animation = None
    focal_length = 0.3
    elev = 20
    azim = 45
    scale = None
    width = None
    height = None
    depth = None
    center = (0, 0, 0)
    track = None

    def __init__(self):
        self.fig, self.ax = plt.subplots(1, 1, figsize=(16, 16), subplot_kw={"projection": "3d"})
        self.fig.tight_layout()
        self.ax.set_proj_type('persp', focal_length=self.focal_length)
        self.fig.set_facecolor('black')
        self.ax.set_facecolor('black')
        self.ax.xaxis.set_pane_color("black")
        self.ax.yaxis.set_pane_color("black")
        self.ax.zaxis.set_pane_color("black")
        self.set_scale(3 * AU)
        viridis_big = matplotlib.colormaps['viridis']
        self.uranus_colour_map = ListedColormap(viridis_big(np.linspace(0.25, 0.75, 128)))

    def start_animation(self):
        self.animation = animation.FuncAnimation(fig=self.fig, func=self.update_all, interval=500, cache_frame_data=False)
        plt.show()

    def set_scale(self, scale):
        self.scale = scale
        self.width = self.scale
        self.height = self.scale
        self.depth = self.scale // 2
        self.update_center()
        self.ax.set_xlim((-self.width  // 2 + self.center[0], self.width  // 2 + self.center[0]))
        self.ax.set_ylim((-self.height // 2 + self.center[1], self.height // 2 + self.center[1]))
        self.ax.set_zlim((-self.depth  // 2 + self.center[2], self.depth  // 2 + self.center[2]))
        self.ax.grid(False)

    def update_center(self):
        if self.track:
            body = self.universe.bodies.get(self.track, None)
            if body:
                self.center = body.position
            else:
                print(f"{self.track} is lost in space, stopped tracking")
                self.track = None

    def reset_view(self):
        self.set_scale(3 * AU)
        self.center = (0, 0, 0)
        self.track = None
        self.ax.view_init(elev=20, azim=45)

    def adjust_view_point(self, azim=None, elev=None):
        new_azim = self.ax.azim if azim is None else (self.ax.azim + azim)
        new_elev = self.ax.elev if elev is None else (self.ax.elev + elev)
        new_azim = min(new_azim, 90)
        new_azim = max(new_azim, -90)
        new_elev = new_elev % 360
        self.ax.view_init(elev=new_elev, azim=new_azim)
        return (self.ax.azim, self.ax.elev)

    def set_view_point(self, azim=None, elev=None):
        new_azim = self.ax.azim if azim is None else azim
        new_elev = self.ax.elev if elev is None else elev
        self.ax.view_init(elev=new_elev, azim=new_azim)
        return (self.ax.azim, self.ax.elev)

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
        self.set_scale(self.scale)
        (min_x, max_x) = self.ax.get_xlim()
        (min_y, max_y) = self.ax.get_ylim()
        (min_z, max_z) = self.ax.get_zlim()
        #for (x, y, z) in [ (min_x, min_y, min_z), (max_x, max_y, max_z) ]:
        #    self.ax.plot(x, y, z, marker="o", markersize=1, color="#000000")

        for body in self.universe.bodies.values():
            if len(body.position) != 3:
                print(body.name, body.position)
                sys.exit()
            (x, y, z) = body.position
            if min_x <= x <= max_x and min_y <= y <= max_y and min_z <= z <= max_z:
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
                # The larger the exponent, the bigger the difference
                size = body.radius ** 0.3 * 250_000
                if size > 40_000_000:
                    size = 40_000_000
                if body.name == "Heroes":
                    # print("Heroes at", x, y, z, size)
                    self.plot_craft((x, y, z), size=size)
                    continue
                colour_map = None
                if body.name == "Uranus":
                    colour_map = self.uranus_colour_map
                elif body.name == "Jupiter":
                    custom_colours = ["#977961", "#B9735A", "#DBCAB6", "#DDB099", "#ECD8D1", "#B18F85",
                                      "#9A7E73", "#785F4B", "#977961", "#977961" ]
                    custom_colours = [to_rgb(c) for c in custom_colours ]
                    foo = []
                    for ((r1, g1, b1), (r2, g2, b2), (r3, g3, b3)) in zip(custom_colours, custom_colours[1:], custom_colours[2:]):
                        t = 100
                        n2 = 2
                        for n in range(0, t):
                            n1 = (t - n)
                            n3 = n
                            n2 = (n1 + n3) * 2
                            bar = n1 + n2 + n3
                            foo.append(((r1 * n1 + r2 * n2 + r3 * n3) / bar,
                                        (g1 * n1 + g2 * n2 + g3 * n3 ) / bar,
                                        (b1 * n1 + b2 * n2 + b3 * n3 ) / bar))
                    custom_colours = foo
                    colour_map = ListedColormap(custom_colours)
                max_resolution = 1024 if colour_map else 128
                resolution = round(size/self.scale * 1000) * (4 if colour_map else 1)
                if resolution > max_resolution:
                    resolution = max_resolution
                elif resolution < 20:
                    resolution = 20
                # print(f"{body.name:<10}  {body.radius:>8} km  size: {size:.1f}   size/scale: {size/self.scale:.3f}   resolution={resolution}")
                u = np.linspace(0, 2 * np.pi, resolution)
                v = np.linspace(0, np.pi, resolution)
                x = size * np.outer(np.cos(u), np.sin(v)) + x
                y = size * np.outer(np.sin(u), np.sin(v)) + y
                z = size * np.outer(np.ones(np.size(u)), np.cos(v)) + z
                self.ax.plot_surface(x, y, z, color=body.rgb_colour, linewidth=0, antialiased=False, lightsource=ls, shade=shade, cmap=colour_map)

        self.ax.set_aspect('equal')
        return

        # Asteroid belt -- work in progress
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
