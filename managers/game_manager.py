import pygame
import random
import math
import json
import os

from entities.player import Player
from entities.button import MobileButtons
from entities.enemy import Enemy
from entities.bullet import Bullet
from db import save_score, get_highest_score, load_leaderboard


class GameManager:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.w = width
        self.h = height

        self.font = pygame.font.SysFont("Arial", 15, bold=True)
        self.small = pygame.font.SysFont("Arial", 11, bold=True)
        self.mid = pygame.font.SysFont("Arial", 21, bold=True)
        self.big = pygame.font.SysFont("Arial", 44, bold=True)
        self.huge = pygame.font.SysFont("Arial", 56, bold=True)

        self.player_name = ""
        self.player_id = None

        self.highest_score = 0
        self.leaderboard_high = 0

        self.state = "playing"

        self.level = 1
        self.level_flash = 90
        self.screen_time = 0

        self.hit_timer = 0
        self.hit_x = 0
        self.hit_y = 0
        self.hit_particles = []
        self.shake_amount = 0

        base_dir = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        self.settings_file = os.path.join(
            base_dir,
            "settings.json"
        )

        self.stars = []

        for i in range(90):
            self.stars.append({
                "x": random.randint(0, self.w),
                "y": random.randint(80, self.h),
                "speed": random.uniform(0.15, 0.7),
                "size": random.choice([1, 1, 1, 2]),
                "phase": random.uniform(0, math.pi * 2)
            })

        cx = width // 2

        self.again = pygame.Rect(
            cx - 170,
            415,
            340,
            44
        )

        self.lb = pygame.Rect(
            cx - 170,
            470,
            160,
            38
        )

        self.menu = pygame.Rect(
            cx + 10,
            470,
            160,
            38
        )

        self.reset()

    def show_controls(self):
        try:
            with open(
                self.settings_file,
                "r",
                encoding="utf-8"
            ) as file:
                settings = json.load(file)

            return settings.get(
                "show_controls",
                True
            )

        except:
            return True

    def set_player(self, player):
        if not player:
            self.player_id = None
            self.player_name = ""
            self.highest_score = 0
            self.leaderboard_high = 0
            self.reset()
            return

        self.player_id = player.get("player_id")
        self.player_name = player.get("username", "")

        try:
            self.highest_score = int(
                get_highest_score(self.player_id) or 0
            )
        except Exception:
            self.highest_score = 0

        try:
            players = load_leaderboard()

            if players:
                self.leaderboard_high = int(
                    players[0].get("score", 0) or 0
                )
            else:
                self.leaderboard_high = 0

        except Exception:
            self.leaderboard_high = 0

        self.reset()
        self.state = "playing"

    def reset(self):
        self.player = Player(
            self.w,
            self.h
        )

        self.buttons = MobileButtons()

        self.bullet = None
        self.enemies = []

        self.score = 0
        self.spawn = 5
        self.timer = 0

        self.history = []

        self.saved = False

        self.level = 1
        self.level_flash = 90

        self.hit_timer = 0
        self.hit_x = 0
        self.hit_y = 0
        self.hit_particles = []
        self.shake_amount = 0

        self.spawn_enemies()

    def get_score(self):
        return int(self.score)

    def spawn_enemies(self):
        self.enemies = [
            Enemy(
                i,
                self.spawn,
                self.w
            )
            for i in range(self.spawn)
        ]

        self.timer = 0

    def update(self, events):
        self.screen_time += 1

        if self.state == "playing":

            # ESC opens Settings and pauses the game
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "settings"

            self.play(events)

            if self.state == "hit":
                self.draw_hit_effect()
                return None

            if self.state == "game_over":
                return self.game_over(events)

            self.draw()
            return None

        if self.state == "hit":
            self.draw_hit_effect()
            return None

        if self.state == "game_over":
            return self.game_over(events)

        return None

    def play(self, events):
        self.history.append(
            (
                self.player.x,
                self.player.y
            )
        )

        if len(self.history) > 60:
            self.history.pop(0)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.player.move_left()

        if keys[pygame.K_RIGHT]:
            self.player.move_right()

        fired = False

        if self.show_controls():
            fired = self.buttons.handle_mouse(
                self.player,
                events
            )

        fired |= any(
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_SPACE
            for event in events
        )

        if fired and self.bullet is None:
            self.bullet = Bullet(
                self.player.x +
                self.player.width // 2 - 16,
                self.player.y
            )

        self.player.keep_inside_screen()

        if self.bullet:
            self.bullet.update()

            if not self.bullet.is_active:
                self.bullet = None

        self.timer += 1

        if self.timer >= 180:
            waiting = [
                enemy
                for enemy in self.enemies
                if enemy.state == "waiting"
            ]

            if waiting and self.history:
                random.choice(
                    waiting
                ).start_drop(
                    *self.history[0]
                )

            self.timer = 0

        for enemy in self.enemies:
            enemy.update()

        if self.enemies and all(
            enemy.state == "offscreen"
            for enemy in self.enemies
        ):
            self.spawn += 1

            self.level = max(
                1,
                self.spawn - 4
            )

            self.level_flash = 90

            self.spawn_enemies()

        if self.level_flash > 0:
            self.level_flash -= 1

        self.collisions()

    def collisions(self):
        player_rect = self.player.get_rect()

        for enemy in self.enemies:
            if enemy.state == "offscreen":
                continue

            enemy_rect = enemy.get_rect()

            if player_rect.colliderect(enemy_rect):
                self.state = "hit"

                self.bullet = None

                self.hit_timer = 35

                self.hit_x = (
                    player_rect.centerx +
                    enemy_rect.centerx
                ) // 2

                self.hit_y = (
                    player_rect.centery +
                    enemy_rect.centery
                ) // 2

                self.shake_amount = 14

                self.hit_particles = []

                for i in range(45):
                    angle = random.uniform(
                        0,
                        math.pi * 2
                    )

                    speed = random.uniform(
                        2,
                        8
                    )

                    self.hit_particles.append({
                        "x": self.hit_x,
                        "y": self.hit_y,
                        "dx": math.cos(angle) * speed,
                        "dy": math.sin(angle) * speed,
                        "life": random.randint(15, 35),
                        "size": random.randint(2, 5)
                    })

                if hasattr(
                    self.player,
                    "is_blinking"
                ):
                    self.player.is_blinking = False

                return

            if (
                self.bullet
                and self.bullet.get_rect().colliderect(
                    enemy_rect
                )
            ):
                enemy.state = "offscreen"
                self.bullet = None
                self.score = int(self.score) + 1
                break

    def draw_hit_effect(self):
        self.background()

        shake_x = 0
        shake_y = 0

        if self.shake_amount > 0:
            shake_x = random.randint(
                -self.shake_amount,
                self.shake_amount
            )

            shake_y = random.randint(
                -self.shake_amount,
                self.shake_amount
            )

            self.shake_amount -= 1

        game_surface = pygame.Surface(
            (self.w, self.h),
            pygame.SRCALPHA
        )

        old_screen = self.screen

        self.screen = game_surface

        self.hud()

        self.player.draw(
            self.screen
        )

        for enemy in self.enemies:
            enemy.draw(
                self.screen
            )

        self.screen = old_screen

        self.screen.blit(
            game_surface,
            (
                shake_x,
                shake_y
            )
        )

        flash = pygame.Surface(
            (self.w, self.h),
            pygame.SRCALPHA
        )

        alpha = int(
            170 *
            (self.hit_timer / 35)
        )

        flash.fill(
            (
                255,
                20,
                45,
                alpha
            )
        )

        self.screen.blit(
            flash,
            (0, 0)
        )

        impact_size = int(
            15 +
            (35 - self.hit_timer) * 2
        )

        pygame.draw.circle(
            self.screen,
            (255, 230, 80),
            (
                self.hit_x,
                self.hit_y
            ),
            impact_size,
            3
        )

        pygame.draw.circle(
            self.screen,
            (255, 70, 30),
            (
                self.hit_x,
                self.hit_y
            ),
            max(
                5,
                impact_size // 2
            ),
            4
        )

        for particle in self.hit_particles:
            if particle["life"] <= 0:
                continue

            particle["x"] += particle["dx"]
            particle["y"] += particle["dy"]

            particle["dy"] += 0.15

            particle["life"] -= 1

            alpha = min(
                255,
                particle["life"] * 10
            )

            particle_surface = pygame.Surface(
                (
                    particle["size"] * 4,
                    particle["size"] * 4
                ),
                pygame.SRCALPHA
            )

            pygame.draw.circle(
                particle_surface,
                (
                    255,
                    random.randint(80, 230),
                    30,
                    alpha
                ),
                (
                    particle["size"] * 2,
                    particle["size"] * 2
                ),
                particle["size"]
            )

            self.screen.blit(
                particle_surface,
                (
                    int(
                        particle["x"] -
                        particle["size"] * 2
                    ),
                    int(
                        particle["y"] -
                        particle["size"] * 2
                    )
                )
            )

        self.hit_timer -= 1

        if self.hit_timer <= 0:
            self.state = "game_over"

    def game_over(self, events):
        if not self.saved:
            if self.player_id:
                try:
                    save_score(
                        self.player_id,
                        int(self.score),
                        self.level
                    )

                    if self.score > self.highest_score:
                        self.highest_score = self.score

                    players = load_leaderboard()

                    if players:
                        self.leaderboard_high = int(
                            players[0].get("score", 0) or 0
                        )

                except Exception as e:
                    print(
                        "Score save error:",
                        e
                    )

            self.saved = True

        self.draw_game_over()

        for event in events:
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                if self.again.collidepoint(event.pos):
                    self.reset()
                    self.state = "playing"
                    return None

                if self.lb.collidepoint(event.pos):
                    return "leaderboard"

                if self.menu.collidepoint(event.pos):
                    return "home"

        return None

    def draw(self):
        self.background()

        self.hud()

        self.player.draw(
            self.screen
        )

        for enemy in self.enemies:
            enemy.draw(
                self.screen
            )

        if self.bullet:
            self.bullet.draw(
                self.screen
            )

        if self.show_controls():
            self.buttons.draw(
                self.screen
            )

    def background(self):
        self.screen.fill(
            (1, 4, 14)
        )

        for star in self.stars:
            star["y"] += star["speed"]

            if star["y"] > self.h:
                star["y"] = 78
                star["x"] = random.randint(
                    0,
                    self.w
                )

            pulse = (
                0.5 +
                0.5 *
                math.sin(
                    self.screen_time * 0.04 +
                    star["phase"]
                )
            )

            brightness = int(
                100 +
                pulse * 120
            )

            pygame.draw.circle(
                self.screen,
                (
                    20,
                    brightness,
                    min(
                        255,
                        brightness + 40
                    )
                ),
                (
                    int(star["x"]),
                    int(star["y"])
                ),
                star["size"]
            )

        pygame.draw.circle(
            self.screen,
            (2, 18, 35),
            (20, 350),
            125
        )

        pygame.draw.circle(
            self.screen,
            (0, 75, 105),
            (20, 350),
            125,
            2
        )

        pygame.draw.circle(
            self.screen,
            (10, 5, 28),
            (785, 280),
            130
        )

        pygame.draw.circle(
            self.screen,
            (105, 25, 155),
            (785, 280),
            130,
            2
        )

        for i in range(3):
            radius = 145 + i * 12

            pygame.draw.arc(
                self.screen,
                (
                    20,
                    55 + i * 20,
                    80 + i * 20
                ),
                (
                    -radius + 30,
                    280,
                    radius * 2,
                    radius
                ),
                math.radians(200),
                math.radians(335),
                1
            )

        pygame.draw.line(
            self.screen,
            (0, 80, 110),
            (15, 565),
            (785, 565),
            1
        )

    def hud(self):
        cyan = (0, 230, 255)
        white = (235, 250, 255)
        gold = (255, 220, 75)
        purple = (200, 80, 255)
        muted = (100, 160, 180)

        name = (
            self.player_name.upper()
            if self.player_name
            else "PLAYER"
        )

        if len(name) > 12:
            name = name[:12]

        high = max(
            self.highest_score,
            self.leaderboard_high,
            self.score
        )

        self.text(
            "PLAYER",
            self.small,
            (25, 12),
            muted
        )

        self.text(
            name,
            self.font,
            (25, 33),
            white
        )

        self.text_center(
            "SCORE",
            self.small,
            (190, 17),
            muted
        )

        self.text_center(
            f"{self.score:04d}",
            self.mid,
            (190, 44),
            white
        )

        self.text_center(
            "LEVEL",
            self.small,
            (400, 17),
            muted
        )

        self.text_center(
            f"{self.level:02d}",
            self.mid,
            (400, 44),
            purple
        )

        self.text_center(
            "HIGHEST SCORE",
            self.small,
            (610, 17),
            muted
        )

        self.text_center(
            f"{high:04d}",
            self.mid,
            (610, 44),
            gold
        )

        pygame.draw.line(
            self.screen,
            (0, 60, 85),
            (22, 72),
            (778, 72),
            1
        )

        pygame.draw.line(
            self.screen,
            cyan,
            (22, 72),
            (145, 72),
            2
        )

        pygame.draw.line(
            self.screen,
            cyan,
            (655, 72),
            (778, 72),
            2
        )

        if self.level_flash > 0:
            alpha = min(
                255,
                self.level_flash * 3
            )

            surface = pygame.Surface(
                (self.w, 100),
                pygame.SRCALPHA
            )

            image = self.big.render(
                f"LEVEL {self.level}",
                True,
                (
                    100,
                    230,
                    255,
                    alpha
                )
            )

            surface.blit(
                image,
                image.get_rect(
                    center=(400, 115)
                )
            )

            self.screen.blit(
                surface,
                (0, 0)
            )

    def draw_game_over(self):
        self.background()

        overlay = pygame.Surface(
            (self.w, self.h),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 2, 12, 210)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        pulse = (
            0.5 +
            0.5 *
            math.sin(
                self.screen_time * 0.07
            )
        )

        panel = pygame.Rect(
            145,
            65,
            510,
            465
        )

        self.panel_glow(
            panel,
            (255, 25, 90)
        )

        pygame.draw.rect(
            self.screen,
            (3, 9, 23),
            panel,
            border_radius=20
        )

        pygame.draw.rect(
            self.screen,
            (105, 30, 65),
            panel,
            1,
            border_radius=20
        )

        pygame.draw.line(
            self.screen,
            (255, 45, 100),
            (175, 100),
            (625, 100),
            2
        )

        self.text_center(
            "MISSION FAILED",
            self.small,
            (400, 87),
            (100, 145, 165)
        )

        icon_x = 400
        icon_y = 145

        glow_radius = int(
            34 +
            pulse * 6
        )

        pygame.draw.circle(
            self.screen,
            (70, 8, 40),
            (icon_x, icon_y),
            glow_radius
        )

        pygame.draw.circle(
            self.screen,
            (255, 40, 90),
            (icon_x, icon_y),
            30,
            2
        )

        pygame.draw.circle(
            self.screen,
            (255, 80, 115),
            (icon_x, icon_y),
            22,
            1
        )

        pygame.draw.line(
            self.screen,
            (255, 70, 110),
            (
                icon_x - 10,
                icon_y - 10
            ),
            (
                icon_x + 10,
                icon_y + 10
            ),
            4
        )

        pygame.draw.line(
            self.screen,
            (255, 70, 110),
            (
                icon_x + 10,
                icon_y - 10
            ),
            (
                icon_x - 10,
                icon_y + 10
            ),
            4
        )

        title = self.huge.render(
            "GAME OVER",
            True,
            (255, 55, 105)
        )

        title_rect = title.get_rect(
            center=(400, 205)
        )

        self.screen.blit(
            title,
            title_rect
        )

        self.stat_box(
            175,
            310,
            135,
            65,
            "SCORE",
            f"{self.score:04d}",
            (255, 210, 70)
        )

        self.stat_box(
            332,
            310,
            135,
            65,
            "LEVEL",
            f"{self.level:02d}",
            (190, 75, 255)
        )

        self.stat_box(
            490,
            310,
            135,
            65,
            "HIGHEST SCORE",
            f"{max(self.highest_score, self.leaderboard_high):04d}",
            (0, 220, 245)
        )

        self.again = pygame.Rect(
            230,
            400,
            340,
            44
        )

        self.lb = pygame.Rect(
            230,
            455,
            160,
            38
        )

        self.menu = pygame.Rect(
            410,
            455,
            160,
            38
        )

        self.game_over_button(
            self.again,
            "PLAY AGAIN",
            "restart",
            True
        )

        self.game_over_button(
            self.lb,
            "LEADERBOARD",
            "trophy",
            False
        )

        self.game_over_button(
            self.menu,
            "MAIN MENU",
            "home",
            False
        )

        pygame.draw.line(
            self.screen,
            (0, 55, 80),
            (175, 490),
            (625, 490),
            1
        )

        self.text_center(
            "SYSTEM READY",
            self.small,
            (400, 510),
            (65, 105, 125)
        )

    def game_over_button(
        self,
        rect,
        label,
        icon,
        primary=False
    ):
        hover = rect.collidepoint(
            pygame.mouse.get_pos()
        )

        if primary:
            normal_fill = (25, 8, 28)
            normal_border = (255, 45, 100)
        else:
            normal_fill = (5, 18, 32)
            normal_border = (0, 155, 190)

        if hover:
            fill = (12, 42, 55)
            border = (0, 235, 255)

            self.box_glow(
                rect,
                border
            )
        else:
            fill = normal_fill
            border = normal_border

        pygame.draw.rect(
            self.screen,
            fill,
            rect,
            border_radius=12
        )

        pygame.draw.rect(
            self.screen,
            border,
            rect,
            2,
            border_radius=12
        )

        cx = rect.x + 28
        cy = rect.centery

        if icon == "restart":
            pygame.draw.arc(
                self.screen,
                border,
                (
                    cx - 9,
                    cy - 9,
                    18,
                    18
                ),
                math.radians(35),
                math.radians(315),
                3
            )

            pygame.draw.polygon(
                self.screen,
                border,
                [
                    (
                        cx + 6,
                        cy - 9
                    ),
                    (
                        cx + 11,
                        cy
                    ),
                    (
                        cx + 1,
                        cy - 2
                    )
                ]
            )

        elif icon == "trophy":
            pygame.draw.rect(
                self.screen,
                border,
                (
                    cx - 7,
                    cy - 8,
                    14,
                    12
                ),
                border_radius=3
            )

            pygame.draw.arc(
                self.screen,
                border,
                (
                    cx - 14,
                    cy - 7,
                    9,
                    12
                ),
                math.radians(270),
                math.radians(90),
                2
            )

            pygame.draw.arc(
                self.screen,
                border,
                (
                    cx + 5,
                    cy - 7,
                    9,
                    12
                ),
                math.radians(90),
                math.radians(270),
                2
            )

            pygame.draw.line(
                self.screen,
                border,
                (
                    cx,
                    cy + 4
                ),
                (
                    cx,
                    cy + 10
                ),
                2
            )

            pygame.draw.line(
                self.screen,
                border,
                (
                    cx - 7,
                    cy + 11
                ),
                (
                    cx + 7,
                    cy + 11
                ),
                2
            )

        elif icon == "home":
            pygame.draw.polygon(
                self.screen,
                border,
                [
                    (
                        cx - 11,
                        cy
                    ),
                    (
                        cx,
                        cy - 10
                    ),
                    (
                        cx + 11,
                        cy
                    ),
                    (
                        cx + 8,
                        cy
                    ),
                    (
                        cx + 8,
                        cy + 10
                    ),
                    (
                        cx - 8,
                        cy + 10
                    ),
                    (
                        cx - 8,
                        cy
                    )
                ]
            )

            pygame.draw.rect(
                self.screen,
                fill,
                (
                    cx - 3,
                    cy + 3,
                    6,
                    7
                )
            )

        self.text_center(
            label,
            self.font if primary else self.small,
            (
                rect.centerx + 18,
                rect.centery
            ),
            (235, 248, 252)
        )

    def stat_box(
        self,
        x,
        y,
        width,
        height,
        label,
        value,
        color
    ):
        rect = pygame.Rect(
            x,
            y,
            width,
            height
        )

        self.box_glow(
            rect,
            color
        )

        pygame.draw.rect(
            self.screen,
            (4, 18, 32),
            rect,
            border_radius=15
        )

        pygame.draw.rect(
            self.screen,
            (0, 70, 95),
            rect,
            1,
            border_radius=15
        )

        pygame.draw.line(
            self.screen,
            color,
            (
                x + 20,
                y
            ),
            (
                x + width - 20,
                y
            ),
            2
        )

        self.text_center(
            label,
            self.small,
            (
                x + width // 2,
                y + 22
            ),
            (95, 150, 170)
        )

        self.text_center(
            value,
            self.mid,
            (
                x + width // 2,
                y + 51
            ),
            color
        )

    def button(
        self,
        rect,
        label,
        primary=False
    ):
        hover = rect.collidepoint(
            pygame.mouse.get_pos()
        )

        if primary:
            base = (5, 30, 45)
            border = (0, 220, 245)
        else:
            base = (4, 20, 33)
            border = (0, 150, 180)

        if hover:
            fill = (9, 55, 70)
            edge = (0, 255, 255)

            self.panel_glow(
                rect,
                (0, 220, 255)
            )
        else:
            fill = base
            edge = border

        pygame.draw.rect(
            self.screen,
            fill,
            rect,
            border_radius=22
        )

        pygame.draw.rect(
            self.screen,
            edge,
            rect,
            2,
            border_radius=22
        )

        self.text_center(
            label,
            self.font,
            rect.center,
            (230, 248, 252)
        )

    def small_button(
        self,
        rect,
        label
    ):
        hover = rect.collidepoint(
            pygame.mouse.get_pos()
        )

        if hover:
            fill = (8, 43, 57)
            border = (0, 255, 255)

            self.panel_glow(
                rect,
                (0, 210, 240)
            )
        else:
            fill = (3, 19, 31)
            border = (0, 135, 165)

        pygame.draw.rect(
            self.screen,
            fill,
            rect,
            border_radius=19
        )

        pygame.draw.rect(
            self.screen,
            border,
            rect,
            2,
            border_radius=19
        )

        self.text_center(
            label,
            self.small,
            rect.center,
            (215, 240, 248)
        )

    def panel_glow(
        self,
        rect,
        color
    ):
        surface = pygame.Surface(
            (self.w, self.h),
            pygame.SRCALPHA
        )

        for size in range(
            10,
            0,
            -1
        ):
            expanded = rect.inflate(
                size * 2,
                size * 2
            )

            alpha = 2 + size * 2

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
                border_radius=25
            )

        self.screen.blit(
            surface,
            (0, 0)
        )

    def box_glow(
        self,
        rect,
        color
    ):
        surface = pygame.Surface(
            (self.w, self.h),
            pygame.SRCALPHA
        )

        for size in range(
            5,
            0,
            -1
        ):
            expanded = rect.inflate(
                size * 2,
                size * 2
            )

            pygame.draw.rect(
                surface,
                (
                    color[0],
                    color[1],
                    color[2],
                    2
                ),
                expanded,
                1,
                border_radius=16
            )

        self.screen.blit(
            surface,
            (0, 0)
        )

    def text(
        self,
        value,
        font,
        pos,
        color,
        center=False
    ):
        image = font.render(
            str(value),
            True,
            color
        )

        if center:
            self.screen.blit(
                image,
                image.get_rect(
                    center=pos
                )
            )
        else:
            self.screen.blit(
                image,
                pos
            )

    def text_center(
        self,
        value,
        font,
        pos,
        color
    ):
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