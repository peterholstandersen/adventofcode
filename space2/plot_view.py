from common import *
from utils import *
import matplotlib.animation as animation
import matplotlib.pyplot as plt

from mpl_toolkits.axes_grid1 import Divider, Size
import universe as u
import clock2 as c

#    bodies["Sun"] = SpaceObject("Sun",         ( 0, 0),        YELLOW,     "*", 696340, "star_sun.png", None)
#    bodies["Mercury"] = SpaceObject("Mercury", ( 0.4 * AU, 0), DARK_GRAY,  "m",   2440, "...", Orbit("Sun",  0.4 * AU,    88))
#    bodies["Venus"] =   SpaceObject("Venus",   ( 0.7 * AU, 0), YELLOW,     "v",   6000, "...", Orbit("Sun",  0.7 * AU,   225))
#    bodies["Earth"] =   SpaceObject("Earth",   ( 1.0 * AU, 0), BLUE,       "e",   6400, "...", Orbit("Sun",  1.0 * AU,   365))
#    bodies["Mars"] =    SpaceObject("Mars",    ( 1.5 * AU, 0), RED,        "m",   6400, "...", Orbit("Sun",  1.5 * AU,   687))
#    bodies["Ceres"] =   SpaceObject("Ceres",   ( 2.8 * AU, 0), DARK_GRAY,  "c",    490, "...", Orbit("Sun",  2.8 * AU,  1682))
#    bodies["Jupiter"] = SpaceObject("Jupiter", ( 5.2 * AU, 0), BROWN,      "J",  70000, "...", Orbit("Sun",  5.2 * AU,  4333))
#    bodies["Saturn"] =  SpaceObject("Saturn",  ( 9.6 * AU, 0), YELLOW,     "S",  58000, "...", Orbit("Sun",  9.6 * AU, 10759))
#    bodies["Uranus"] =  SpaceObject("Uranus",  (19.2 * AU, 0), LIGHT_CYAN, "U",  15800, "...", Orbit("Sun", 19.2 * AU, 30687))
#    bodies["Neptun"] =  SpaceObject("Neptun",  (30.0 * AU, 0), LIGHT_BLUE, "N",  15300, "...", Orbit("Sun", 30.0 * AU, 60190))
#    bodies["Pluto"] =   SpaceObject("Pluto",   (39.5 * AU, 0), DARK_GRAY,  "p",   2400, "...", Orbit("Sun", 39.5 * AU, 90560))

# TODO
ansi_to_colour = {
    YELLOW: "yellow",
    DARK_GRAY: "grey",
    BLUE: "blue",
    RED: "red",
    BROWN: "brown",
    LIGHT_CYAN: "cyan",
    LIGHT_BLUE: "blue",
}

class PlotView:
    def __init__(self, universe):
        self.universe = universe
        self.bodies = dict()
        self.height = self.width = 16 # 2048/4*3*self.px
        self.scale = 10 * AU / self.width
        for (key, body) in universe.bodies.items():
            colour = ansi_to_colour.get(body.colour, "white")
            # body.radius is K km
            radius = body.radius / 500000
            if radius < 0.02:
                radius = 0.02
            if radius > 0.3:
                radius = 0.3
            circle = plt.Circle(self.uxy_to_pxy(body.position), radius, color=colour, clip_on=False)
            self.bodies[key] = circle

        plt.style.use('dark_background')
        print(f"scale={self.scale:.0f}  width={self.width}\"  height={self.height}\"")
        print(f"1 AU = {1 * AU / self.scale}\"")

        # self.fig, self.ax = plt.subplots(figsize=(self.width, self.height), subplot_kw = {"projection": "3d"})
        self.fig, self.ax = plt.subplots(figsize=(self.width, self.height))

        self.fig.tight_layout()
        plt.gca().set_aspect('equal')
        self.ax.set_axis_off()
        self.ax.margins(x=0.0, y=0.0)
        self.ax.set_xlim((-self.width / 2, self.width / 2))
        self.ax.set_ylim((-self.height / 2, self.height / 2))

        for (key, circle) in self.bodies.items():
            print(key, circle)
            self.ax.add_patch(circle)

        if is_running_in_terminal():
            ani = animation.FuncAnimation(fig=self.fig, func=self.update, interval=50, cache_frame_data=False)  # 500 ms
            plt.show()

    def uxy_to_pxy(self, uxy):
        (ux, uy) = uxy
        (x, y) = (ux / self.scale + self.width / self.scale, uy / self.scale + self.height / self.scale)
        return (x, y)

    def update(self, frame):
        self.universe.update()
        for (key, circle) in self.bodies.items():
            body = self.universe.bodies[key]
            uxy = body.position
            pxy = self.uxy_to_pxy(uxy)
            circle.center = pxy

class PlotView3D:
    def __init__(self, universe):
        self.brightness = 0.75
        self.universe = universe
        self.size = 800
        self.fig, self.ax = plt.subplots(1, 1, figsize=(self.size / 50, self.size / 50), subplot_kw={"projection": "3d"})
        self.fig.tight_layout()

        # self.ax.set_proj_type('persp', focal_length=1)

        self.fig.set_facecolor('black')
        self.ax.set_facecolor('black')
        self.ax.grid(False)
        self.ax.xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        self.ax.yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        self.ax.zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))

        self.ax.view_init(elev=20, azim=45)
        self.scale = 1 * AU
        self.max_x = 0
        self.max_y = 0
        self.max_z = 0

        to_draw = ["Sun", "Mercury", "Venus", "Earth", "Mars"]
        for body in self.universe.bodies.values():
            if body.name not in to_draw:
                continue
            uxy = body.position
            (x, y) = self.uxy_to_pxy(uxy)
            z = 0
            self.max_x = max(self.max_x, abs(x))
            self.max_y = max(self.max_y, abs(y))
            self.max_z = max(self.max_z, abs(z))

        random.seed(1000)
        for degree in range(0, 360):
            (x, y) = (math.sin(math.radians(degree)), math.cos(math.radians(degree)))
            distance = random.randint(round(2.5 * AU), round(3.2 * AU))
            (x, y) = (x * distance, y * distance)
            (x, y) = self.uxy_to_pxy((x, y))
            self.max_x = max(self.max_x, abs(x))
            self.max_y = max(self.max_y, abs(y))

        self.draw_bodies()

        if is_running_in_terminal():
            ani = animation.FuncAnimation(fig=self.fig, func=self.update_all, interval=50, cache_frame_data=False)  # 500 ms
            plt.show()

    # TODO:
    # - shadows
    # - stars
    # - text below space objects (see iPad)
    # - crafts
    # - move view point
    # - asteroids (orbit)
    # - moons?
    # - integrate with command.py
    # - scale + zoom (+++/---) / enhance
    # - center, track
    #
    # - use z-plane (pluto, and others?)
    # - draw furthest away first

    def uxy_to_pxy(self, uxy):
        (ux, uy) = uxy
        (x, y) = (ux / self.scale + self.size / self.scale, uy / self.scale + self.size / self.scale)
        return (x, y)

    def uxyz_to_pxyz(self, uxyz):
        (ux, uy, uz) = uxyz
        (x, y, z) = (ux / self.scale + self.size / self.scale, uy / self.scale + self.size / self.scale, uz / self.scale)
        return (x, y, z)

    def draw_bodies(self, frame=0):
        self.ax.clear()
        self.ax.set_xlim((-self.max_x, self.max_x))
        self.ax.set_ylim((-self.max_y, self.max_y))
        self.ax.set_zlim((-self.size / 2, self.size / 2))
        self.ax.grid(False)

        to_draw = ["Sun", "Mercury", "Venus", "Earth", "Mars", "Ceres"]
        for body in self.universe.bodies.values():
            if body.name not in to_draw:
                continue
            uxy = body.position
            (x, y) = self.uxy_to_pxy(uxy)
            z = 0
            size = body.radius / 500
            if size > 30:
                size = 30
            if body.name == "Sun":
                colour = "#f29f05"
            elif body.name == "Mercury":
                colour = "#d1cfc8"
            elif body.name == "Venus":
                colour = "#fade7c"
            elif body.name == "Earth":
                colour = "#023ca7"
            elif body.name == "Mars":
                colour = "#b82020"
            else:
                colour = ansi_to_colour.get(body.colour, (0.5, 0.5, 0.5))
            if body.name == "Ceres":
                size = 2
                colour = "#707070"

            if body.name != "Sun":
                colour = "#" + ("".join([f"{round(eval('0x' + colour[i:i + 2]) * self.brightness):02X}" for i in [1, 3, 5]]))

            self.ax.plot(x, y, z, marker="o", markersize=size, color=colour) # z was -self.size / 2

        random.seed(1000)
        for degree in range(0, 360):
            distance = random.randint(round(2.5 * AU), round(3.2 * AU))
            offset = (frame / (5*16)) * (3.2 * AU)**3 / distance**3
            z = random.randint(-round(0.1 * AU), round(0.1 * AU))
            # z = 0
            (x, y) = (math.sin(math.radians(degree - offset)), math.cos(math.radians(degree - offset)))
            (x, y) = (x * distance, y * distance)
            (x, y, z) = self.uxyz_to_pxyz((x, y, z))
            self.ax.plot(x, y, z, marker="o", markersize=1, color="#505050")



    def update_all(self, frame):
        self.universe.update()
        #print(frame)
        self.draw_bodies(frame)

# ==================================

def test_plot_view():
    (universe, clock) = u.create_test_universe(start_thread=False)
    clock.start(86400)
    plot_view = PlotView(universe)
    sys.exit()

def test_plot_view_3d():
    (universe, clock) = u.create_test_universe(start_thread=False)
    clock.start(86400 // 4)
    x = PlotView3D(universe)
    #x.update_all()
    #x.draw_all()
    # time.sleep(100000000)

if __name__ == "__main__":
    # test_plot_view()
    test_plot_view_3d()

