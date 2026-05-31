import random
import pygame

from modes.base_screen_two_d import BaseScreen2D


class CaveGenerator(BaseScreen2D):

    FILL_RATIO = 0.45
    STABLE_CHECK_GENERATIONS = 3

    COLOR_MAP = {
        1: (120, 100, 80),
    }

    def __init__(self):
        super().__init__()
        self._randomize()

    def _randomize(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.grid[row][col] = 1 if random.random() < self.FILL_RATIO else 0

    def _get_wall_neighbours(self, row, col):
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r = row + dr
                c = col + dc
                if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
                    count += 1  # treat border as wall
                elif self.grid[r][c] == 1:
                    count += 1
        return count

    def _next_generation(self):
        new_grid = [[0] * self.cols for _ in range(self.rows)]
        for row in range(self.rows):
            for col in range(self.cols):
                neighbours = self._get_wall_neighbours(row, col)
                alive = self.grid[row][col] == 1
                # B678/S2345678
                if alive and neighbours in (2, 3, 4, 5, 6, 7, 8):
                    new_grid[row][col] = 1
                elif not alive and neighbours in (6, 7, 8):
                    new_grid[row][col] = 1
        return new_grid

    def _grids_equal(self, a, b):
        for row in range(self.rows):
            for col in range(self.cols):
                if a[row][col] != b[row][col]:
                    return False
        return True

    def _generate_cave(self):
        stable_count = 0
        while stable_count < self.STABLE_CHECK_GENERATIONS:
            new_grid = self._next_generation()
            if self._grids_equal(self.grid, new_grid):
                stable_count += 1
            else:
                stable_count = 0
            self.grid = new_grid
            self.draw_grid(self.COLOR_MAP)
            self.clock.tick(30)

    def run(self):
        self._generate_cave()

        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self._randomize()
                    self._generate_cave()

            self.draw_grid(self.COLOR_MAP)
            self.clock.tick(30)

        pygame.quit()