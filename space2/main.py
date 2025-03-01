from common import *
import universe as u
import view as v
import command

def main():
    try:
        (universe, clock) = u.create_test_universe(start_thread=True)
        view = v.create_test_view()
        view.show(universe)
        command.command_loop(universe, view)
    finally:
        clock.terminate()

if __name__ == "__main__":
    main()
