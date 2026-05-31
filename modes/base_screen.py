import pygame


class BaseScreen:
    HEIGHT = 1000
    WIDTH = 1600
    CELL_SIZE = 2
    GENERATION_TIMESTEP = 10
    RULESET_CODE = 123

    done = False
    cells = []
    generation = 0
    screen = None
    clock = None

    def __init__(self):
        pygame.init()

        screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Celicni automat")

        done = False
        clock = pygame.time.Clock()

        # Initial conditions for the cells. All 0 with center cell as 1
        cells = [0 for e in range(self.WIDTH // self.CELL_SIZE)]
        cells[len(cells) // 2] = 1

        generation = 0
        screen.fill((255, 255, 255))

        self.screen = screen
        self.cells = cells
        self.generation = generation
        self.done = done
        self.clock = clock
