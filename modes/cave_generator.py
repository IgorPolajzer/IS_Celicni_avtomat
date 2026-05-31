import random
import pygame

from modes.base_screen_two_d import BaseScreen2D


class CaveGenerator(BaseScreen2D):
    FILL_RATIO = 0.45
    STABLE_CHECK_GENERATIONS = 3

    EMPTY = 0
    WALL = 1
    SAND = 2
    WATER = 3
    FIRE = 4
    WOOD = 5
    EMBER = 6
    SMOKE_DARK = 7
    SMOKE_LIGHT = 8

    # Water fluid simulation constants
    MAX_WATER = 1.0  # normal full cell
    MAX_COMPRESS = 1.1  # how much a cell can be overfilled (pressure)
    MIN_FLOW = 0.01  # ignore flows smaller than this
    FLOW_SPEED = 0.25  # fraction transferred per tick

    FIRE_LIFETIME = 80  # used only for EMBER now
    EMBER_LIFETIME = 40

    FLAMMABLE = None  # set in __init__ after class attrs exist

    COLOR_MAP = {}  # built dynamically in _build_color_map()

    def __init__(self):
        super().__init__()
        self.FLAMMABLE = {self.WOOD, self.EMBER}
        self._water = [[0.0] * self.cols for _ in range(self.rows)]
        self._build_color_map()
        self._randomize()
        self._selected_material = self.SAND

    def _build_color_map(self):
        self.COLOR_MAP = {
            self.WALL: (120, 100, 80),
            self.SAND: (194, 178, 128),
            self.FIRE: (255, 80, 0),
            self.WOOD: (80, 50, 20),
            self.EMBER: (255, 160, 0),
            self.SMOKE_DARK: (60, 60, 60),
            self.SMOKE_LIGHT: (200, 200, 200),
        }

    def _water_color(self, amount):
        t = min(amount / self.MAX_COMPRESS, 1.0)
        r = int(10 + (1 - t) * 20)
        g = int(60 + (1 - t) * 60)
        b = int(255 - int(t * 120))
        return (r, g, b)

    def _randomize(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.grid[row][col] = 1 if random.random() < self.FILL_RATIO else 0
        self._water = [[0.0] * self.cols for _ in range(self.rows)]

    def _get_wall_neighbours(self, row, col):
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
                    count += 1
                elif self.grid[r][c] == self.WALL:
                    count += 1
        return count

    def _next_cave_generation(self):
        new_grid = [[0] * self.cols for _ in range(self.rows)]
        for row in range(self.rows):
            for col in range(self.cols):
                neighbours = self._get_wall_neighbours(row, col)
                alive = self.grid[row][col] == self.WALL
                if alive and neighbours in (2, 3, 4, 5, 6, 7, 8):
                    new_grid[row][col] = self.WALL
                elif not alive and neighbours in (6, 7, 8):
                    new_grid[row][col] = self.WALL
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
            new_grid = self._next_cave_generation()
            if self._grids_equal(self.grid, new_grid):
                stable_count += 1
            else:
                stable_count = 0
            self.grid = new_grid
            self.draw_grid(self.COLOR_MAP)
            self.clock.tick(30)

    def _in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def _is_empty(self, grid, r, c):
        return self._in_bounds(r, c) and grid[r][c] == self.EMPTY

    def _can_water_enter(self, grid, r, c):
        return self._in_bounds(r, c) and grid[r][c] in (self.EMPTY, self.WATER)

    def _water_step(self):
        new_water = [row[:] for row in self._water]
        new_grid = [row[:] for row in self.grid]

        def passable(r, c):
            if not self._in_bounds(r, c):
                return False
            return new_grid[r][c] in (self.EMPTY, self.WATER)

        def stable_amount(above, below):
            total = above + below
            if total <= self.MAX_WATER:
                return 0.0  # all flows down
            elif total < 2 * self.MAX_WATER + self.MAX_COMPRESS:
                return (total - self.MAX_WATER) / 2.0
            else:
                return total - self.MAX_WATER - self.MAX_COMPRESS

        for row in range(self.rows - 2, -1, -1):
            for col in range(self.cols):
                if self.grid[row][col] != self.WATER:
                    continue
                amount = new_water[row][col]
                if amount < self.MIN_FLOW:
                    continue

                # -- rule 1: flow down --
                if passable(row + 1, col):
                    if new_grid[row + 1][col] == self.EMPTY:
                        new_grid[row + 1][col] = self.WATER
                    capacity = self.MAX_COMPRESS - new_water[row + 1][col]
                    flow = min(amount, capacity, amount * self.FLOW_SPEED)
                    flow = max(flow, 0.0)
                    if flow >= self.MIN_FLOW:
                        new_water[row][col] -= flow
                        new_water[row + 1][col] += flow

                # -- rule 2: flow sideways --
                if new_water[row][col] >= self.MIN_FLOW:
                    for dc in (-1, 1):
                        nc = col + dc
                        if passable(row, nc):
                            if new_grid[row][nc] == self.EMPTY:
                                new_grid[row][nc] = self.WATER
                            diff = new_water[row][col] - new_water[row][nc]
                            if diff > self.MIN_FLOW:
                                flow = diff * self.FLOW_SPEED * 0.5
                                new_water[row][col] -= flow
                                new_water[row][nc] += flow

                # -- rule 3: flow up (pressure) --
                if new_water[row][col] > self.MAX_COMPRESS and passable(row - 1, col):
                    if new_grid[row - 1][col] == self.EMPTY:
                        new_grid[row - 1][col] = self.WATER
                    excess = new_water[row][col] - self.MAX_COMPRESS
                    flow = min(excess, excess * self.FLOW_SPEED)
                    new_water[row][col] -= flow
                    new_water[row - 1][col] += flow

                # clean up near-empty cells
                if new_water[row][col] < self.MIN_FLOW:
                    new_water[row][col] = 0.0
                    new_grid[row][col] = self.EMPTY

        self._water = new_water
        self.grid = new_grid

    def _simulation_step(self):
        cols_order = list(range(self.cols))
        random.shuffle(cols_order) # For left/right randomness (sand ect)

        new_grid = [row[:] for row in self.grid]
        new_water = [row[:] for row in self._water]

        def swap(r1, c1, r2, c2):
            new_grid[r1][c1], new_grid[r2][c2] = new_grid[r2][c2], new_grid[r1][c1]
            new_water[r1][c1], new_water[r2][c2] = new_water[r2][c2], new_water[r1][c1]

        def is_empty(r, c):
            return self._in_bounds(r, c) and new_grid[r][c] == self.EMPTY

        def in_bounds(r, c):
            return self._in_bounds(r, c)

        for row in range(self.rows - 2, -1, -1):
            for col in cols_order:
                cell = new_grid[row][col]

                # SAND
                if cell == self.SAND:
                    below = new_grid[row + 1][col] if in_bounds(row + 1, col) else self.WALL
                    if is_empty(row + 1, col):
                        swap(row, col, row + 1, col)
                    elif below == self.WATER:
                        # sand sinks through water
                        swap(row, col, row + 1, col)
                        new_water[row][col] = new_water[row + 1][col]
                        new_water[row + 1][col] = 0.0
                        new_grid[row][col] = self.WATER
                    elif is_empty(row + 1, col - 1):
                        swap(row, col, row + 1, col - 1)
                    elif is_empty(row + 1, col + 1):
                        swap(row, col, row + 1, col + 1)

                # WOOD
                elif cell == self.WOOD:
                    below = new_grid[row + 1][col] if in_bounds(row + 1, col) else self.WALL
                    above = new_grid[row - 1][col] if in_bounds(row - 1, col) else self.WALL
                    # float: if below is water and above is empty, bob up
                    if below == self.WATER and above == self.EMPTY:
                        swap(row, col, row - 1, col)
                        # water fills vacated spot — give it the water amount
                        new_water[row][col] = new_water[row + 1][col]
                        new_grid[row][col] = self.WATER
                    # fall into empty space (before it hits water)
                    elif is_empty(row + 1, col):
                        swap(row, col, row + 1, col)

                # FIRE
                elif cell == self.FIRE:
                    # check neighbours for water — extinguish
                    extinguished = False
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = row + dr, col + dc
                        if in_bounds(nr, nc) and new_grid[nr][nc] == self.WATER:
                            new_grid[row][col] = self.SMOKE_DARK
                            new_water[nr][nc] = max(0.0, new_water[nr][nc] - 0.3)
                            if new_water[nr][nc] < self.MIN_FLOW:
                                new_grid[nr][nc] = self.EMPTY
                                new_water[nr][nc] = 0.0
                            extinguished = True
                            break

                    if not extinguished:
                        # move randomly downward
                        moved = False
                        down_dirs = [0, random.choice([-1, 1])]
                        random.shuffle(down_dirs)
                        for dc in down_dirs:
                            nr, nc = row + 1, col + dc
                            if not in_bounds(nr, nc):
                                continue
                            target = new_grid[nr][nc]
                            if target == self.EMPTY:
                                swap(row, col, nr, nc)
                                moved = True
                                break
                            elif target in self.FLAMMABLE:
                                new_grid[row][col] = self.SMOKE_DARK
                                if target == self.WOOD:
                                    new_grid[nr][nc] = self.EMBER
                                moved = True
                                break

                        if not moved:
                            new_grid[row][col] = self.SMOKE_LIGHT

                        # ignite adjacent wood
                        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nr, nc = row + dr, col + dc
                            if in_bounds(nr, nc) and new_grid[nr][nc] == self.WOOD:
                                if random.random() < 0.02:
                                    new_grid[nr][nc] = self.EMBER

                # EMBER
                elif cell == self.EMBER:
                    # water extinguishes ember too
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = row + dr, col + dc
                        if in_bounds(nr, nc) and new_grid[nr][nc] == self.WATER:
                            new_grid[row][col] = self.SMOKE_DARK
                            new_water[nr][nc] = max(0.0, new_water[nr][nc] - 0.2)
                            if new_water[nr][nc] < self.MIN_FLOW:
                                new_grid[nr][nc] = self.EMPTY
                                new_water[nr][nc] = 0.0
                            break
                    else:
                        if is_empty(row - 1, col) and random.random() < 0.3:
                            new_grid[row - 1][col] = self.FIRE
                        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nr, nc = row + dr, col + dc
                            if in_bounds(nr, nc) and new_grid[nr][nc] == self.WOOD:
                                if random.random() < 0.01:
                                    new_grid[nr][nc] = self.EMBER

                # SMOKE
                elif cell in (self.SMOKE_DARK, self.SMOKE_LIGHT):
                    moved = False
                    if is_empty(row - 1, col):
                        swap(row, col, row - 1, col)
                        moved = True
                    if not moved:
                        dirs = [-1, 1]
                        random.shuffle(dirs)
                        for d in dirs:
                            if is_empty(row, col + d):
                                swap(row, col, row, col + d)
                                break

        self.grid = new_grid
        self._water = new_water

        # run water fluid simulation separately
        self._water_step()

    def draw_grid(self, color_map):
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.grid[row][col]
                if cell == self.WATER:
                    color = self._water_color(self._water[row][col])
                elif cell in color_map:
                    color = color_map[cell]
                else:
                    color = (30, 30, 30)  # EMPTY background

                x = col * self.CELL_SIZE
                y = row * self.CELL_SIZE
                pygame.draw.rect(self.screen, color,
                                 (x, y, self.CELL_SIZE, self.CELL_SIZE))
        pygame.display.flip()

    def _place_material(self, mouse_pos, material, radius=1):
        mx, my = mouse_pos
        col = mx // self.CELL_SIZE
        row = my // self.CELL_SIZE
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                r, c = row + dr, col + dc
                if not self._in_bounds(r, c):
                    continue
                if self.grid[r][c] == self.WALL:
                    continue
                self.grid[r][c] = material
                if material == self.WATER:
                    self._water[r][c] = self.MAX_WATER
                elif material == self.FIRE:
                    self._water[r][c] = 0.0
                else:
                    self._water[r][c] = 0.0


    def run(self):
        self._generate_cave()

        MATERIAL_KEYS = {
            pygame.K_1: self.SAND,
            pygame.K_2: self.WATER,
            pygame.K_3: self.FIRE,
            pygame.K_4: self.WOOD,
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
