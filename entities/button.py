import pygame

class MobileButtons:
    def __init__(self):
        self.left = pygame.Rect(25, 520, 75, 55)
        self.right = pygame.Rect(115, 520, 75, 55)
        self.fire = pygame.Rect(700, 510, 75, 65)

    def draw(self, screen):
        mouse = pygame.mouse.get_pos()

        self.control(screen, self.left, "left", mouse)
        self.control(screen, self.right, "right", mouse)
        self.control(screen, self.fire, "fire", mouse)

    def control(self, screen, rect, icon, mouse):
        hover = rect.collidepoint(mouse)
        fill = (5, 42, 55) if hover else (2, 20, 32)
        border = (0, 255, 255) if hover else (0, 190, 220)

        pygame.draw.rect(screen, fill, rect, border_radius=15)
        pygame.draw.rect(screen, border, rect, 2, border_radius=15)

        pygame.draw.line(
            screen, border,
            (rect.left, rect.top + 12),
            (rect.left + 12, rect.top),
            2
        )
        pygame.draw.line(
            screen, border,
            (rect.right - 12, rect.bottom),
            (rect.right, rect.bottom - 12),
            2
        )

        x, y = rect.center

        if icon == "left":
            self.arrow(screen, x, y, -1, border)

        elif icon == "right":
            self.arrow(screen, x, y, 1, border)

        else:
            self.fire_icon(screen, x, y, border)

    def arrow(self, screen, x, y, direction, color):
        pygame.draw.polygon(
            screen,
            color,
            [
                (x + 14 * direction, y),
                (x - 7 * direction, y - 13),
                (x - 7 * direction, y + 13)
            ]
        )

        pygame.draw.line(
            screen,
            color,
            (x - 15 * direction, y),
            (x + 5 * direction, y),
            4
        )

    def fire_icon(self, screen, x, y, color):
        pygame.draw.circle(
            screen,
            color,
            (x, y),
            20,
            2
        )

        pygame.draw.circle(
            screen,
            color,
            (x, y),
            5
        )

        pygame.draw.line(
            screen,
            color,
            (x, y - 29),
            (x, y - 12),
            3
        )

        pygame.draw.line(
            screen,
            color,
            (x, y + 12),
            (x, y + 29),
            3
        )

        pygame.draw.line(
            screen,
            color,
            (x - 29, y),
            (x - 12, y),
            3
        )

        pygame.draw.line(
            screen,
            color,
            (x + 12, y),
            (x + 29, y),
            3
        )

    def handle_mouse(self, player, events):
        mouse = pygame.mouse.get_pos()

        if pygame.mouse.get_pressed()[0]:
            if self.left.collidepoint(mouse):
                player.move_left()

            elif self.right.collidepoint(mouse):
                player.move_right()

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.fire.collidepoint(event.pos):
                    return True

        return False