import pygame
from modes.base_screen import BaseScreen


class BaseScreen2D(BaseScreen):
    CELL_SIZE = 8

    def __init__(self):
        super().__init__()
        self.cols = self.WIDTH // self.CELL_SIZE
        self.rows = self.HEIGHT // self.CELL_SIZE
        self.grid = [[0] * self.cols for _ in range(self.rows)]

    def get_neighbours(self, row, col):
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r = (row + dr) % self.rows
                c = (col + dc) % self.cols
                if self.grid[r][c]:
                    count += 1
        return count

    def draw_grid(self, color_map):
        self.screen.fill((0, 0, 0))
        for row in range(self.rows):
            for col in range(self.cols):
                state = self.grid[row][col]
                if state in color_map:
                    pygame.draw.rect(
                        self.screen,
                        color_map[state],
                        (col * self.CELL_SIZE, row * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)
                    )
        pygame.display.flip()