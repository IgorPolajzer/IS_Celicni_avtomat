from modes.menu import Menu
from modes.one_dim_ca import OneDimCellularAutomata
from modes.game_of_life import GameOfLife
from modes.cave_generator import CaveGenerator

MODES = [
    OneDimCellularAutomata,
    GameOfLife,
    CaveGenerator,
]

if __name__ == '__main__':
    choice = Menu().run()
    if choice is not None:
        MODES[choice]().run()