from common import *
import universe as u

def main():
    universe = u.big_bang()
    universe.clock.set_factor(1)
    command = universe.command
    command_thread = threading.Thread(target=command.cmdloop)
    command_thread.start()
    universe.clock.set_factor(86400 // 4)   # while testing
    universe.plot_view.start_animation()
    # start_animation blocks until universe.alive is set to False, which is done in the command_thread on the "exit" command
    command_thread.join() # wait for the thread to terminate properly

if __name__ == "__main__":
    main()
