from common import *
import universe as u
import view as v
import command

def main():
    universe = u.create_test_universe()
    view = v.View((0, 0), AU // 10, 4)
    command.command_loop(universe, view)

if __name__ == "__main__":
    main()
