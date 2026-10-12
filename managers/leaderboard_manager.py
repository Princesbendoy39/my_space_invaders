import pygame
import math
import random
from db import load_leaderboard


class LeaderboardManager:
    def __init__(self, screen, width, height, current_username=None):
        self.screen = screen
        self.w = width
        self.h = height

        self.current_username = current_username

        self.brand_font = pygame.font.SysFont("Arial", 16, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 30, bold=True)
        self.subtitle_font = pygame.font.SysFont("Arial", 12, bold=True)
        self.header_font = pygame.font.SysFont("Arial", 11, bold=True)
        self.font = pygame.font.SysFont("Arial", 14, bold=True)
        self.score_font = pygame.font.SysFont("Arial", 16, bold=True)
        self.button_font = pygame.font.SysFont("Arial", 14, bold=True)

        self.back = pygame.Rect(300, 527, 200, 36)

        self.players = []
        self.stars = []

        for _ in range(60):
            self.stars.append({
                "x": random.randint(10, self.w - 10),
                "y": random.randint(65, 565),
                "speed": random.uniform(0.15, 0.55),
                "size": random.choice([1, 1, 1, 2])
            })

        self.ship_time = 0
        self.ship_x = 400

    def set_player(self, player):
        if player is None:
            self.current_username = None
            return

        self.current_username = player.get(
            "username",
            None
        )

    def update(self, events):
        try:
            self.players = load_leaderboard()

            if self.players is None:
                self.players = []

        except Exception:
            self.players = []

        self.ship_time += 1

        for star in self.stars:
            star["y"] += star["speed"]

            if star["y"] > 565:
                star["y"] = 65
                star["x"] = random.randint(
                    10,
                    self.w - 10
                )

        self.ship_x = 400 + math.sin(
            self.ship_time * 0.015
        ) * 45

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.back.collidepoint(event.pos):
                        return "home"

        self.draw()
        return None

    def draw(self):
        self.background()
        self.top_header()
        self.title()
        self.leaderboard_panel()
        self.rows()
        self.your_rank()
        self.spaceship()
        self.back_button()
        self.bottom_bar()

    def background(self):
        self.screen.fill((2, 6, 15))

        for star in self.stars:
            glow = int(
                130 + 50 * math.sin(
                    self.ship_time * 0.025 + star["x"]
                )
            )

            pygame.draw.circle(
                self.screen,
                (
                    0,
                    glow,
                    min(255, glow + 35)
                ),
                (
                    int(star["x"]),
                    int(star["y"])
                ),
                star["size"]
            )

        pygame.draw.circle(
            self.screen,
            (4, 18, 35),
            (30, 325),
            105
        )

        pygame.draw.circle(
            self.screen,
            (0, 70, 100),
            (30, 325),
            105,
            1
        )

        pygame.draw.circle(
            self.screen,
            (9, 12, 35),
            (775, 300),
            105
        )

        pygame.draw.circle(
            self.screen,
            (70, 30, 120),
            (775, 300),
            105,
            1
        )

    def top_header(self):
        pygame.draw.rect(
            self.screen,
            (3, 12, 24),
            (0, 0, self.w, 58)
        )

        pygame.draw.line(
            self.screen,
            (0, 180, 220),
            (0, 57),
            (self.w, 57),
            1
        )

        self.text(
            "SPACE INVADERS",
            self.brand_font,
            (22, 17),
            (0, 225, 245)
        )

        self.text(
            "BY: PRINCES B.",
            self.subtitle_font,
            (22, 38),
            (85, 135, 155)
        )

        pygame.draw.circle(
            self.screen,
            (0, 255, 180),
            (620, 19),
            4
        )

        self.text(
            "ONLINE",
            self.header_font,
            (630, 14),
            (140, 225, 210)
        )

        logged_name = self.current_username

        if not logged_name:
            logged_name = "PLAYER"

        self.text(
            str(logged_name).upper(),
            self.header_font,
            (630, 33),
            (180, 205, 215)
        )

    def title(self):
        self.text_center(
            "LEADERBOARD",
            self.title_font,
            (400, 82),
            (0, 230, 255)
        )

        self.text_center(
            "SPACE INVADERS GAME RANKINGS",
            self.subtitle_font,
            (400, 108),
            (100, 165, 185)
        )

        pygame.draw.line(
            self.screen,
            (0, 65, 90),
            (145, 120),
            (655, 120),
            1
        )

        pygame.draw.line(
            self.screen,
            (0, 225, 250),
            (145, 120),
            (265, 120),
            2
        )

        pygame.draw.line(
            self.screen,
            (0, 225, 250),
            (535, 120),
            (655, 120),
            2
        )

    def leaderboard_panel(self):
        self.panel_rect = pygame.Rect(
            105,
            132,
            590,
            292
        )

        self.glow(
            self.panel_rect,
            (0, 170, 220)
        )

        pygame.draw.rect(
            self.screen,
            (3, 15, 28),
            self.panel_rect,
            border_radius=16
        )

        pygame.draw.rect(
            self.screen,
            (0, 145, 185),
            self.panel_rect,
            1,
            border_radius=16
        )

        self.text_center(
            "RANK",
            self.header_font,
            (145, 157),
            (90, 145, 165)
        )

        self.text(
            "NAME",
            self.header_font,
            (205, 151),
            (90, 145, 165)
        )

        self.text_center(
            "SCORE",
            self.header_font,
            (505, 157),
            (90, 145, 165)
        )

        self.text_center(
            "LEVEL",
            self.header_font,
            (615, 157),
            (90, 145, 165)
        )

        pygame.draw.line(
            self.screen,
            (0, 65, 85),
            (125, 177),
            (675, 177),
            1
        )

    def rows(self):
        if not self.players:
            self.text_center(
                "NO RECORDS AVAILABLE",
                self.font,
                (400, 275),
                (90, 150, 170)
            )
            return

        for i, player in enumerate(
            self.players[:8],
            1
        ):
            y = 197 + (i - 1) * 25

            if i == 1:
                rank_color = (255, 215, 65)
                name_color = (255, 235, 155)

            elif i == 2:
                rank_color = (215, 225, 235)
                name_color = (230, 240, 245)

            elif i == 3:
                rank_color = (220, 155, 85)
                name_color = (235, 225, 205)

            else:
                rank_color = (80, 175, 205)
                name_color = (215, 235, 242)

            if i <= 3:
                pygame.draw.circle(
                    self.screen,
                    (
                        rank_color[0] // 5,
                        rank_color[1] // 5,
                        rank_color[2] // 5
                    ),
                    (145, y),
                    11
                )

                pygame.draw.circle(
                    self.screen,
                    rank_color,
                    (145, y),
                    11,
                    1
                )

                self.text_center(
                    str(i),
                    self.header_font,
                    (145, y),
                    rank_color
                )

            else:
                self.text_center(
                    f"{i:02d}",
                    self.header_font,
                    (145, y),
                    rank_color
                )

            username = str(
                player.get(
                    "username",
                    "UNKNOWN"
                )
            ).upper()

            if len(username) > 22:
                username = username[:22]

            self.text(
                username,
                self.font,
                (205, y - 7),
                name_color
            )

            try:
                score = int(
                    player.get(
                        "score",
                        0
                    )
                )

            except:
                score = 0

            self.text_center(
                f"{score:,}",
                self.score_font,
                (505, y),
                rank_color
            )

            try:
                level = int(
                    player.get(
                        "level",
                        1
                    )
                )

            except:
                level = 1

            level = max(
                1,
                min(
                    99,
                    level
                )
            )

            self.text_center(
                f"{level:02d}",
                self.font,
                (615, y),
                (110, 200, 220)
            )

            if i < min(
                8,
                len(self.players)
            ):
                pygame.draw.line(
                    self.screen,
                    (0, 38, 55),
                    (125, y + 13),
                    (675, y + 13),
                    1
                )

    def your_rank(self):
        if not self.players:
            return

        if not self.current_username:
            return

        current_name = str(
            self.current_username
        ).strip().lower()

        player = None
        player_rank = None

        for i, item in enumerate(
            self.players,
            1
        ):
            username = str(
                item.get(
                    "username",
                    ""
                )
            ).strip().lower()

            if username == current_name:
                player = item
                player_rank = i
                break

        if player is None:
            return

        username = str(
            player.get(
                "username",
                "UNKNOWN"
            )
        ).upper()

        if len(username) > 16:
            username = username[:16]

        try:
            score = int(
                player.get(
                    "score",
                    0
                )
            )

        except:
            score = 0

        card = pygame.Rect(
            170,
            435,
            460,
            68
        )

        self.glow(
            card,
            (0, 170, 220)
        )

        pygame.draw.rect(
            self.screen,
            (4, 18, 32),
            card,
            border_radius=14
        )

        pygame.draw.rect(
            self.screen,
            (0, 150, 195),
            card,
            1,
            border_radius=14
        )

        pygame.draw.line(
            self.screen,
            (0, 65, 85),
            (320, 447),
            (320, 491),
            1
        )

        pygame.draw.line(
            self.screen,
            (0, 65, 85),
            (480, 447),
            (480, 491),
            1
        )

        self.text_center(
            "PLAYER",
            self.header_font,
            (245, 449),
            (80, 155, 175)
        )

        self.text_center(
            "YOUR RANK",
            self.header_font,
            (400, 449),
            (80, 155, 175)
        )

        self.text_center(
            "SCORE",
            self.header_font,
            (555, 449),
            (80, 155, 175)
        )

        self.text_center(
            username,
            self.font,
            (245, 477),
            (230, 245, 250)
        )

        self.text_center(
            f"{player_rank:02d}",
            self.score_font,
            (400, 477),
            (0, 230, 255)
        )

        self.text_center(
            f"{score:,}",
            self.score_font,
            (555, 477),
            (255, 215, 70)
        )

    def spaceship(self):
        x = int(self.ship_x)
        y = 515

        flame = 5 + int(
            abs(
                math.sin(
                    self.ship_time * 0.12
                )
            ) * 5
        )

        pygame.draw.polygon(
            self.screen,
            (30, 10, 55),
            [
                (x, y - 16),
                (x - 14, y + 8),
                (x - 42, y + 17),
                (x - 25, y + 1),
                (x - 48, y + 5),
                (x - 20, y - 5),
                (x, y - 27),
                (x + 20, y - 5),
                (x + 48, y + 5),
                (x + 25, y + 1),
                (x + 42, y + 17),
                (x + 14, y + 8)
            ]
        )

        pygame.draw.polygon(
            self.screen,
            (175, 45, 255),
            [
                (x, y - 24),
                (x - 11, y + 6),
                (x, y),
                (x + 11, y + 6)
            ]
        )

        pygame.draw.polygon(
            self.screen,
            (110, 30, 190),
            [
                (x - 30, y + 2),
                (x - 48, y + 7),
                (x - 34, y + 12),
                (x - 18, y + 7)
            ]
        )

        pygame.draw.polygon(
            self.screen,
            (110, 30, 190),
            [
                (x + 30, y + 2),
                (x + 48, y + 7),
                (x + 34, y + 12),
                (x + 18, y + 7)
            ]
        )

        pygame.draw.circle(
            self.screen,
            (255, 80, 220),
            (x, y - 10),
            5
        )

        pygame.draw.circle(
            self.screen,
            (255, 190, 250),
            (x, y - 10),
            2
        )

        pygame.draw.polygon(
            self.screen,
            (255, 55, 190),
            [
                (x - 8, y + 7),
                (x + 8, y + 7),
                (x + 3, y + 23 + flame),
                (x, y + 17 + flame),
                (x - 3, y + 23 + flame)
            ]
        )

        pygame.draw.polygon(
            self.screen,
            (255, 150, 245),
            [
                (x - 3, y + 8),
                (x + 3, y + 8),
                (x, y + 19 + flame)
            ]
        )

    def back_button(self):
        hover = self.back.collidepoint(
            pygame.mouse.get_pos()
        )

        if hover:
            fill = (5, 45, 60)
            border = (0, 255, 255)

            self.glow(
                self.back,
                (0, 220, 255)
            )

        else:
            fill = (3, 20, 32)
            border = (0, 175, 210)

        pygame.draw.rect(
            self.screen,
            fill,
            self.back,
            border_radius=18
        )

        pygame.draw.rect(
            self.screen,
            border,
            self.back,
            2,
            border_radius=18
        )

        self.text_center(
            "BACK TO HOME",
            self.button_font,
            self.back.center,
            (225, 245, 250)
        )

    def bottom_bar(self):
        pygame.draw.line(
            self.screen,
            (0, 70, 90),
            (20, 570),
            (780, 570),
            1
        )

        self.text(
            "● SYSTEM ONLINE",
            self.header_font,
            (25, 580),
            (0, 225, 180)
        )

        self.text_center(
            "SPACE INVADERS v1.0",
            self.header_font,
            (400, 584),
            (75, 120, 140)
        )

        self.text_right(
            "DEFEND • SHOOT • SURVIVE",
            self.header_font,
            (775, 580),
            (80, 135, 155)
        )

    def glow(self, rect, color):
        surface = pygame.Surface(
            (self.w, self.h),
            pygame.SRCALPHA
        )

        for size in range(8, 0, -1):
            expanded = rect.inflate(
                size * 2,
                size * 2
            )

            alpha = 4 + size * 2

            pygame.draw.rect(
                surface,
                (
                    color[0],
                    color[1],
                    color[2],
                    alpha
                ),
                expanded,
                1,
                border_radius=rect.height // 2
            )

        self.screen.blit(
            surface,
            (0, 0)
        )

    def text(self, value, font, pos, color):
        image = font.render(
            str(value),
            True,
            color
        )

        self.screen.blit(
            image,
            pos
        )

    def text_center(self, value, font, pos, color):
        image = font.render(
            str(value),
            True,
            color
        )

        self.screen.blit(
            image,
            image.get_rect(
                center=pos
            )
        )

    def text_right(self, value, font, pos, color):
        image = font.render(
            str(value),
            True,
            color
        )

        self.screen.blit(
            image,
            image.get_rect(
                right=pos[0],
                centery=pos[1]
            )
        )
