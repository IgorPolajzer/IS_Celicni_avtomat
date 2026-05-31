import random
import pygame

from modes.base_screen_two_d import BaseScreen2D
from modes.cell_type import CellType


class CaveGenerator(BaseScreen2D):
    FILL_RATIO = 0.45
    STABLE_CHECK_GENERATIONS = 3
    SMOKE_MAX_AGE = 40

    MAX_WATER = 1.0
    MAX_COMPRESS = 1.1
    MIN_FLOW = 0.01
    FLOW_SPEED = 0.25

    COLOR_MAP = {
        CellType.WALL: (120, 100, 80),
        CellType.SAND: (194, 178, 128),
        CellType.FIRE: (255, 80, 0),
        CellType.WOOD: (80, 50, 20),
        CellType.SMOKE_DARK: (60, 60, 60),
        CellType.SMOKE_LIGHT: (200, 200, 200),
    }

    def __init__(self):
        super().__init__()
        self._water = [[0.0] * self.cols for _ in range(self.rows)]
        self._smoke_age = [[0] * self.cols for _ in range(self.rows)]
        self._randomize()
        self._selected_material = CellType.SAND


    def _randomize(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.grid[row][col] = int(
                    CellType.WALL if random.random() < self.FILL_RATIO else CellType.EMPTY
                )
        self._water = [[0.0] * self.cols for _ in range(self.rows)]
        self._smoke_age = [[0] * self.cols for _ in range(self.rows)]

    def _get_wall_neighbours(self, row, col):
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
                    count += 1
                elif self.grid[r][c] == CellType.WALL:
                    count += 1
        return count

    def _next_cave_generation(self):
        new_grid = [[int(CellType.EMPTY)] * self.cols for _ in range(self.rows)]
        for row in range(self.rows):
            for col in range(self.cols):
                n = self._get_wall_neighbours(row, col)
                alive = self.grid[row][col] == CellType.WALL
                if alive and n in (2, 3, 4, 5, 6, 7, 8):
                    new_grid[row][col] = int(CellType.WALL)
                elif not alive and n in (6, 7, 8):
                    new_grid[row][col] = int(CellType.WALL)
        return new_grid

    def _grids_equal(self, a, b):
        return all(a[r][c] == b[r][c] for r in range(self.rows) for c in range(self.cols))

    def _generate_cave(self):
        stable_count = 0
        while stable_count < self.STABLE_CHECK_GENERATIONS:
            new_grid = self._next_cave_generation()
            stable_count = stable_count + 1 if self._grids_equal(self.grid, new_grid) else 0
            self.grid = new_grid
            self.draw_grid(self.COLOR_MAP)
            self.clock.tick(30)


    def _in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols


    def _cell(self, grid, r, c):
        return CellType(grid[r][c]) if self._in_bounds(r, c) else CellType.WALL


    def _is_empty(self, grid, r, c):
        return self._cell(grid, r, c) == CellType.EMPTY


    def _water_color(self, amount):
        t = min(amount / self.MAX_COMPRESS, 1.0)
        return (
            int(10 + (1 - t) * 20),
            int(60 + (1 - t) * 60),
            int(255 - t * 120),
        )

    def _water_step(self):
        new_water = [row[:] for row in self._water]
        new_grid = [row[:] for row in self.grid]

        # Check if water can pass.
        def passable(r, c):
            return self._in_bounds(r, c) and new_grid[r][c] in (CellType.EMPTY, CellType.WATER)

        # Simulation step.
        for row in range(self.rows - 2, -1, -1):
            for col in range(self.cols):
                if self.grid[row][col] != CellType.WATER:
                    continue
                amount = new_water[row][col]
                if amount < self.MIN_FLOW:
                    continue

                # rule 1: flow down
                if passable(row + 1, col):
                    if new_grid[row + 1][col] == CellType.EMPTY:
                        new_grid[row + 1][col] = int(CellType.WATER)
                    flow = min(amount,
                               self.MAX_COMPRESS - new_water[row + 1][col],
                               amount * self.FLOW_SPEED)
                    flow = max(flow, 0.0)
                    if flow >= self.MIN_FLOW:
                        new_water[row][col] -= flow
                        new_water[row + 1][col] += flow

                # rule 2: flow sideways
                if new_water[row][col] >= self.MIN_FLOW:
                    for dc in (-1, 1):
                        nc = col + dc
                        if passable(row, nc):
                            if new_grid[row][nc] == CellType.EMPTY:
                                new_grid[row][nc] = int(CellType.WATER)
                            diff = new_water[row][col] - new_water[row][nc]
                            if diff > self.MIN_FLOW:
                                flow = diff * self.FLOW_SPEED * 0.5
                                new_water[row][col] -= flow
                                new_water[row][nc] += flow

                # rule 3: flow up (pressure)
                if new_water[row][col] > self.MAX_COMPRESS and passable(row - 1, col):
                    if new_grid[row - 1][col] == CellType.EMPTY:
                        new_grid[row - 1][col] = int(CellType.WATER)
                    excess = new_water[row][col] - self.MAX_COMPRESS
                    flow = excess * self.FLOW_SPEED
                    new_water[row][col] -= flow
                    new_water[row - 1][col] += flow

                if new_water[row][col] < self.MIN_FLOW:
                    new_water[row][col] = 0.0
                    new_grid[row][col] = int(CellType.EMPTY)

        self._water = new_water
        self.grid = new_grid


    def _simulation_step(self):
        cols_order = list(range(self.cols))
        random.shuffle(cols_order)

        new_grid = [row[:] for row in self.grid]
        new_water = [row[:] for row in self._water]
        new_smoke_age = [row[:] for row in self._smoke_age]

        # Utils to handle cell operations.
        def cell(r, c):
            return self._cell(new_grid, r, c)

        def swap(r1, c1, r2, c2):
            new_grid[r1][c1], new_grid[r2][c2] = new_grid[r2][c2], new_grid[r1][c1]
            new_water[r1][c1], new_water[r2][c2] = new_water[r2][c2], new_water[r1][c1]

        def is_empty(r, c):
            return self._is_empty(new_grid, r, c)

        # Simulation step.
        for row in range(self.rows - 2, -1, -1):
            for col in cols_order:
                c = cell(row, col)

                # SAND
                if c == CellType.SAND:
                    if is_empty(row + 1, col): # Add sand
                        swap(row, col, row + 1, col)

                    elif cell(row + 1, col) == CellType.WATER: # Make sand go under water
                        swap(row, col, row + 1, col)
                        new_water[row][col] = new_water[row + 1][col]
                        new_water[row + 1][col] = 0.0
                        new_grid[row][col] = int(CellType.WATER)

                    elif is_empty(row + 1, col - 1): # Make sand go to the left
                        swap(row, col, row + 1, col - 1)

                    elif is_empty(row + 1, col + 1): # Make sand go to the right
                        swap(row, col, row + 1, col + 1)

                # WOOD
                elif c == CellType.WOOD:
                    if is_empty(row + 1, col): # Add wood
                        swap(row, col, row + 1, col)

                # FIRE
                elif c == CellType.FIRE:
                    # water extinguishes fire
                    extinguished = False
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = row + dr, col + dc
                        if self._in_bounds(nr, nc) and cell(nr, nc) == CellType.WATER:
                            new_grid[row][col] = int(CellType.SMOKE_DARK)
                            new_smoke_age[row][col] = self.SMOKE_MAX_AGE
                            new_water[nr][nc] = max(0.0, new_water[nr][nc] - 0.3)
                            if new_water[nr][nc] < self.MIN_FLOW:
                                new_grid[nr][nc] = int(CellType.EMPTY)
                                new_water[nr][nc] = 0.0
                            extinguished = True
                            break

                    if not extinguished:
                        down_dirs = [0, random.choice([-1, 1])]
                        random.shuffle(down_dirs)
                        for dc in down_dirs:
                            nr, nc = row + 1, col + dc
                            if not self._in_bounds(nr, nc):
                                continue
                            target = cell(nr, nc)
                            if target == CellType.EMPTY:
                                swap(row, col, nr, nc)
                                break
                            elif target == CellType.WOOD:
                                new_grid[row][col] = int(CellType.SMOKE_DARK)
                                new_smoke_age[row][col] = self.SMOKE_MAX_AGE
                                new_grid[nr][nc] = int(CellType.FIRE)
                                break

                        # ignite adjacent wood
                        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nr, nc = row + dr, col + dc
                            if self._in_bounds(nr, nc) and cell(nr, nc) == CellType.WOOD:
                                if random.random() < 0.02:
                                    new_grid[nr][nc] = int(CellType.FIRE)

                # SMOKE
                elif c in (CellType.SMOKE_DARK, CellType.SMOKE_LIGHT):
                    new_smoke_age[row][col] -= 1
                    if new_smoke_age[row][col] <= 0:
                        new_grid[row][col] = int(CellType.EMPTY)
                    else:
                        if is_empty(row - 1, col):
                            swap(row, col, row - 1, col)
                            new_smoke_age[row - 1][col] = new_smoke_age[row][col]
                            new_smoke_age[row][col] = 0
                        else:
                            dirs = [-1, 1]
                            random.shuffle(dirs)
                            for d in dirs:
                                if is_empty(row, col + d):
                                    swap(row, col, row, col + d)
                                    new_smoke_age[row][col + d] = new_smoke_age[row][col]
                                    new_smoke_age[row][col] = 0
                                    break

        self.grid = new_grid
        self._water = new_water
        self._smoke_age = new_smoke_age
        self._water_step()


    def draw_grid(self, color_map):
        for row in range(self.rows):
            for col in range(self.cols):
                c = self.grid[row][col]
                if c == CellType.WATER:
                    color = self._water_color(self._water[row][col])
                elif c in color_map:
                    color = color_map[c]
                else:
                    color = (30, 30, 30)
                pygame.draw.rect(self.screen, color,
                                 (col * self.CELL_SIZE, row * self.CELL_SIZE,
                                  self.CELL_SIZE, self.CELL_SIZE))
        pygame.display.flip()


    def _place_material(self, mouse_pos, material, radius=1):
        mx, my = mouse_pos
        col = mx // self.CELL_SIZE
        row = my // self.CELL_SIZE
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                r, c = row + dr, col + dc

                if not self._in_bounds(r, c) or self.grid[r][c] == CellType.WALL:
                    continue

                self.grid[r][c] = int(material)
                self._water[r][c] = self.MAX_WATER if material == CellType.WATER else 0.0
                self._smoke_age[r][c] = 0


    def run(self):
        self._generate_cave()

        MATERIAL_KEYS = {
            pygame.K_1: CellType.SAND,
            pygame.K_2: CellType.WATER,
            pygame.K_3: CellType.FIRE,
            pygame.K_4: CellType.WOOD,
        }

        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self._randomize()
                        self._generate_cave()
                    elif event.key in MATERIAL_KEYS:
                        self._selected_material = MATERIAL_KEYS[event.key]

            if pygame.mouse.get_pressed()[0]:
                self._place_material(pygame.mouse.get_pos(), self._selected_material)

            self._simulation_step()
            self.draw_grid(self.COLOR_MAP)
            self.clock.tick(30)

        pygame.quit()
