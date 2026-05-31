import random
import pygame

from modes.base_screen_two_d import BaseScreen2D

EMPTY = 0
WALL = 1
SAND = 2
WOOD = 3
FIRE = 4
SMOKE = 5
WATER = 6
BALLOON = 7

COLORS = {
    EMPTY: (15, 15, 20),
    WALL: (120, 100, 80),
    SAND: (210, 180, 100),
    WOOD: (100, 60, 20),
    FIRE: (255, 80, 20),
    SMOKE: (80, 80, 90),
    WATER: (40, 80, 200),
    BALLOON: (230, 50, 200),
}

FLAMMABLE = {WOOD}
SOLID = {WALL, SAND, WOOD}
BLOCKING = {WALL, SAND, WOOD, FIRE, SMOKE, WATER, BALLOON}

SMOKE_LIFETIME = 30


class ElementSimulation(BaseScreen2D):
    CELL_SIZE = 6
    GENERATION_TIMESTEP = 30

    def __init__(self):
        super().__init__()
        self.smoke_age = [[0] * self.cols for _ in range(self.rows)]
        self.water_level = [[0.0] * self.cols for _ in range(self.rows)]
        self.selected_element = SAND
        self._place_border_walls()

    def _place_border_walls(self):
        for col in range(self.cols):
            self.grid[0][col] = WALL
            self.grid[self.rows - 1][col] = WALL
        for row in range(self.rows):
            self.grid[row][0] = WALL
            self.grid[row][self.cols - 1] = WALL

    def _in_bounds(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols

    def _is_empty(self, row, col):
        return self._in_bounds(row, col) and self.grid[row][col] == EMPTY

    def _step_sand(self, row, col, new_grid, visited):
        if visited[row][col]:
            return
        visited[row][col] = True

        if self._is_empty(row + 1, col):
            new_grid[row][col] = EMPTY
            new_grid[row + 1][col] = SAND
            visited[row + 1][col] = True
            return

        dirs = [-1, 1]
        random.shuffle(dirs)
        for dc in dirs:
            if self._is_empty(row + 1, col + dc):
                new_grid[row][col] = EMPTY
                new_grid[row + 1][col + dc] = SAND
                visited[row + 1][col + dc] = True
                return

        new_grid[row][col] = SAND

    def _step_wood(self, row, col, new_grid, visited):
        if visited[row][col]:
            return
        visited[row][col] = True

        if self._is_empty(row + 1, col):
            new_grid[row][col] = EMPTY
            new_grid[row + 1][col] = WOOD
            visited[row + 1][col] = True
            return

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                r, c = row + dr, col + dc
                if self._in_bounds(r, c) and self.grid[r][c] == FIRE:
                    new_grid[row][col] = FIRE
                    return

        new_grid[row][col] = WOOD

    def _step_fire(self, row, col, new_grid, new_smoke_age, visited):
        if visited[row][col]:
            return
        visited[row][col] = True

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                r, c = row + dr, col + dc
                if self._in_bounds(r, c) and self.grid[r][c] in FLAMMABLE:
                    new_grid[r][c] = FIRE

        target_row = row + random.choice([-1, 1])
        target_col = col + random.randint(-1, 1)

        if self._is_empty(target_row, target_col):
            new_grid[row][col] = EMPTY
            if self.grid[target_row][target_col] in FLAMMABLE:
                new_grid[target_row][target_col] = SMOKE
                new_smoke_age[target_row][target_col] = SMOKE_LIFETIME
            else:
                new_grid[target_row][target_col] = SMOKE
                new_smoke_age[target_row][target_col] = SMOKE_LIFETIME
            visited[target_row][target_col] = True
        else:
            new_grid[row][col] = SMOKE
            new_smoke_age[row][col] = SMOKE_LIFETIME

    def _step_smoke(self, row, col, new_grid, new_smoke_age, visited):
        if visited[row][col]:
            return
        visited[row][col] = True

        age = self.smoke_age[row][col] - 1
        if age <= 0:
            new_grid[row][col] = EMPTY
            return

        moved = False
        dirs = [-1, 0, 1]
        random.shuffle(dirs)
        for dc in dirs:
            if self._is_empty(row - 1, col + dc):
                new_grid[row][col] = EMPTY
                new_grid[row - 1][col + dc] = SMOKE
                new_smoke_age[row - 1][col + dc] = age
                visited[row - 1][col + dc] = True
                moved = True
                break

        if not moved:
            for dc in [-1, 1]:
                if self._is_empty(row, col + dc):
                    new_grid[row][col] = EMPTY
                    new_grid[row][col + dc] = SMOKE
                    new_smoke_age[row][col + dc] = age
                    visited[row][col + dc] = True
                    moved = True
                    break

        if not moved:
            new_grid[row][col] = SMOKE
            new_smoke_age[row][col] = age

    def _step_water(self, row, col, new_grid, new_water, visited):
        if visited[row][col]:
            return
        visited[row][col] = True

        level = self.water_level[row][col]

        if self._is_empty(row + 1, col) or self.grid[row + 1][col] == WATER:
            capacity = 1.0 - new_water[row + 1][col]
            flow = min(level, capacity)
            new_water[row][col] -= flow
            new_water[row + 1][col] += flow
            if new_water[row + 1][col] > 0:
                new_grid[row + 1][col] = WATER
            if new_water[row][col] <= 0:
                new_grid[row][col] = EMPTY
                new_water[row][col] = 0
            else:
                new_grid[row][col] = WATER
            return

        spread = level / 2
        for dc in [-1, 1]:
            c = col + dc
            if self._in_bounds(row, c) and (self.grid[row][c] == EMPTY or self.grid[row][c] == WATER):
                capacity = 1.0 - new_water[row][c]
                flow = min(spread, capacity)
                new_water[row][col] -= flow
                new_water[row][c] += flow
                if new_water[row][c] > 0:
                    new_grid[row][c] = WATER

        if new_water[row][col] > 1.0 and self._is_empty(row - 1, col):
            overflow = new_water[row][col] - 1.0
            new_water[row][col] = 1.0
            new_water[row - 1][col] += overflow
            new_grid[row - 1][col] = WATER

        if new_water[row][col] <= 0:
            new_grid[row][col] = EMPTY
            new_water[row][col] = 0
        else:
            new_grid[row][col] = WATER

    def _step_balloon(self, row, col, new_grid, visited):
        if visited[row][col]:
            return
        visited[row][col] = True

        target_row = row - 1
        target_col = col + random.randint(-1, 1)

        if not self._in_bounds(target_row, target_col):
            new_grid[row][col] = BALLOON
            return

        if self.grid[target_row][target_col] in BLOCKING - {EMPTY}:
            new_grid[row][col] = EMPTY
            return

        if self._is_empty(target_row, target_col):
            new_grid[row][col] = EMPTY
            new_grid[target_row][target_col] = BALLOON
            visited[target_row][target_col] = True
        else:
            new_grid[row][col] = BALLOON

    def _next_generation(self):
        new_grid = [row[:] for row in self.grid]
        new_smoke_age = [row[:] for row in self.smoke_age]
        new_water = [row[:] for row in self.water_level]
        visited = [[False] * self.cols for _ in range(self.rows)]

        for row in range(self.rows - 1, -1, -1):
            for col in range(self.cols):
                state = self.grid[row][col]
                if state == SAND:
                    self._step_sand(row, col, new_grid, visited)
                elif state == WOOD:
                    self._step_wood(row, col, new_grid, visited)
                elif state == FIRE:
                    self._step_fire(row, col, new_grid, new_smoke_age, visited)
                elif state == SMOKE:
                    self._step_smoke(row, col, new_grid, new_smoke_age, visited)
                elif state == WATER:
                    self._step_water(row, col, new_grid, new_water, visited)
                elif state == BALLOON:
                    self._step_balloon(row, col, new_grid, visited)

        self.grid = new_grid
        self.smoke_age = new_smoke_age
        self.water_level = new_water

    def _draw(self):
        self.screen.fill(COLORS[EMPTY])
        for row in range(self.rows):
            for col in range(self.cols):
                state = self.grid[row][col]
                if state == EMPTY:
                    continue
                if state == WATER:
                    level = min(self.water_level[row][col], 1.0)
                    blue = int(100 + 155 * level)
                    color = (20, 40, blue)
                else:
                    color = COLORS.get(state, (255, 0, 255))
                pygame.draw.rect(
                    self.screen, color,
                    (col * self.CELL_SIZE, row * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)
                )

        self._draw_hud()
        pygame.display.flip()

    def _draw_hud(self):
        font = pygame.font.SysFont("monospace", 14)
        elements = [
            (SAND, "1:Sand"),
            (WOOD, "2:Wood"),
            (FIRE, "3:Fire"),
            (WATER, "4:Water"),
            (WALL, "5:Wall"),
            (BALLOON, "6:Balloon"),
        ]
        x = 10
        for state, label in elements:
            color = COLORS[state]
            bg = (50, 50, 60) if state != self.selected_element else (80, 180, 255)
            text = font.render(f" {label} ", True, color, bg)
            self.screen.blit(text, (x, 10))
            x += text.get_width() + 6

    def _place_element(self, mx, my):
        col = mx // self.CELL_SIZE
        row = my // self.CELL_SIZE
        if not self._in_bounds(row, col):
            return
        self.grid[row][col] = self.selected_element
        if self.selected_element == WATER:
            self.water_level[row][col] = 1.0

    def run(self):
        key_to_element = {
            pygame.K_1: SAND,
            pygame.K_2: WOOD,
            pygame.K_3: FIRE,
            pygame.K_4: WATER,
            pygame.K_5: WALL,
            pygame.K_6: BALLOON,
        }

        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                if event.type == pygame.KEYDOWN:
                    if event.key in key_to_element:
                        self.selected_element = key_to_element[event.key]

            if pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                self._place_element(mx, my)

            self._next_generation()
            self._draw()
            self.clock.tick(1000 / self.GENERATION_TIMESTEP)

        pygame.quit()
