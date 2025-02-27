from common import *
import command
import utils
import universe
import view

if __name__ == "__main__":
    # Call test in every moduel?
    command.run_all_tests()
    utils.run_all_tests()
    universe.run_all_tests()
    view.run_all_tests()
