import pygame


class RuleInputScreen:
    BACKGROUND = (15, 15, 20)
    TEXT_COLOR = (200, 200, 210)
    HIGHLIGHT_COLOR = (80, 180, 255)
    ERROR_COLOR = (255, 80, 80)
    DIM_COLOR = (80, 80, 100)

    def __init__(self, width=600, height=400):
        self.width = width
        self.height = height

    def run(self):
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Enter Rule")
        clock = pygame.time.Clock()

        title_font = pygame.font.SysFont("monospace", 22, bold=True)
        input_font = pygame.font.SysFont("monospace", 36, bold=True)
        label_font = pygame.font.SysFont("monospace", 15)
        hint_font  = pygame.font.SysFont("monospace", 13)

        input_text = ""
        error = ""

        while True:
            screen.fill(self.BACKGROUND)

            title = title_font.render("1D CELLULAR AUTOMATON", True, self.HIGHLIGHT_COLOR)
            screen.blit(title, (self.width // 2 - title.get_width() // 2, 60))

            pygame.draw.line(screen, self.DIM_COLOR, (80, 100), (self.width - 80, 100), 1)

            label = label_font.render("Enter rule number (0 - 255):", True, self.TEXT_COLOR)
            screen.blit(label, (self.width // 2 - label.get_width() // 2, 150))

            box_w, box_h = 200, 60
            box_x = self.width // 2 - box_w // 2
            box_y = 185
            pygame.draw.rect(screen, (30, 30, 40), (box_x, box_y, box_w, box_h))
            pygame.draw.rect(screen, self.HIGHLIGHT_COLOR, (box_x, box_y, box_w, box_h), 2)

            display = input_text if input_text else "0"
            number = input_font.render(display, True, self.HIGHLIGHT_COLOR)
            screen.blit(number, (self.width // 2 - number.get_width() // 2, box_y + box_h // 2 - number.get_height() // 2))

            if error:
                err_surf = label_font.render(error, True, self.ERROR_COLOR)
                screen.blit(err_surf, (self.width // 2 - err_surf.get_width() // 2, 265))

            hint = hint_font.render("Type a number   ENTER to confirm   ESC to go back", True, (60, 60, 80))
            screen.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height - 40))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    elif event.key == pygame.K_RETURN:
                        try:
                            value = int(input_text) if input_text else 0
                            if 0 <= value <= 255:
                                return value
                            else:
                                error = "Must be between 0 and 255"
                        except ValueError:
                            error = "Invalid number"
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                        error = ""
                    elif event.unicode.isdigit() and len(input_text) < 3:
                        input_text += event.unicode
                        error = ""

            clock.tick(60)