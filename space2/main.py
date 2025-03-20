from common import *
import universe as u
import view as v
import plot_view as pv
import command as c

def main():
    try:
        (universe, clock) = u.create_test_universe(start_thread=False)
        view = v.create_test_view()
        view.show(universe)

        command = c.Command(universe, view, universe.bodies.get("Heroes"))
        command_thread = threading.Thread(target=command.cmdloop)
        command_thread.start()

        plot_view = pv.create_plot_view_3d(universe)  # blocks
    finally:
        clock.terminate()

if __name__ == "__main__":
    main()
