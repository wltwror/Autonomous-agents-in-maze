from src.run_modes import pygame_simulation, team_winrate
import sys




def main():
    # load CLI arguments
    # arguments "--run $NumberOfSimulations"
    flag = False
    runs = 0
    try:
        if sys.argv[1] == "--run":
            flag = True
            runs = int(sys.argv[2])

    except IndexError or ValueError:
        flag = False


    if not flag:
        pygame_simulation()
    else:
        team_winrate(runs)

if __name__ == "__main__":
    main()

