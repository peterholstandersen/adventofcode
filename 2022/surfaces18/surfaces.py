import sys
import time

def get_dimension(block):
    if type(block) is int:
        return 1
    else:
        return len(block)

def get_surfaces_on_block(block):
    surfaces = None
    dimension = get_dimension(block)
    if dimension == 1:
        x = block
        surfaces = [ (x-1,x), (x,x+1) ]
    elif dimension == 2:
        (x, y) = block
        surfaces = []
        for (dx,dy) in [ (-1,0), (0,1), (1,0), (0,-1) ]:
            surfaces.append( ( (x,y), (x+dx, y+dy) ))
    elif dimension == 3:
        (x, y, z) = block
        surfaces = []
        for (dx,dy,dz) in [ (-1,0,0), (1,0,0), (0,-1,0), (0,1,0), (0,0,-1), (0,0,1) ]:
            surfaces.append( ( (x,y,z), (x+dx,y+dy,z+dz) ))
    else:
        print("Unhandled dimension: ", len(block))
        sys.exit(1)
    return surfaces

def register_surface(surfaces, surface):
    (coord1, coord2) = surface
    key = (coord1, coord2) if (coord1 < coord2) else (coord2, coord1)
    surfaces[key] = surfaces.get(key, 0) + 1

def doit(blocks):
    surfaces = dict()
    for block in blocks:
        for surface in get_surfaces_on_block(block):
            register_surface(surfaces, surface)
    free_surfaces = 0
    for surface in surfaces:
        if surfaces.get(surface, None) == 1:
            free_surfaces += 1
    print(free_surfaces)

def get_neighbours(block):
    (x, y, z) = block
    neighbours = []
    for (dx,dy,dz) in [ (-1,0,0), (1,0,0), (0,-1,0), (0,1,0), (0,0,-1), (0,0,1) ]:
        neighbours.append( (x+dx,y+dy,z+dz) )
    return neighbours

def doit2(blocks):
    count = 0
    for block in blocks:
        for neighbour in get_neighbours(block):
            if not neighbour in blocks:
                count += 1
    return count

def example():
    blocks = [ (2,2,2), (1,2,2), (3,2,2), (2,1,2), (2,3,2), (2,2,1),
               (2,2,3), (2,2,4), (2,2,6), (1,2,5), (3,2,5), (2,1,5),
               (2,3,5)
    ]
    return blocks

def main():
    filename = "small.in"; expected_count = 64
    filename = "big.in";   expected_count = 4332

    blocks = []
    with open(filename) as file:
        for line in file:
            if len(line) == 0:
                continue
            block = line.strip().split(",")
            blocks.append( (int(block[0]), int(block[1]), int(block[2])) )

    print(f"{filename}: read {len(blocks)} blocks")

    start_time = time.time()
    count = doit2(blocks)
    print(f"count = {count}:", "ok" if count == expected_count else f"not ok: expected {expected_count}")
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    main()