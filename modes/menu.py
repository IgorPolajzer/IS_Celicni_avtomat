import pygame


class Menu:
    BACKGROUND = (15, 15, 20)
    TEXT_COLOR = (200, 200, 210)
    HIGHLIGHT_COLOR = (80, 180, 255)
    DIM_COLOR = (80, 80, 100)

    OPTIONS = [
        "1D Cellular Automaton",
        "Game of Life",
        "Cave Simulation",
    ]

    def __init__(self, width=600, height=400):
        self.width = width
        self.height = height
        self.selected = 0

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Select Mode")
        clock = pygame.time.Clock()

        title_font = pygame.font.SysFont("monospace", 22, bold=True)
        option_font = pygame.font.SysFont("monospace", 18)
        hint_font = pygame.font.SysFont("monospace", 13)

        while True:
            screen.fill(self.BACKGROUND)

            # Title
            title = title_font.render("CELLULAR AUTOMATA", True, self.HIGHLIGHT_COLOR)
            screen.blit(title, (self.width // 2 - title.get_width() // 2, 60))

            # Divider
            pygame.draw.line(screen, self.DIM_COLOR, (80, 100), (self.width - 80, 100), 1)

            # Options
            for i, option in enumerate(self.OPTIONS):
                y = 150 + i * 50
                is_selected = i == self.selected

                if is_selected:
                    # Highlight bar
                    pygame.draw.rect(screen, (30, 60, 90), (70, y - 8, self.width - 140, 36))
                    pygame.draw.rect(screen, self.HIGHLIGHT_COLOR, (70, y - 8, 3, 36))
                    color = self.HIGHLIGHT_COLOR
                    prefix = "> "
                else:
                    color = self.DIM_COLOR
                    prefix = "  "

                label = option_font.render(prefix + option, True, color)
                screen.blit(label, (90, y))

            # Hint
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.OPTIONS)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.OPTIONS)
                    elif event.key == pygame.K_RETURN:
                        pygame.quit()
                        return self.selected
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return None

            clock.tick(60)