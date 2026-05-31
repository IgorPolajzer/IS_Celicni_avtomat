import random
import time
import pygame

from modes.base_screen import BaseScreen


class OneDimCellularAutomata(BaseScreen):


    def rules(self, left, middle, right):
        neighbourhood = [left, middle, right]
        # RuleIndex is the decimal form of the (binary) neighbourhood. Used to acces a new cell from the ruleset array.
        ruleIndex = int(''.join(str(e) for e in neighbourhood), 2)
        # This converts the rulesetcode (decimal) into an 8 bit number represented as a list
        ruleset = list('{0:08b}'.format(self.RULESET_CODE))
        ruleset.reverse()
        # Access the state of the new cell from the ruleset using our index
        return int(ruleset[ruleIndex])


    def run(self):
        while not self.done:
            # Exit.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True

            for i, cell in enumerate(self.cells):
                if cell == 1:
                    # If the cell size is a single pixel we can't use rect to draw it
                    if self.CELL_SIZE > 1:
                        pygame.draw.rect(self.screen, (0, 0, 0),
                                         [i * self.CELL_SIZE, self.CELL_SIZE * self.generation, self.CELL_SIZE, self.CELL_SIZE])
                    else:
                        self.screen.set_at((i * self.CELL_SIZE, self.CELL_SIZE * self.generation), (0, 0, 0))

            # Loop through the cells, grabbing it's neighbours and calculate the subsequent generation
            newcells = []
            for i, cell in enumerate(self.cells):
                # This modular maths wraps the index if were at the edge of the screen
                left = self.cells[(i - 1) % len(self.cells)]
                middle = cell
                right = self.cells[(i + 1) % len(self.cells)]
                newstate = self.rules(left, middle, right)
                # We use newcells so we don't overwrite cells while we're still using it
                newcells.append(newstate)
            self.cells = newcells

            # If we've filled the screen then pick a new rule and reset everything
            if (self.CELL_SIZE * self.generation) >= self.HEIGHT:
                self.RULESET_CODE = random.randint(0, 255)
                self.generation = 0
                time.sleep(2)
                pygame.display.flip()
                self.screen.fill((255, 255, 255))
                self.cells = [0 for e in range(self.WIDTH // self.CELL_SIZE)]
                self.cells[len(self.cells) // 2] = 1
                print("Current Rule: {0:d} ({0:08b})".format(self.RULESET_CODE))
            else:
                # Update only part of the screen so previous generations are left untouched
                pygame.display.update([0, self.CELL_SIZE * self.generation, self.WIDTH, self.HEIGHT])
                self.generation += 1

            # Wait until the next generation
            self.clock.tick(1000 / self.GENERATION_TIMESTEP)

        pygame.quit()