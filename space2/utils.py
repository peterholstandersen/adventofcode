from common import *

def cl_to_xy(cl, offset_cl, center_xy, scale):
    x = (cl[0] - offset_cl[0]) * scale + center_xy[0]
    y = (offset_cl[1] - cl[1]) * scale - center_xy[1]
    return (x, y)

def xy_to_cl(xy, offset_cl, center_xy, scale):
    c = round((xy[0] - center_xy[0]) // scale + offset_cl[0])
    l = round((- xy[1] + center_xy[1]) // scale + offset_cl[1])
    return (c, l)

def distance(a, b):
    (x1, y1) = a
    (x2, y2) = b
    xx = x1 - x2
    yy = y1 - y2
    return sqrt(xx * xx + yy * yy)

def safe_float(x):
    try:
        return float(x)
    except (ValueError, TypeError):
        return None

def is_running_in_terminal():
    try:
        os.get_terminal_size()
    except OSError:
        return False
    else:
        return True

# =====================================================================================================

def verify(result, expected, silent=False):
    stack = traceback.extract_stack()
    fs = stack[-2]
    if not silent:
        print(f"{fs.filename.split("/")[-1]}:{fs.lineno}: {fs.line.replace('test(', '')}", end="")
    ok = expected(result) if callable(expected) else (expected == result)
    if ok:
        if not silent:
            print("  OK")
    else:
        print(f"  ERROR. result={result} expected={expected}")
        sys.exit(1)
    return ok

def run_all_tests():
    cl = (0, 0)
    offset_cl = (0, 0)
    center_xy = (0, 0)
    verify(xy_to_cl((1000, 1000), offset_cl, center_xy, scale=1000), (1, -1))
    verify(xy_to_cl((1000, 1000), offset_cl, (1000, 1000), scale=1000), (0, 0))
    verify(xy_to_cl((2000, 2000), offset_cl, (1000, 1000), scale=1000), (1, -1))
    verify(xy_to_cl((2000, 2000), (10, 20), (1000, 1000), scale=1000), (11, 19))
    verify(cl_to_xy((0, 0), offset_cl, center_xy, scale=1), (0, 0))
    verify(cl_to_xy((0, 0), offset_cl, center_xy, scale=1000), (0, 0))
    verify(cl_to_xy((1, -1), offset_cl, center_xy, scale=1000), (1000, 1000))

if __name__ == "__main__":
    run_all_tests()