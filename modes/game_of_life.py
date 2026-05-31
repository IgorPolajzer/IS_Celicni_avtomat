import pygame

from modes.base_screen_two_d import BaseScreen2D


class GameOfLife(BaseScreen2D):

    COLOR_MAP = {
        1: (255, 255, 255),
    }

    def __init__(self):
        super().__init__()
        self._randomize()

    def _randomize(self):
        import random
        for row in range(self.rows):
            for col in range(self.cols):
                self.grid[row][col] = random.choice([0, 1])

    def _next_generation(self):
        new_grid = [[0] * self.cols for _ in range(self.rows)]
        for row in range(self.rows):
            for col in range(self.cols):
                neighbours = self.get_neighbours(row, col)
                alive = self.grid[row][col] == 1
                if alive and neighbours in (2, 3): # A live cell wit 2 or 3 neighbours stays alive.
                    new_grid[row][col] = 1
                elif not alive and neighbours == 3: # Dead cell with 3 live neighbours comes to life.
                    new_grid[row][col] = 1

                # Other rules are handled by default since the new grid is empty.
                # Any live cell with fewer than two live neighbours dies
                # Any live cell with more than three live neighbours dies
        self.grid = new_grid

    def run(self):
        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self._randomize()

            self._next_generation()
            self.draw_grid(self.COLOR_MAP)
            self.clock.tick(1000 / self.GENERATION_TIMESTEP)

        pygame.quit()