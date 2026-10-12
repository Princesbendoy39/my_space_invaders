import pygame
import math
import random

from db import register_player, login_player


class AuthManager:

    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height

        self.mode = "login"
        self.active = "username"

        self.username = ""
        self.password = ""
        self.confirm = ""

        self.show_password = False
        self.show_confirm = False

        self.message = ""
        self.message_type = ""

        self.popup = False
        self.popup_timer = 0

        self.player_x = 220
        self.player_y = 445

        self.player_bullets = []
        self.enemy_bullets = []

        self.fire_timer = 0
        self.stars = []
        self.enemies = []
        self.explosions = []

        self.time = 0

        self.cyan = (0, 245, 255)
        self.blue = (45, 130, 255)
        self.purple = (155, 55, 255)
        self.magenta = (255, 40, 200)
        self.white = (235, 250, 255)
        self.dark = (3, 6, 20)

        self.create_stars()
        self.create_enemies()

    def clear_fields(self):
        self.username = ""
        self.password = ""
        self.confirm = ""

        self.active = "username"

        self.show_password = False
        self.show_confirm = False

        self.message = ""
        self.message_type = ""

    def create_stars(self):
        for _ in range(110):
            self.stars.append({
                "x": random.randint(0, self.width),
                "y": random.randint(0, self.height),
                "speed": random.uniform(0.2, 1.1),
                "size": random.randint(1, 2),
                "phase": random.uniform(0, math.pi * 2)
            })

    def create_enemies(self):
        positions = [
            (65, 145), (140, 115), (215, 150),
            (290, 115), (365, 145), (105, 205),
            (190, 185), (275, 205), (350, 185)
        ]

        self.enemies = []

        for x, y in positions:
            self.enemies.append({
                "x": x,
                "y": y,
                "base_y": y,
                "phase": random.uniform(0, math.pi * 2),
                "fire": random.randint(100, 220),
                "alive": True
            })

    def glow_circle(self, x, y, radius, color, strength=3):
        for i in range(strength, 0, -1):
            surface = pygame.Surface(
                (radius * 4, radius * 4),
                pygame.SRCALPHA
            )

            pygame.draw.circle(
                surface,
                (*color, int(25 / i)),
                (radius * 2, radius * 2),
                radius + i * 8
            )

            self.screen.blit(
                surface,
                (x - radius * 2, y - radius * 2)
            )

    def glow_line(self, start, end, color, width=2):
        for extra in range(10, 0, -2):
            surface = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA
            )

            pygame.draw.line(
                surface,
                (*color, max(8, 30 - extra * 2)),
                start,
                end,
                width + extra
            )

            self.screen.blit(surface, (0, 0))

        pygame.draw.line(
            self.screen,
            color,
            start,
            end,
            width
        )

    def neon_rect(self, rect, color, radius=12, width=2):
        for extra in range(12, 0, -3):
            surface = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA
            )

            pygame.draw.rect(
                surface,
                (*color, max(5, 35 - extra * 2)),
                (
                    rect.x - extra // 2,
                    rect.y - extra // 2,
                    rect.width + extra,
                    rect.height + extra
                ),
                width + 2,
                radius + extra // 2
            )

            self.screen.blit(surface, (0, 0))

        pygame.draw.rect(
            self.screen,
            color,
            rect,
            width,
            radius
        )

    def update_stars(self):
        for star in self.stars:
            star["y"] += star["speed"]

            if star["y"] > self.height:
                star["y"] = 0
                star["x"] = random.randint(0, self.width)

    def update_player(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.player_x -= 5

        if keys[pygame.K_RIGHT]:
            self.player_x += 5

        self.player_x = max(75, min(415, self.player_x))

    def update_player_fire(self):
        self.fire_timer += 1

        if self.fire_timer >= 35:
            self.fire_timer = 0

            self.player_bullets.append({
                "x": self.player_x,
                "y": self.player_y - 75,
                "speed": 7
            })

    def update_enemy_fire(self):
        for enemy in self.enemies:
            if not enemy["alive"]:
                continue

            enemy["fire"] -= 1

            if enemy["fire"] <= 0:
                self.enemy_bullets.append({
                    "x": enemy["x"],
                    "y": enemy["y"] + 20,
                    "speed": 4
                })

                enemy["fire"] = random.randint(150, 240)

    def update_bullets(self):
        for bullet in self.player_bullets[:]:
            bullet["y"] -= bullet["speed"]

            if bullet["y"] < 70:
                self.player_bullets.remove(bullet)

        for bullet in self.enemy_bullets[:]:
            bullet["y"] += bullet["speed"]

            if bullet["y"] > self.height:
                self.enemy_bullets.remove(bullet)

    def check_collisions(self):
        for bullet in self.player_bullets[:]:
            bullet_rect = pygame.Rect(
                bullet["x"] - 3,
                bullet["y"] - 14,
                6,
                28
            )

            for enemy in self.enemies:
                if not enemy["alive"]:
                    continue

                enemy_rect = pygame.Rect(
                    enemy["x"] - 25,
                    enemy["y"] - 18,
                    50,
                    36
                )

                if bullet_rect.colliderect(enemy_rect):
                    enemy["alive"] = False

                    if bullet in self.player_bullets:
                        self.player_bullets.remove(bullet)

                    self.explosions.append({
                        "x": enemy["x"],
                        "y": enemy["y"],
                        "life": 25
                    })

                    break

    def update_explosions(self):
        for explosion in self.explosions[:]:
            explosion["life"] -= 1

            if explosion["life"] <= 0:
                self.explosions.remove(explosion)

    def draw_background(self):
        self.screen.fill(self.dark)

        for i in range(5):
            x = 120 + i * 170
            y = 100 + math.sin(
                self.time * 0.002 + i
            ) * 40

            self.glow_circle(
                x,
                y,
                35,
                self.purple if i % 2 == 0 else self.blue,
                2
            )

        for star in self.stars:
            pulse = (
                math.sin(
                    self.time * 0.003 + star["phase"]
                ) + 1
            ) / 2

            brightness = int(100 + pulse * 155)

            pygame.draw.circle(
                self.screen,
                (
                    brightness // 2,
                    brightness,
                    255
                ),
                (
                    int(star["x"]),
                    int(star["y"])
                ),
                star["size"]
            )

    def draw_title(self):
        title_font = pygame.font.SysFont(
            "arial", 38, bold=True
        )

        subtitle_font = pygame.font.SysFont(
            "arial", 14, bold=True
        )

        title = title_font.render(
            "SPACE INVADERS",
            True,
            self.white
        )

        rect = title.get_rect(
            center=(400, 38)
        )

        glow = title_font.render(
            "SPACE INVADERS",
            True,
            self.cyan
        )

        glow.set_alpha(30)

        for offset in (8, 5, 3):
            self.screen.blit(
                glow,
                (rect.x - offset, rect.y)
            )

        self.screen.blit(title, rect)

        subtitle = subtitle_font.render(
            "BY: PRINCES BENDOY",
            True,
            self.magenta
        )

        self.screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(400, 68)
            )
        )

    def draw_spaceship(self):
        x = int(
            self.player_x +
            math.sin(self.time * 0.004) * 7
        )

        y = int(
            self.player_y +
            math.sin(self.time * 0.006) * 5
        )

        self.glow_circle(
            x, y + 20, 35, self.cyan, 3
        )

        self.glow_circle(
            x, y + 15, 18, self.magenta, 2
        )

        flame = 25 + int(
            math.sin(self.time * 0.02) * 7
        )

        pygame.draw.polygon(
            self.screen,
            self.magenta,
            [
                (x - 16, y + 37),
                (x, y + 37 + flame),
                (x + 16, y + 37)
            ]
        )

        pygame.draw.polygon(
            self.screen,
            self.cyan,
            [
                (x - 8, y + 34),
                (x, y + 32 + flame),
                (x + 8, y + 34)
            ]
        )

        pygame.draw.polygon(
            self.screen,
            (12, 20, 45),
            [
                (x, y - 35),
                (x - 24, y + 20),
                (x - 55, y + 35),
                (x - 20, y + 40),
                (x, y + 28),
                (x + 20, y + 40),
                (x + 55, y + 35),
                (x + 24, y + 20)
            ]
        )

        pygame.draw.polygon(
            self.screen,
            self.blue,
            [
                (x, y - 35),
                (x - 24, y + 20),
                (x - 55, y + 35),
                (x - 20, y + 34),
                (x, y + 23),
                (x + 20, y + 34),
                (x + 55, y + 35),
                (x + 24, y + 20)
            ],
            2
        )

        pygame.draw.polygon(
            self.screen,
            (18, 25, 55),
            [
                (x, y - 27),
                (x - 13, y + 18),
                (x + 13, y + 18)
            ]
        )

        pygame.draw.polygon(
            self.screen,
            self.cyan,
            [
                (x, y - 25),
                (x - 10, y + 13),
                (x + 10, y + 13)
            ],
            2
        )

        pygame.draw.ellipse(
            self.screen,
            (70, 180, 255),
            (x - 10, y - 15, 20, 24)
        )

        pygame.draw.ellipse(
            self.screen,
            (170, 245, 255),
            (x - 5, y - 12, 10, 15)
        )

        pygame.draw.circle(
            self.screen,
            self.magenta,
            (x - 39, y + 29),
            4
        )

        pygame.draw.circle(
            self.screen,
            self.magenta,
            (x + 39, y + 29),
            4
        )

    def draw_enemies(self):
        for enemy in self.enemies:
            if not enemy["alive"]:
                continue

            x = int(enemy["x"])

            y = int(
                enemy["base_y"] +
                math.sin(
                    self.time * 0.003 +
                    enemy["phase"]
                ) * 4
            )

            self.glow_circle(
                x, y, 16, self.magenta, 2
            )

            shape = [
                (x, y - 17),
                (x - 23, y - 2),
                (x - 18, y + 15),
                (x, y + 8),
                (x + 18, y + 15),
                (x + 23, y - 2)
            ]

            pygame.draw.polygon(
                self.screen,
                (28, 10, 55),
                shape
            )

            pygame.draw.polygon(
                self.screen,
                self.magenta,
                shape,
                2
            )

            pygame.draw.circle(
                self.screen,
                self.cyan,
                (x - 9, y),
                3
            )

            pygame.draw.circle(
                self.screen,
                self.cyan,
                (x + 9, y),
                3
            )

    def draw_bullets(self):
        for bullet in self.player_bullets:
            x = int(bullet["x"])
            y = int(bullet["y"])

            self.glow_line(
                (x, y + 14),
                (x, y - 12),
                self.cyan,
                4
            )

            pygame.draw.line(
                self.screen,
                self.white,
                (x, y + 10),
                (x, y - 10),
                2
            )

        for bullet in self.enemy_bullets:
            x = int(bullet["x"])
            y = int(bullet["y"])

            self.glow_line(
                (x, y - 10),
                (x, y + 12),
                self.magenta,
                4
            )

            pygame.draw.line(
                self.screen,
                (255, 210, 240),
                (x, y - 7),
                (x, y + 9),
                2
            )

    def draw_explosions(self):
        for explosion in self.explosions:
            radius = max(
                3,
                35 - explosion["life"]
            )

            self.glow_circle(
                explosion["x"],
                explosion["y"],
                radius,
                self.magenta,
                2
            )

            pygame.draw.circle(
                self.screen,
                self.cyan,
                (
                    int(explosion["x"]),
                    int(explosion["y"])
                ),
                radius,
                2
            )

    def draw_panel(self):
        panel = pygame.Rect(
            490, 125, 275, 390
        )

        pygame.draw.rect(
            self.screen,
            (6, 10, 28),
            panel,
            border_radius=18
        )

        self.neon_rect(
            panel,
            self.cyan,
            18,
            2
        )

        pygame.draw.rect(
            self.screen,
            (10, 14, 38),
            panel.inflate(-10, -10),
            1,
            border_radius=14
        )

        self.draw_tabs()

        if self.mode == "login":

            self.draw_field(
                "USERNAME",
                self.username,
                pygame.Rect(520, 230, 215, 48),
                "username"
            )

            self.draw_field(
                "PASSWORD",
                self.password,
                pygame.Rect(520, 305, 215, 48),
                "password"
            )

            self.draw_button(
                pygame.Rect(520, 385, 215, 50),
                "ENTER"
            )

        else:

            self.draw_field(
                "USERNAME",
                self.username,
                pygame.Rect(520, 215, 215, 48),
                "username"
            )

            self.draw_field(
                "PASSWORD",
                self.password,
                pygame.Rect(520, 280, 215, 48),
                "password"
            )

            self.draw_field(
                "CONFIRM",
                self.confirm,
                pygame.Rect(520, 345, 215, 48),
                "confirm"
            )

            self.draw_button(
                pygame.Rect(520, 420, 215, 50),
                "CREATE"
            )

        if self.message:

            font = pygame.font.SysFont(
                "arial", 12, bold=True
            )

            color = (
                self.cyan
                if self.message_type == "success"
                else self.magenta
            )

            text = font.render(
                self.message,
                True,
                color
            )

            self.screen.blit(
                text,
                text.get_rect(
                    center=(627, 490)
                )
            )

    def draw_tabs(self):
        login = pygame.Rect(
            520, 160, 100, 42
        )

        signup = pygame.Rect(
            635, 160, 100, 42
        )

        active = (
            login
            if self.mode == "login"
            else signup
        )

        inactive = (
            signup
            if self.mode == "login"
            else login
        )

        pygame.draw.rect(
            self.screen,
            (8, 18, 42),
            inactive,
            border_radius=10
        )

        pygame.draw.rect(
            self.screen,
            (8, 30, 50),
            active,
            border_radius=10
        )

        self.neon_rect(
            active,
            self.cyan,
            10,
            2
        )

        font = pygame.font.SysFont(
            "arial", 13, bold=True
        )

        login_text = font.render(
            "LOG IN",
            True,
            self.cyan
            if self.mode == "login"
            else (100, 110, 145)
        )

        signup_text = font.render(
            "SIGN UP",
            True,
            self.cyan
            if self.mode == "signup"
            else (100, 110, 145)
        )

        self.screen.blit(
            login_text,
            login_text.get_rect(
                center=login.center
            )
        )

        self.screen.blit(
            signup_text,
            signup_text.get_rect(
                center=signup.center
            )
        )

    def draw_field(self, label, value, rect, field):
        active = self.active == field
        color = (
            self.cyan
            if active
            else (65, 80, 120)
        )

        pygame.draw.rect(
            self.screen,
            (4, 8, 25),
            rect,
            border_radius=9
        )

        self.neon_rect(
            rect,
            color,
            9,
            1
        )

        label_font = pygame.font.SysFont(
            "arial", 10, bold=True
        )

        self.screen.blit(
            label_font.render(
                label,
                True,
                self.cyan
                if active
                else (120, 135, 170)
            ),
            (rect.x + 12, rect.y + 7)
        )

        display = value

        if field == "password" and not self.show_password:
            display = "*" * len(value)

        if field == "confirm" and not self.show_confirm:
            display = "*" * len(value)

        value_font = pygame.font.SysFont(
            "arial", 15
        )

        text = value_font.render(
            display,
            True,
            self.white
        )

        self.screen.blit(
            text,
            (rect.x + 12, rect.y + 23)
        )

        if active and (self.time // 30) % 2 == 0:
            cursor_x = (
                rect.x +
                14 +
                text.get_width()
            )

            pygame.draw.line(
                self.screen,
                self.cyan,
                (cursor_x, rect.y + 22),
                (cursor_x, rect.y + 39),
                2
            )

        if field == "password":
            self.draw_eye(
                pygame.Rect(
                    rect.right - 35,
                    rect.y + 9,
                    25,
                    28
                ),
                self.show_password
            )

        if field == "confirm":
            self.draw_eye(
                pygame.Rect(
                    rect.right - 35,
                    rect.y + 9,
                    25,
                    28
                ),
                self.show_confirm
            )

    def draw_eye(self, rect, visible):
        pygame.draw.ellipse(
            self.screen,
            self.cyan,
            rect,
            2
        )

        pygame.draw.circle(
            self.screen,
            self.cyan,
            rect.center,
            4
        )

        if not visible:
            pygame.draw.line(
                self.screen,
                self.magenta,
                (rect.left - 2, rect.bottom + 2),
                (rect.right + 2, rect.top - 2),
                2
            )

    def draw_button(self, rect, text):
        pulse = (
            math.sin(self.time * 0.008) + 1
        ) / 2

        pygame.draw.rect(
            self.screen,
            (5, 18, 38),
            rect,
            border_radius=11
        )

        self.neon_rect(
            rect,
            (
                0,
                int(190 + pulse * 65),
                255
            ),
            11,
            2
        )

        font = pygame.font.SysFont(
            "arial", 14, bold=True
        )

        surface = font.render(
            text,
            True,
            self.white
        )

        self.screen.blit(
            surface,
            surface.get_rect(
                center=rect.center
            )
        )

    def draw_popup(self):
        overlay = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 10, 175)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        box = pygame.Rect(
            210, 185, 380, 230
        )

        pygame.draw.rect(
            self.screen,
            (5, 12, 32),
            box,
            border_radius=18
        )

        self.neon_rect(
            box,
            self.cyan,
            18,
            2
        )

        self.glow_circle(
            400, 235, 20,
            self.cyan,
            3
        )

        pygame.draw.circle(
            self.screen,
            self.cyan,
            (400, 235),
            24,
            2
        )

        pygame.draw.line(
            self.screen,
            self.white,
            (390, 235),
            (397, 242),
            3
        )

        pygame.draw.line(
            self.screen,
            self.white,
            (397, 242),
            (411, 225),
            3
        )

        title_font = pygame.font.SysFont(
            "arial", 24, bold=True
        )

        body_font = pygame.font.SysFont(
            "arial", 14
        )

        title = title_font.render(
            "ACCOUNT CREATED",
            True,
            self.cyan
        )

        self.screen.blit(
            title,
            title.get_rect(
                center=(400, 285)
            )
        )

        lines = [
            ("Your Space Invaders account has been", self.white),
            ("successfully created.", self.white),
            ("You can now log in.", self.magenta)
        ]

        for i, (line, color) in enumerate(lines):
            text = body_font.render(
                line,
                True,
                color
            )

            self.screen.blit(
                text,
                text.get_rect(
                    center=(400, 320 + i * 22)
                )
            )

    def login(self):
        username = self.username.strip()

        if not username or not self.password:
            self.message = "ENTER USERNAME AND PASSWORD"
            self.message_type = "error"
            return None

        result = login_player(
            username,
            self.password
        )

        if result:
            self.username = ""
            self.password = ""
            self.confirm = ""

            self.show_password = False
            self.show_confirm = False

            self.message = ""
            self.message_type = ""

            self.active = "username"

            return result

        self.message = "INVALID USERNAME ID OR PASSWORD"
        self.message_type = "error"

        return None

    def signup(self):
        username = self.username.strip()

        if not username or not self.password or not self.confirm:
            self.message = "COMPLETE ALL FIELDS"
            self.message_type = "error"
            return None

        if self.password != self.confirm:
            self.message = "PASSWORDS DO NOT MATCH"
            self.message_type = "error"
            return None

        result = register_player(
            username,
            self.password
        )

        if result:
            self.popup = True
            self.popup_timer = 180
            self.mode = "login"

            self.clear_fields()

            return None

        self.message = "USERNAME ALREADY EXISTS"
        self.message_type = "error"

        return None

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            if self.popup:
                if event.key in (
                    pygame.K_RETURN,
                    pygame.K_ESCAPE,
                    pygame.K_SPACE
                ):
                    self.popup = False

                return None

            if event.key == pygame.K_ESCAPE:
                return None

            if event.key == pygame.K_TAB:

                if self.mode == "login":
                    self.active = (
                        "password"
                        if self.active == "username"
                        else "username"
                    )

                else:
                    fields = [
                        "username",
                        "password",
                        "confirm"
                    ]

                    self.active = fields[
                        (fields.index(self.active) + 1) % 3
                    ]

            elif event.key == pygame.K_BACKSPACE:

                if self.active == "username":
                    self.username = self.username[:-1]

                elif self.active == "password":
                    self.password = self.password[:-1]

                else:
                    self.confirm = self.confirm[:-1]

            elif event.key == pygame.K_RETURN:

                if self.mode == "login":
                    return self.login()

                return self.signup()

            elif event.unicode.isprintable():

                if self.active == "username":
                    if len(self.username) < 25:
                        self.username += event.unicode

                elif self.active == "password":
                    if len(self.password) < 30:
                        self.password += event.unicode

                elif self.active == "confirm":
                    if len(self.confirm) < 30:
                        self.confirm += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse = event.pos

            if self.popup:
                self.popup = False
                return None

            login_tab = pygame.Rect(
                520, 160, 100, 42
            )

            signup_tab = pygame.Rect(
                635, 160, 100, 42
            )

            if login_tab.collidepoint(mouse):
                self.mode = "login"
                self.clear_fields()
                return None

            if signup_tab.collidepoint(mouse):
                self.mode = "signup"
                self.clear_fields()
                return None

            if self.mode == "login":

                user = pygame.Rect(
                    520, 230, 215, 48
                )

                password = pygame.Rect(
                    520, 305, 215, 48
                )

                button = pygame.Rect(
                    520, 385, 215, 50
                )

                eye = pygame.Rect(
                    700, 305, 35, 48
                )

                if user.collidepoint(mouse):
                    self.active = "username"

                elif password.collidepoint(mouse):
                    self.active = "password"

                if eye.collidepoint(mouse):
                    self.show_password = not self.show_password

                if button.collidepoint(mouse):
                    return self.login()

            else:

                user = pygame.Rect(
                    520, 215, 215, 48
                )

                password = pygame.Rect(
                    520, 280, 215, 48
                )

                confirm = pygame.Rect(
                    520, 345, 215, 48
                )

                button = pygame.Rect(
                    520, 420, 215, 50
                )

                pass_eye = pygame.Rect(
                    700, 280, 35, 48
                )

                confirm_eye = pygame.Rect(
                    700, 345, 35, 48
                )

                if user.collidepoint(mouse):
                    self.active = "username"

                elif password.collidepoint(mouse):
                    self.active = "password"

                elif confirm.collidepoint(mouse):
                    self.active = "confirm"

                if pass_eye.collidepoint(mouse):
                    self.show_password = not self.show_password

                if confirm_eye.collidepoint(mouse):
                    self.show_confirm = not self.show_confirm

                if button.collidepoint(mouse):
                    return self.signup()

        return None

    def update(self, events):
        self.time += 1
        self.update_stars()

        if not self.popup:
            self.update_player()
            self.update_player_fire()
            self.update_enemy_fire()
            self.update_bullets()
            self.check_collisions()
            self.update_explosions()

        else:
            self.popup_timer -= 1

            if self.popup_timer <= 0:
                self.popup = False

        result = None

        for event in events:
            event_result = self.handle_event(event)

            if event_result:
                result = event_result

        self.draw_background()
        self.draw_title()
        self.draw_enemies()
        self.draw_spaceship()
        self.draw_bullets()
        self.draw_explosions()
        self.draw_panel()

        if self.popup:
            self.draw_popup()

        return result