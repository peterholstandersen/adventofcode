from common import *
import universe as u
import view as v
import command as c

def main():
    try:
        (universe, clock) = u.create_test_universe(start_thread=True)
        view = v.create_test_view()
        view.show(universe)
        command = c.Command(universe, view, universe.bodies.get("Heroes"))
        command.cmdloop()
    finally:
        clock.terminate()

if __name__ == "__main__":
    main()
