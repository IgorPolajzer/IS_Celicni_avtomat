import pygame

from modes.base_screen import BaseScreen
from modes.rule_input_screen import RuleInputScreen


class OneDimCellularAutomata(BaseScreen):

    def __init__(self):
        super().__init__()

    def _reset(self, rule):
        self.RULESET_CODE = rule
        self.generation = 0
        self.cells = [0] * (self.WIDTH // self.CELL_SIZE)
        self.cells[len(self.cells) // 2] = 1
        self.screen.fill((255, 255, 255))

    def _apply_rule(self, left, middle, right):
        neighbourhood_index = int(f"{left}{middle}{right}", 2)
        ruleset = list(f"{self.RULESET_CODE:08b}")
        ruleset.reverse()
        return int(ruleset[neighbourhood_index])

    def _next_generation(self):
        new_cells = []
        for i, middle in enumerate(self.cells):
            left = self.cells[(i - 1) % len(self.cells)]
            right = self.cells[(i + 1) % len(self.cells)]
            new_cells.append(self._apply_rule(left, middle, right))
        self.cells = new_cells

    def _draw_current_generation(self):
        y = self.CELL_SIZE * self.generation
        for i, cell in enumerate(self.cells):
            if cell == 1:
                x = i * self.CELL_SIZE
                if self.CELL_SIZE > 1:
                    pygame.draw.rect(self.screen, (0, 0, 0), [x, y, self.CELL_SIZE, self.CELL_SIZE])
                else:
                    self.screen.set_at((x, y), (0, 0, 0))
        pygame.display.update([0, y, self.WIDTH, self.CELL_SIZE])

    def _screen_is_full(self):
        return self.CELL_SIZE * self.generation >= self.HEIGHT

    def run(self):
        while True:
            rule = RuleInputScreen(self.WIDTH, self.HEIGHT).run()
            if rule is None:
                break

            self._reset(rule)

            while not self.done and not self._screen_is_full():
                self._draw_current_generation()
                self._next_generation()
                self.generation += 1
                self.clock.tick(1000 / self.GENERATION_TIMESTEP)

            if self.done:
                break

        pygame.quit()
