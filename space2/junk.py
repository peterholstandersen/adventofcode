# Asteroid belt -- work in progress
random.seed(1000)
for degree in range(0, 360):
    distance = random.randint(round(2.5 * AU), round(3.2 * AU))
    offset = (frame / (5 * 16)) * (3.2 * AU) ** 3 / distance ** 3
    z = random.randint(-round(0.1 * AU), round(0.1 * AU))
    (x, y) = (math.sin(math.radians(degree - offset)), math.cos(math.radians(degree - offset)))
    (x, y) = (x * distance, y * distance)
    z = 0
    if abs(x) <= self.width / 2 and abs(y) <= self.height / 2 and abs(z) <= self.depth / 2:
        self.ax.plot(x, y, z, marker="o", markersize=1, color="#505050")

self.ax.set_aspect('equal')

class Orbit(Course):
    center = None
    distance = None
    orbit_time = None

    def __init__(self, center, distance, orbit_time, *args):
        self.center = center
        self.distance = distance
        self.orbit_time = orbit_time
        super().__init__(*args)

    def calculate_position(self, universe, _, __, now):
        center_xyz = universe.get_body_position(self.center)
        if center_xyz is None:
            print(f"{self.center} is lost in space.")
            return None
        else:
            (x, y, z) = center_xyz
            day = (now + hash(self)) / 86400
            angle = math.radians(360) - math.radians(360) * (float(day % self.orbit_time) / float(self.orbit_time))
            dx = math.sin(angle) * self.distance
            dy = math.cos(angle) * self.distance
            return (x + dx, y + dy, z)

    def view(self, now=0):
        return ""


def fun():
    theta = np.linspace(0, 2 * np.pi, resolution)
    x = a * np.cos(theta)
    y = b * np.sin(theta)
    z = 0
    # Now for some matrix fun
    plt.plot(x1, y1, z1, "-")


def more_or_less_fun():
        # Orbital elements: https://astronomy.swin.edu.au/cosmos/O/Orbital+Elements
        eee = eccentricity = 0.205630
        a = semimajor_axis = 57.909e+06
        # b = semiminor_axis = a * sqrt(1 - e**2) ... can be decuded from longtitude of perihelion

        I = inclination = math.radians(7.005)
        w_bar = longtitude_of_perihelion = math.radians(77.45771895)
        Omega = longtitude_ascending_node = math.radians(48.33961819)

        T = centuries_past_J2000 = ...

        # Perihelion: the point in the orbital path of a heavenly body that is nearest to the sun
        #
        # Longtitude of the perihelion (lowercase omega with a bar: w_bar): Det er nok hvor langt der er fra focus til perihelion
        #
        # Ascending node (Omega) (https://astronomy.swin.edu.au/cosmos/A/Ascending+Node): The ascending node is usually
        # quoted  as the angular position at which a celestial body passes from the southern side of a reference plane
        # to the northern side, hence ‘ascending'
        #
        # Argument of the perihelion (lowercase omega: w) is the rotation angle around the z-axis (i.e., in the x-y plane) around the focus
        # - https://astronomy.swin.edu.au/cosmos/a/argument+of+perihelion

        # Compute the argument of perihelion (lowercase omega: w)
        w = w_bar - Omega

        # and the mean anomaly (M): the period that has lapsed since the body passed perihelion (says something about the speed of the object)
        M = L - w_bar + b*T**2

        # If we rotate the axis of the orbit around the focus, then the rotation angle is the argument of perihelion (ω).


        # ???????
        T = (T_eph - 2451545) / 36525
        M = L - w + b*T**2 + c*cos(fT) + s*sin(fT)
        # find E where: M = E - e_star * sin(E), where e_star = 180 / pi * e = 57.29578 * e
        #p = orbital_period = 87.9691  # sidereal (in relation to close star)
        #M = mean_anolomy = 174.796    # degrees
        # ?????

        x = a * (cos(E) - e)
        y = a * sqrt(1 - e**2) * sin(E)
        z = 0

        x_ecl = (cos(w)*cos(O) - sin(w)*sin(O)*cos(I)) * x + (-sin(w)*cos(O) - cos(w)*sin(O)*cos(I)) * y
        y_ecl = (cos(w)*sin(O) + sin(w)*cos(O)*cos(I)) * x + (-sin(w)*sin(O) + cos(w)*cos(O)*cos(I)) * y
        z_ecl = (sin(w)*sin(I)) * x + (cos(w)*sin(I)) * y


# Create two 3D polygons
v1 = np.array([ [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0.5, 0.5, 1] ])
vertices2 = np.array([
    [1.5, 1.5, 0],
    [2.5, 1.5, 0],
    [2.5, 2.5, 0],
    [1.5, 2.5, 0],
    [2, 2, 1]
])
faces = np.array([
    [0, 1, 4],
    [1, 2, 4],
    [2, 3, 4],
    [3, 0, 4],
    [0, 1, 2]
])
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_trisurf(vertices1[:, 0], vertices1[:, 1], vertices1[:, 2], triangles=faces, color='r', alpha=0.5)
ax.plot_trisurf(vertices2[:, 0], vertices2[:, 1], vertices2[:, 2], triangles=faces, color='b', alpha=0.5)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.title('Multiple 3D Polygons')
plt.show()


self.max_x = 0
self.max_y = 0
self.max_z = 0
for body in self.universe.bodies.values():
    if body.name not in self.to_draw:
        continue
    (ux, uy) = body.position
    (x, y, z) = self.uxyz_to_pxyz((ux, uy, 0))
    self.max_x = max(self.max_x, abs(x))
    self.max_y = max(self.max_y, abs(y))
    self.max_z = max(self.max_z, abs(z))
print(self.max_x, self.max_y, self.max_z)

random.seed(1000)
for degree in range(0, 360):
    (x, y) = (math.sin(math.radians(degree)), math.cos(math.radians(degree)))
    distance = random.randint(round(2.5 * AU), round(3.2 * AU))
    (x, y) = (x * distance, y * distance)
    (x, y, _) = self.uxyz_to_pxyz((x, y, 0))
    # self.max_x = max(self.max_x, abs(x))
    # self.max_y = max(self.max_y, abs(y))


# print(self.max_x, self.max_y, self.max_z)


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
            ani = animation.FuncAnimation(fig=self.fig, func=self.update, interval=50, cache_frame_data=False)
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



def foo():
    radius = self.radius * enhance
    if min_x - radius <= x <= max_x + radius and min_y - radius <= y <= max_y + radius:
        (min_c, max_l) = xy_to_cl((x - radius, y - radius), offset_cl, center_xy, scale)
        (max_c, min_l) = xy_to_cl((x + radius, y + radius), offset_cl, center_xy, scale)
        min_c = max(0, min_c)
        min_l = max(0, min_l)
        max_c = min(size_cl[0], max_c)
        max_l = min(size_cl[1], max_l)
        print(self.visual, scale, center_xy, radius, enhance, min_c, max_c, min_l, max_l)
        if min_c == max_c and min_l == max_l:
            visual[(min_c, min_l)] = self.visual
            return visual
        for c in range(min_c, max_c + 1):
            for l in range(min_l, max_l + 1):
                xy = cl_to_xy((c, l), offset_cl, center_xy, scale)
                print(self.visual, c, l, distance(xy, self.position), radius)
                if distance(xy, self.position) <= radius:
                    visual[(c, l)] = self.visual
                else:
                    visual[(c, l)] = "."
        return visual


def get_visual(self, bbox_xy, size_cl, offset_cl, center_xy, scale, enhance=1):
    visual = dict()
    ((min_x, min_y), (max_x, max_y)) = bbox_xy
    radius = self.radius * enhance
    (x, y) = self.position
    if min_x - radius <= x <= max_x + radius and min_y - radius <= y <= max_y + radius:
        (min_c, max_l) = xy_to_cl((x - radius, y - radius), offset_cl, center_xy, scale)
        (max_c, min_l) = xy_to_cl((x + radius, y + radius), offset_cl, center_xy, scale)
        min_c = max(0, min_c)
        min_l = max(0, min_l)
        max_c = min(size_cl[0], max_c)
        max_l = min(size_cl[1], max_l)
        print(self.visual, scale, center_xy, radius, enhance, min_c, max_c, min_l, max_l)
        if min_c == max_c and min_l == max_l:
            visual[(min_c, min_l)] = self.visual
            return visual
        for c in range(min_c, max_c + 1):
            for l in range(min_l, max_l + 1):
                xy = cl_to_xy((c, l), offset_cl, center_xy, scale)
                print(self.visual, c, l, distance(xy, self.position), radius)
                if distance(xy, self.position) <= radius:
                    visual[(c, l)] = self.visual
                else:
                    visual[(c, l)] = "."
    return visual


def _get_visual(self, universe, size_cl):
    offset_cl = (size_cl[0] // 2, size_cl[1] // 2)
    # (min_x, max_y) is correct since line 0 represents the maximum y value
    (min_x, max_y) = cl_to_xy((0, 0), offset_cl, self.center, self.scale)
    (max_x, min_y) = cl_to_xy(size_cl, offset_cl, self.center, self.scale)
    bbox_xy = ((min_x, min_y), (max_x, max_y))
    visual = dict()
    for body in universe.bodies.values():
        visual.update(body.get_visual(bbox_xy, size_cl, offset_cl, self.center, self.scale, self.enhance))
    return visual


# move to utils
def match_and_get(pattern, text, getter):
    match = re.match(pattern, text)
    if match:
        return getter(match)
    return None

def parse_relative_position(universe, text):
    text = text.strip()
    xy = parse_absolute_position(universe, text)
    foo = match_and_get(rf"{number}\s*d\s*{number}", text, lambda match: match.groups())
    if foo:
        (degrees, dist) = (float(foo[0]), float(foo[1]))
        print("ddxyz:", degrees, dist)
    else:
        print("ddxyz:", None)
    return (0,0)

def parse_absolute_position(universe, text):
    text = text.replace(" ", "")
    xy = match_and_get(coords, text, lambda match: (float(match.group(1)), float(match.group(2))))
    if not xy:
        xy = match_and_get(ident, text, lambda match: universe.get_body_position(match.group(1)))
    return xy
