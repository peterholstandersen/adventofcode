import sys
from common import *
from utils import *
import universe as u
import course as c
from matplotlib.colors import LightSource, ListedColormap, to_rgb, to_hex
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import math

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
        self.reset_view()

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
        new_azim = self.ax.azim if azim is None else int(self.ax.azim + azim)
        new_elev = self.ax.elev if elev is None else int(self.ax.elev + elev)
        self.ax.view_init(elev=new_elev, azim=new_azim)
        return (self.ax.azim, self.ax.elev)

    def set_view_point(self, azim=None, elev=None):
        new_azim = self.ax.azim if azim is None else azim
        new_elev = self.ax.elev if elev is None else elev
        self.ax.view_init(elev=new_elev, azim=new_azim)
        return (self.ax.azim, self.ax.elev)

    def plot_craft(self, pos, size, lightsource):
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

        self.ax.plot_trisurf(vertices1[:, 0], vertices1[:, 1], vertices1[:, 2], triangles=front, color='#909090', alpha=1, lightsource=lightsource)
        self.ax.plot_trisurf(vertices1[:, 0], vertices1[:, 1], vertices1[:, 2], triangles=body, color='#808080', alpha=1, lightsource=lightsource)
        self.ax.plot_trisurf(vertices1[:, 0], vertices1[:, 1], vertices1[:, 2], triangles=aft, color='#fc272f', alpha=1, lightsource=lightsource)

    def plot_trajectory(self, body):
        return
        now = self.universe._last_update
        if type(body.course) is c.Orbit:
            positions = []
            for theta in np.linspace(0, 2 * math.pi, 360):
                day = theta / body.course.dM # dM is radians per day
                timestamp = now + day * 24 * 3600
                positions.append(body.course.calculate_position(self.universe, None, None, timestamp))
            (xs, ys, zs) = (
                [pos[0] for pos in positions],
                [pos[1] for pos in positions],
                [pos[2] for pos in positions]
            )
            self.ax.plot(xs, ys, zs)

    def compute_lightsource(self, x, y, z):
        if x == 0:
            degrees = 90 if y > 0 else 270
        else:
            degrees = math.degrees(math.atan(y / x))
            if x < 0:
                degrees += 180
        degrees = - degrees - 90
        xy = math.sqrt(x ** 2 + y ** 2)
        altdeg = math.degrees(math.atan(-z / xy)) if xy != 0 else (-90 if z > 0 else 90)
        return LightSource(azdeg=degrees, altdeg=altdeg)

    def draw_bodies(self, frame=0):
        plt.cla()
        self.set_scale(self.scale)
        (min_x, max_x) = self.ax.get_xlim()
        (min_y, max_y) = self.ax.get_ylim()
        (min_z, max_z) = self.ax.get_zlim()

        for body in self.universe.bodies.values():
            (x, y, z) = body.position
            if x < min_x or x > max_x or y < min_y or y > max_y or z < min_z or z > max_z:
                continue
            if (x, y, z) == (0, 0, 0):
                shade = False
                lightsource = None
            else:
                shade = True
                lightsource = self.compute_lightsource(x, y, z)
            # The larger the exponent, the bigger the difference
            size = body.radius ** 0.3 * 250_000
            if size > 40_000_000:
                size = 40_000_000
            if body.name == "Heroes":
                self.plot_craft((x, y, z), size=size, lightsource=lightsource)
                continue
            colour_map = body.colour_map
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
            self.ax.plot_surface(x, y, z, color=body.rgb_colour, linewidth=0, antialiased=False, lightsource=lightsource, shade=shade, cmap=colour_map)
            self.ax.set_aspect('equal')
        return

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
