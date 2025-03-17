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
            if radius < 0.05:
                radius = 0.05
            if radius > 0.3:
                radius = 0.3
            circle = plt.Circle(self.uxy_to_pxy(body.position), radius, color=colour, clip_on=False)
            self.bodies[key] = circle

        plt.style.use('dark_background')
        print(f"scale={self.scale:.0f}  width={self.width}\"  height={self.height}\"")
        print(f"1 AU = {1 * AU / self.scale}\"")

        self.fig, self.ax = plt.subplots(figsize=(self.width, self.height))#, facecolor="black", edgecolor="black", frameon=False)
        self.fig.tight_layout()
        plt.gca().set_aspect('equal')
        self.ax.set_axis_off()
        # self.ax.set_frame_on(False)
        self.ax.margins(x=0.0, y=0.0)
        self.ax.set_xlim((-self.width / 2, self.width / 2))
        self.ax.set_ylim((-self.height / 2, self.height / 2))

        for (key, circle) in self.bodies.items():
            print(key, circle)
            self.ax.add_patch(circle)

        if is_running_in_terminal():
            ani = animation.FuncAnimation(fig=self.fig, func=self.update, interval=50)  # 500 ms
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
            #if key == "Earth":
            #    print(self.universe.clock._factor, self.universe.clock.get_time(), key, uxy, pxy)
            circle.center = pxy

# ==================================

def test_plot_view():
    (universe, clock) = u.create_test_universe(start_thread=False)
    clock.start(10 * 86400)
    plot_view = PlotView(universe)
    sys.exit()

if __name__ == "__main__":
    test_plot_view()
