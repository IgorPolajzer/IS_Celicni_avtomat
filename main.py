from modes.menu import Menu
from modes.one_dim_ca import OneDimCellularAutomata
from modes.game_of_life import GameOfLife
from modes.cave_generator import CaveGenerator
from modes.element_simulation import ElementSimulation

MODES = [
    OneDimCellularAutomata,
    GameOfLife,
    CaveGenerator,
    ElementSimulation,
]

if __name__ == '__main__':
    choice = Menu().run()
    if choice is not None:
        MODES[choice]().run()