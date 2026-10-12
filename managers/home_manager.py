import pygame
import math
import random


class HomeManager:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.w, self.h = width, height

        self.title_font = pygame.font.SysFont("Arial", 38, bold=True)
        self.space_font = pygame.font.SysFont("Arial", 58, bold=True)
        self.menu_font = pygame.font.SysFont("Arial", 17, bold=True)
        self.profile_font = pygame.font.SysFont("Arial", 14, bold=True)
        self.small = pygame.font.SysFont("Arial", 10, bold=True)
        self.tiny = pygame.font.SysFont("Arial", 8, bold=True)

        self.time = 0

        self.buttons = [
            ("play", "PLAY GAME", 300),
            ("trophy", "LEADERBOARD", 365),
            ("user", "PROFILE", 430),
            ("logout", "LOGOUT", 495)
        ]

        self.settings_rect = pygame.Rect(25, 505, 42, 42)

        self.stars = []

        for _ in range(90):
            self.stars.append({
                "x": random.randint(0, self.w),
                "y": random.randint(0, self.h),
                "size": random.choice([1, 1, 1, 2]),
                "speed": random.uniform(0.15, 0.6),
                "phase": random.uniform(0, math.pi * 2)
            })

        self.neon_cyan = (0, 245, 255)
        self.neon_blue = (45, 130, 255)
        self.neon_purple = (145, 55, 255)
        self.neon_magenta = (255, 45, 200)

    def update(self, events):
        self.time += 1

        for star in self.stars:
            star["y"] += star["speed"]

            if star["y"] > self.h:
                star["y"] = 0
                star["x"] = random.randint(0, self.w)

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:

                if self.settings_rect.collidepoint(e.pos):
                    return "settings"

                for icon, text, y in self.buttons:
                    r = pygame.Rect(535, y, 225, 50)

                    if r.collidepoint(e.pos):
                        return {
                            "PLAY GAME": "game",
                            "PROFILE": "profile",
                            "LEADERBOARD": "leaderboard",
                            "LOGOUT": "logout"
                        }[text]

        return None

    def draw(self, player):
        self.screen.fill((2, 4, 18))

        self.background()
        self.top_bar()
        self.logo()
        self.spaceship()
        self.enemy_fleet()
        self.profile(player)
        self.menu()
        self.settings_button()
        self.bottom_hud()

    def background(self):
        for star in self.stars:
            pulse = (
                math.sin(self.time * 0.03 + star["phase"]) + 1
            ) / 2

            brightness = int(100 + pulse * 155)

            color = (
                brightness // 3,
                brightness,
                255
            )

            pygame.draw.circle(
                self.screen,
                color,
                (int(star["x"]), int(star["y"])),
                star["size"]
            )

        for i in range(4):
            x = 130 + i * 210
            y = 230 + math.sin(self.time * 0.01 + i) * 50

            surface = pygame.Surface(
                (220, 220),
                pygame.SRCALPHA
            )

            for radius in range(100, 10, -15):
                alpha = int(2 + (100 - radius) * 0.08)

                pygame.draw.circle(
                    surface,
                    (
                        40 if i % 2 else 100,
                        80,
                        255,
                        alpha
                    ),
                    (110, 110),
                    radius
                )

            self.screen.blit(
                surface,
                (x - 110, y - 110)
            )

        pygame.draw.line(
            self.screen,
            (15, 55, 85),
            (0, 575),
            (800, 575),
            1
        )

        pygame.draw.line(
            self.screen,
            (10, 35, 60),
            (0, 95),
            (800, 95),
            1
        )

    def top_bar(self):
        pygame.draw.rect(
            self.screen,
            (3, 10, 25),
            (0, 0, self.w, 80)
        )

        pygame.draw.line(
            self.screen,
            self.neon_cyan,
            (20, 79),
            (780, 79),
            1
        )

        self.text(
            "SPACE INVADERS",
            self.menu_font,
            (25, 18),
            self.neon_cyan
        )

        self.text(
            "BY: PRINCES BENDOY",
            self.tiny,
            (27, 43),
            (125, 150, 190)
        )

        pygame.draw.circle(
            self.screen,
            self.neon_cyan,
            (685, 25),
            5
        )

        self.text(
            "ONLINE",
            self.small,
            (698, 20),
            self.neon_cyan
        )

        self.text(
            "v1.0.0",
            self.tiny,
            (720, 44),
            (100, 120, 160)
        )

    def logo(self):
        self.text(
            "SPACE",
            self.space_font,
            (55, 112),
            (235, 250, 255)
        )

        glow = pygame.Surface(
            (300, 80),
            pygame.SRCALPHA
        )

        glow_font = pygame.font.SysFont(
            "Arial",
            58,
            bold=True
        )

        glow_text = glow_font.render(
            "INVADERS",
            True,
            self.neon_cyan
        )

        glow_text.set_alpha(45)

        glow.blit(
            glow_text,
            (0, 0)
        )

        self.screen.blit(
            glow,
            (58, 158)
        )

        self.text(
            "INVADERS",
            self.space_font,
            (55, 158),
            self.neon_cyan
        )

        self.text(
            "DEFEND  •  SHOOT  •  SURVIVE",
            self.small,
            (60, 225),
            self.neon_magenta
        )

    def spaceship(self):
        x = 255 + math.sin(self.time * 0.015) * 25
        y = 375 + math.sin(self.time * 0.025) * 8

        x = int(x)
        y = int(y)

        self.glow_circle(
            x,
            y + 35,
            38,
            self.neon_cyan,
            3
        )

        flame = 30 + int(
            math.sin(self.time * 0.06) * 8
        )

        pygame.draw.polygon(
            self.screen,
            self.neon_magenta,
            [
                (x - 14, y + 35),
                (x, y + 35 + flame),
                (x + 14, y + 35)
            ]
        )

        pygame.draw.polygon(
            self.screen,
            self.neon_cyan,
            [
                (x - 7, y + 33),
                (x, y + 30 + flame),
                (x + 7, y + 33)
            ]
        )

        pygame.draw.polygon(
            self.screen,
            (8, 18, 42),
            [
                (x, y - 55),
                (x - 30, y + 20),
                (x - 85, y + 42),
                (x - 35, y + 48),
                (x, y + 30),
                (x + 35, y + 48),
                (x + 85, y + 42),
                (x + 30, y + 20)
            ]
        )

        pygame.draw.polygon(
            self.screen,
            self.neon_blue,
            [
                (x, y - 55),
                (x - 30, y + 20),
                (x - 85, y + 42),
                (x - 35, y + 38),
                (x, y + 25),
                (x + 35, y + 38),
                (x + 85, y + 42),
                (x + 30, y + 20)
            ],
            2
        )

        pygame.draw.polygon(
            self.screen,
            (10, 25, 55),
            [
                (x, y - 43),
                (x - 17, y + 20),
                (x + 17, y + 20)
            ]
        )

        pygame.draw.polygon(
            self.screen,
            self.neon_cyan,
            [
                (x, y - 43),
                (x - 13, y + 17),
                (x + 13, y + 17)
            ],
            2
        )

        pygame.draw.ellipse(
            self.screen,
            (50, 160, 255),
            (x - 12, y - 28, 24, 30)
        )

        pygame.draw.ellipse(
            self.screen,
            (180, 250, 255),
            (x - 6, y - 24, 12, 18)
        )

        pygame.draw.circle(
            self.screen,
            self.neon_magenta,
            (x - 60, y + 35),
            5
        )

        pygame.draw.circle(
            self.screen,
            self.neon_magenta,
            (x + 60, y + 35),
            5
        )

    def enemy_fleet(self):
        positions = [
            (80, 315),
            (130, 290),
            (380, 280),
            (425, 320)
        ]

        for i, (x, y) in enumerate(positions):
            offset = math.sin(
                self.time * 0.012 + i
            ) * 5

            y = int(y + offset)

            self.glow_circle(
                x,
                y,
                12,
                self.neon_magenta,
                2
            )

            pygame.draw.polygon(
                self.screen,
                (15, 8, 40),
                [
                    (x, y - 14),
                    (x - 20, y),
                    (x - 14, y + 14),
                    (x, y + 8),
                    (x + 14, y + 14),
                    (x + 20, y)
                ]
            )

            pygame.draw.polygon(
                self.screen,
                self.neon_magenta,
                [
                    (x, y - 14),
                    (x - 20, y),
                    (x - 14, y + 14),
                    (x, y + 8),
                    (x + 14, y + 14),
                    (x + 20, y)
                ],
                1
            )

    def profile(self, player):
        r = pygame.Rect(
            535,
            110,
            225,
            105
        )

        pygame.draw.rect(
            self.screen,
            (5, 12, 32),
            r,
            border_radius=14
        )

        self.neon_rect(
            r,
            (35, 120, 180),
            14,
            1
        )

        pygame.draw.circle(
            self.screen,
            (7, 28, 48),
            (570, 162),
            29
        )

        pygame.draw.circle(
            self.screen,
            self.neon_cyan,
            (570, 162),
            29,
            2
        )

        self.user_icon(
            570,
            162,
            self.neon_cyan
        )

        name = (
            player["username"].upper()
            if player
            else "PLAYER"
        )

        self.text(
            "PLAYER PROFILE",
            self.tiny,
            (612, 130),
            self.neon_cyan
        )

        self.text(
            name,
            self.profile_font,
            (612, 151),
            (235, 250, 255)
        )

        self.text(
            "",
            self.tiny,
            (612, 176),
            (130, 155, 190)
        )

        pygame.draw.line(
            self.screen,
            (30, 70, 100),
            (612, 193),
            (735, 193),
            2
        )

        pygame.draw.line(
            self.screen,
            self.neon_cyan,
            (612, 193),
            (665, 193),
            2
        )

    def menu(self):
        mouse = pygame.mouse.get_pos()

        self.text(
            "MAIN MENU",
            self.small,
            (535, 240),
            self.neon_cyan
        )

        pygame.draw.line(
            self.screen,
            (30, 80, 110),
            (535, 257),
            (760, 257),
            1
        )

        for icon, text, y in self.buttons:
            self.button(
                icon,
                text,
                y,
                mouse
            )

    def button(self, icon, text, y, mouse):
        r = pygame.Rect(
            535,
            y,
            225,
            50
        )

        hover = r.collidepoint(mouse)

        if hover:
            fill = (8, 30, 50)
            border = self.neon_cyan
        else:
            fill = (4, 12, 30)
            border = (35, 95, 135)

        if hover:
            self.glow_rect(
                r,
                self.neon_cyan
            )

        pygame.draw.rect(
            self.screen,
            fill,
            r,
            border_radius=12
        )

        pygame.draw.rect(
            self.screen,
            border,
            r,
            2,
            border_radius=12
        )

        pygame.draw.line(
            self.screen,
            border,
            (535, y + 13),
            (548, y),
            2
        )

        pygame.draw.line(
            self.screen,
            border,
            (747, y + 50),
            (760, y + 37),
            2
        )

        pygame.draw.circle(
            self.screen,
            border,
            (565, y + 25),
            15,
            1
        )

        if icon == "play":
            self.play_icon(
                565,
                y + 25,
                border
            )

        elif icon == "user":
            self.user_icon(
                565,
                y + 25,
                border
            )

        elif icon == "trophy":
            self.trophy_icon(
                565,
                y + 25,
                border
            )

        else:
            self.logout_icon(
                565,
                y + 25,
                border
            )

        self.text(
            text,
            self.menu_font,
            (595, y + 15),
            (235, 250, 255)
        )

        self.text(
            "›",
            self.title_font,
            (735, y + 7),
            border
        )

    def settings_button(self):
        mouse = pygame.mouse.get_pos()
        r = self.settings_rect
        hover = r.collidepoint(mouse)

        border = self.neon_cyan if hover else (35, 95, 135)
        fill = (8, 30, 50) if hover else (4, 12, 30)

        if hover:
            self.glow_rect(r, self.neon_cyan)

        pygame.draw.rect(
            self.screen,
            fill,
            r,
            border_radius=12
        )

        pygame.draw.rect(
            self.screen,
            border,
            r,
            2,
            border_radius=12
        )

        self.gear_icon(
            r.centerx,
            r.centery,
            border
        )

    def gear_icon(self, x, y, c):
        pygame.draw.circle(
            self.screen,
            c,
            (x, y),
            12,
            3
        )

        pygame.draw.circle(
            self.screen,
            c,
            (x, y),
            4
        )

        for angle in range(0, 360, 45):
            rad = math.radians(angle)

            x1 = int(x + math.cos(rad) * 12)
            y1 = int(y + math.sin(rad) * 12)

            x2 = int(x + math.cos(rad) * 16)
            y2 = int(y + math.sin(rad) * 16)

            pygame.draw.line(
                self.screen,
                c,
                (x1, y1),
                (x2, y2),
                3
            )

    def bottom_hud(self):
        self.text(
            "MISSION STATUS",
            self.tiny,
            (85, 552),
            (100, 130, 165)
        )

        self.text(
            "READY",
            self.small,
            (85, 565),
            self.neon_cyan
        )

        pygame.draw.circle(
            self.screen,
            self.neon_cyan,
            (135, 570),
            3
        )

        self.text(
            "SYSTEM ONLINE",
            self.tiny,
            (150, 565),
            (100, 130, 165)
        )

        self.text(
            "DEFEND • SHOOT • SURVIVE",
            self.small,
            (400, 565),
            self.neon_magenta,
            True
        )

    def glow_circle(self, x, y, radius, color, strength=3):
        for i in range(strength, 0, -1):
            surface = pygame.Surface(
                (radius * 5, radius * 5),
                pygame.SRCALPHA
            )

            alpha = int(18 / i)

            pygame.draw.circle(
                surface,
                (*color, alpha),
                (radius * 2, radius * 2),
                radius + i * 8
            )

            self.screen.blit(
                surface,
                (
                    x - radius * 2,
                    y - radius * 2
                )
            )

    def glow_rect(self, rect, color):
        for size in [12, 8, 5]:
            surface = pygame.Surface(
                (
                    rect.width + size * 2,
                    rect.height + size * 2
                ),
                pygame.SRCALPHA
            )

            pygame.draw.rect(
                surface,
                (*color, 20),
                (
                    size,
                    size,
                    rect.width,
                    rect.height
                ),
                3,
                border_radius=14
            )

            self.screen.blit(
                surface,
                (
                    rect.x - size,
                    rect.y - size
                )
            )

    def neon_rect(self, rect, color, radius=10, width=2):
        pygame.draw.rect(
            self.screen,
            color,
            rect,
            width,
            border_radius=radius
        )

    def play_icon(self, x, y, c):
        pygame.draw.polygon(
            self.screen,
            c,
            [
                (x - 5, y - 9),
                (x + 9, y),
                (x - 5, y + 9)
            ]
        )

    def user_icon(self, x, y, c):
        pygame.draw.circle(
            self.screen,
            c,
            (x, y - 6),
            5
        )

        pygame.draw.arc(
            self.screen,
            c,
            (x - 10, y + 1, 20, 15),
            0,
            math.pi,
            3
        )

    def trophy_icon(self, x, y, c):
        pygame.draw.rect(
            self.screen,
            c,
            (x - 6, y - 8, 12, 13),
            2
        )

        pygame.draw.arc(
            self.screen,
            c,
            (x - 13, y - 7, 9, 12),
            math.pi / 2,
            math.pi * 1.5,
            2
        )

        pygame.draw.arc(
            self.screen,
            c,
            (x + 4, y - 7, 9, 12),
            -math.pi / 2,
            math.pi / 2,
            2
        )

        pygame.draw.line(
            self.screen,
            c,
            (x, y + 5),
            (x, y + 11),
            2
        )

        pygame.draw.line(
            self.screen,
            c,
            (x - 7, y + 12),
            (x + 7, y + 12),
            2
        )

    def logout_icon(self, x, y, c):
        pygame.draw.rect(
            self.screen,
            c,
            (x - 9, y - 11, 11, 22),
            2
        )

        pygame.draw.line(
            self.screen,
            c,
            (x - 1, y),
            (x + 10, y),
            2
        )

        pygame.draw.line(
            self.screen,
            c,
            (x + 5, y - 5),
            (x + 10, y),
            2
        )

        pygame.draw.line(
            self.screen,
            c,
            (x + 5, y + 5),
            (x + 10, y),
            2
        )

    def text(self, value, font, pos, color, center=False):
        img = font.render(
            value,
            True,
            color
        )

        if center:
            self.screen.blit(
                img,
                img.get_rect(center=pos)
            )
        else:
            self.screen.blit(
                img,
                pos
            )
