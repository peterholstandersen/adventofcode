
class ansi:
    green = "\u001b[32m"
    white = "\u001b[37m"
    bold = "\u001b[1m"
    reset = "\u001b[0m"
    reverse = "\u001b[7m"
    top = "\u001b[0;0H"


# TODO: also works for sets, so needs to be renamed
def print_list(xs, name=None, start="[", end="]"):
    if name:
        print(f"{name}({len(xs)})=", end="")
    if xs is None:
        print("None")
    else:
        print(start + ' '.join(map(str, xs)) + end)
