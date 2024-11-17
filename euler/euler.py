import sys
import math
import itertools
import statistics as stat

def read_coords(filename):
    return [(float(x), float(y)) for (x, y) in [line.split(" ") for line in open(filename).read().strip().split("\n")]]

def read_it():
    nodes = read_coords("nodes")
    nodes.sort()
    node_ids = dict(zip(nodes, range(0, len(nodes) + 1)))  # mapping from (lattitude, longtitude) to id
    walk1 = read_coords("Euler_1.txt")
    dist1 = compute_distances_in_walk(walk1)
    walk2 = average_walk(walk1, 3)
    dist2 = compute_distances_in_walk(walk2)
    print("walk1:", walk1)
    print("walk2:", walk2)
    print("dist2:", dist2)
    print("dist1:", dist1)
    return(nodes, node_ids, walk2)
    # How close are the nodes?
    all_distances = [geo_dist(loc1, loc2) for (loc1, loc2) in itertools.product(nodes, nodes) if loc1 != loc2]
    all_distances.sort()
    print(all_distances)
    print()

def geo_dist(loc1, loc2):
    (lat1, lon1) = loc1
    (lat2, lon2) = loc2
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    lon1 = math.radians(lon1)
    lon2 = math.radians(lon2)
    sin = math.sin
    cos = math.cos
    return math.acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon2-lon1))*6371000
    #print(geo_dist((55.76115, 12.17849), (55.76111, 12.17893)))
    #sys.exit(1)

# Compute a moving average over the coordinates
def average_walk(walk, window_size):
    lats = [lat for (lat, lon) in walk]
    lons = [lon for (lat, lon) in walk]
    new_lats = [stat.mean(lats[i:i + window_size]) for i in range(0, len(lats) - window_size)]
    new_lons = [stat.mean(lons[i:i + window_size]) for i in range(0, len(lons) - window_size)]
    new_walk = list(zip(new_lats, new_lons))
    return new_walk

def compute_distances_in_walk(walk):
    bar = [geo_dist(loc1, loc2) for (loc1, loc2) in zip(walk, walk[1:])]
    bar.sort(reverse=True)
    return bar

def print_bbox(nodes):
    min_lat = min([lat for (lat, _) in nodes])
    max_lat = max([lat for (lat, _) in nodes])
    print(min_lat, max_lat, max_lat - min_lat)
    min_long = min([long for (_, long) in nodes])
    max_long = max([long for (_, long) in nodes])
    print(min_long, max_long, max_long - min_long)

def pesudo_dist(loc1, loc2):
    (y1, x1) = loc1
    (y2, x2) = loc2
    dy = y1 - y2
    dx = x1 - x2
    return dy * dy + dx * dx

def doit(nodes, node_ids, walk):
    path = []
    started = False
    for (location, index) in zip(walk, range(0, len(walk) + 1)):
        # find the closest node in nodes
        a = [ (geo_dist(location, node), node) for node in nodes ]
        a.sort()
        b = [(node_ids[node], round(distance, 2)) for (distance, node) in a]
        (node, distance) = b[0]
        if distance > 5.0:
            continue
        if (not started and distance < 5.0):
            started = True
            path.append(node)
            continue
        if started:
            if path[-1] != node:
                path.append(node)
    print(path)

    # https://www.google.com/maps/dir/33.93729,-106.85761/33.91629,-106.866761/33.98729,-106.85861//@34.0593359,-106.7131944,11z

    # https://www.google.com/maps/dir/33.93729,-106.85761/33.91629,-106.866761/33.98729,-106.85861//@34.0593359,-106.7131944,73375m/data=!3m1!1e3?entry=ttu&g_ep=EgoyMDI0MTExMy4xIKXMDSoASAFQAw%3D%3D

    url = "https://www.google.com/maps/dir"

    # path = path[0:2]

    for point in path:
        (lat, lon) = nodes[point]
        url += f"/{lat},{lon}"

    point = path[-1]
    (lat, lon) = nodes[point]
    url += f"//@{lat},{lon},17z"

    print(url)
    sys.exit(1)

    for point in path:
        (lat, lon) = nodes[point]
        print(f"{point}: http://www.openstreetmap.org/?&mlat={lat}&mlon={lon}#map=19/{lat}/{lon}")

def main():
    (nodes, node_ids, walk) = read_it()
    doit(nodes, node_ids, walk)

main()