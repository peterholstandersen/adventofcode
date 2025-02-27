
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
