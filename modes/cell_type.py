from enum import IntEnum

class CellType(IntEnum):
    EMPTY       = 0
    WALL        = 1
    SAND        = 2
    WATER       = 3
    FIRE        = 4
    WOOD        = 5
    SMOKE_DARK  = 6
    SMOKE_LIGHT = 7