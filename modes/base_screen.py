import pygame


class BaseScreen:
    HEIGHT = 1000
    WIDTH = 1600
    CELL_SIZE = 2
    GENERATION_TIMESTEP = 10
    RULESET_CODE = 123

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Celicni avtomat")
        self.clock = pygame.time.Clock()
        self.done = False
        self.generation = 0
        self.cells = []