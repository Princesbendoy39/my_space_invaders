import pygame
import random
import math

from db import (
    get_highest_score,
    update_player_profile,
    delete_player,
    get_db_connection
)


class ProfileManager:

    def __init__(self, screen, width, height):

        self.screen = screen
        self.w = width
        self.h = height

        self.title_font = pygame.font.SysFont(
            "Arial", 28, bold=True
        )
        self.name_font = pygame.font.SysFont(
            "Arial", 24, bold=True
        )
        self.medium_font = pygame.font.SysFont(
            "Arial", 18, bold=True
        )
        self.small_font = pygame.font.SysFont(
            "Arial", 14
        )
        self.tiny_font = pygame.font.SysFont(
            "Arial", 12
        )
        self.stat_font = pygame.font.SysFont(
            "Arial", 30, bold=True
        )

        self.bg = (5, 8, 18)
        self.panel = (10, 17, 32)
        self.panel2 = (14, 24, 43)

        self.cyan = (0, 220, 255)
        self.cyan_dark = (0, 120, 160)

        self.white = (235, 245, 255)
        self.gray = (145, 160, 180)

        self.green = (60, 230, 150)

        self.red = (255, 75, 95)
        self.red_dark = (150, 35, 50)

        self.border = (30, 95, 125)

        self.player_id = None
        self.username = ""

        self.current_score = 0
        self.highest_score = 0
        self.games_played = 0

        self.editing = False
        self.edit_text = ""
        self.cursor_visible = True
        self.cursor_timer = 0

        self.confirm_delete = False

        self.message = ""
        self.message_type = "info"
        self.message_timer = 0

        self.edit_button = pygame.Rect(
            490, 205, 110, 36
        )

        self.delete_button = pygame.Rect(
            610, 205, 110, 36
        )

        self.back_button = pygame.Rect(
            600, 520, 145, 34
        )

        self.username_box = pygame.Rect(
            200, 290, 400, 48
        )

        self.save_edit = pygame.Rect(
            260, 360, 110, 40
        )

        self.cancel_edit = pygame.Rect(
            430, 360, 110, 40
        )

        self.confirm_yes = pygame.Rect(
            260, 355, 110, 40
        )

        self.confirm_no = pygame.Rect(
            430, 355, 110, 40
        )

        self.stars = []

        for _ in range(90):
            self.stars.append({
                "x": random.randint(0, self.w),
                "y": random.randint(0, self.h),
                "size": random.choice([1, 1, 1, 2]),
                "speed": random.uniform(0.1, 0.5)
            })

        self.avatar = self.create_avatar()

    def set_player(self, player):

        if not player:
            self.clear_player()
            return

        if isinstance(player, dict):

            new_player_id = (
                player.get("player_id")
                or player.get("id")
                or player.get("username")
            )

            new_username = (
                player.get("username")
                or player.get("name")
                or "PLAYER"
            )

        else:

            new_player_id = getattr(
                player,
                "player_id",
                getattr(player, "id", None)
            )

            new_username = getattr(
                player,
                "username",
                getattr(player, "name", "PLAYER")
            )

        same_player = (
            self.player_id is not None
            and str(self.player_id) == str(new_player_id)
        )

        self.player_id = new_player_id
        self.username = str(new_username)

        if not same_player:
            self.current_score = 0

        self.highest_score = 0
        self.games_played = 0

        self.load_statistics()

    def clear_player(self):

        self.player_id = None
        self.username = ""

        self.current_score = 0
        self.highest_score = 0
        self.games_played = 0

        self.editing = False
        self.edit_text = ""

        self.confirm_delete = False

        self.message = ""
        self.message_timer = 0

    def set_current_score(self, score):

        try:
            self.current_score = int(score or 0)
        except (TypeError, ValueError):
            self.current_score = 0

    def load_statistics(self):

        if not self.player_id:
            self.highest_score = 0
            self.games_played = 0
            return

        try:
            self.highest_score = int(
                get_highest_score(self.player_id) or 0
            )
        except Exception:
            self.highest_score = 0

        self.games_played = 0

        conn = None
        cursor = None

        try:

            conn = get_db_connection()

            if not conn:
                return

            cursor = conn.cursor(
                dictionary=True
            )

            cursor.execute(
                """
                SELECT COUNT(*) AS games_played
                FROM scores
                WHERE player_id = %s
                """,
                (self.player_id,)
            )

            result = cursor.fetchone()

            if result:
                self.games_played = int(
                    result.get("games_played", 0) or 0
                )

        except Exception:

            self.games_played = 0

        finally:

            try:
                if cursor:
                    cursor.close()
            except Exception:
                pass

            try:
                if conn:
                    conn.close()
            except Exception:
                pass

    def create_avatar(self):

        surface = pygame.Surface(
            (150, 150),
            pygame.SRCALPHA
        )

        center = (75, 75)

        for radius in range(70, 45, -5):

            alpha = max(
                10,
                70 - (70 - radius) * 2
            )

            pygame.draw.circle(
                surface,
                (0, 220, 255, alpha),
                center,
                radius,
                2
            )

        pygame.draw.circle(
            surface,
            (8, 20, 35),
            center,
            55
        )

        pygame.draw.circle(
            surface,
            self.cyan,
            center,
            55,
            3
        )

        pygame.draw.circle(
            surface,
            (20, 50, 70),
            center,
            45
        )

        pygame.draw.circle(
            surface,
            self.cyan,
            (75, 62),
            17
        )

        pygame.draw.arc(
            surface,
            self.cyan,
            (45, 73, 60, 55),
            math.pi,
            math.pi * 2,
            6
        )

        pygame.draw.line(
            surface,
            self.cyan,
            (48, 105),
            (102, 105),
            6
        )

        return surface

    def update(self, events):

        for star in self.stars:

            star["y"] += star["speed"]

            if star["y"] > self.h:
                star["y"] = 0

        if self.message_timer > 0:

            self.message_timer -= 1

            if self.message_timer <= 0:
                self.message = ""

        self.cursor_timer += 1

        if self.cursor_timer >= 30:

            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

        if self.confirm_delete:

            for event in events:

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:
                        self.confirm_delete = False

                elif event.type == pygame.MOUSEBUTTONDOWN:

                    if event.button == 1:

                        if self.confirm_yes.collidepoint(event.pos):
                            return self.delete_account()

                        if self.confirm_no.collidepoint(event.pos):
                            self.confirm_delete = False

            self.draw()
            return None

        if self.editing:

            for event in events:

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:

                        self.editing = False
                        self.edit_text = self.username

                    elif event.key == pygame.K_BACKSPACE:

                        self.edit_text = self.edit_text[:-1]

                    elif event.key == pygame.K_RETURN:

                        self.save_profile()

                    elif len(self.edit_text) < 22:

                        if event.unicode.isprintable():
                            self.edit_text += event.unicode

                elif event.type == pygame.MOUSEBUTTONDOWN:

                    if event.button == 1:

                        if self.save_edit.collidepoint(event.pos):
                            self.save_profile()

                        elif self.cancel_edit.collidepoint(event.pos):

                            self.editing = False
                            self.edit_text = self.username

            self.draw()
            return None

        for event in events:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    return "home"

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    if self.back_button.collidepoint(event.pos):
                        return "home"

                    elif self.edit_button.collidepoint(event.pos):

                        self.editing = True
                        self.edit_text = self.username
                        self.cursor_visible = True

                    elif self.delete_button.collidepoint(event.pos):

                        self.confirm_delete = True

        self.draw()

        return None

    def save_profile(self):

        new_name = self.edit_text.strip()

        if not new_name:

            self.show_message(
                "PLAYER ID CANNOT BE EMPTY",
                "error"
            )

            return

        if len(new_name) < 3:

            self.show_message(
                "PLAYER ID IS TOO SHORT",
                "error"
            )

            return

        try:

            result = update_player_profile(
                self.player_id,
                new_name
            )

            if result is False:

                self.show_message(
                    "FAILED TO UPDATE PROFILE",
                    "error"
                )

                return

            self.username = new_name
            self.editing = False

            self.show_message(
                "PROFILE UPDATED SUCCESSFULLY",
                "success"
            )

        except Exception:

            self.show_message(
                "FAILED TO UPDATE PROFILE",
                "error"
            )

    def delete_account(self):

        try:

            result = delete_player(
                self.player_id
            )

            if result is False:

                self.confirm_delete = False

                self.show_message(
                    "FAILED TO DELETE ACCOUNT",
                    "error"
                )

                return None

            self.clear_player()

            return "login"

        except Exception:

            self.confirm_delete = False

            self.show_message(
                "FAILED TO DELETE ACCOUNT",
                "error"
            )

            return None

    def show_message(self, message, message_type="info"):

        self.message = message
        self.message_type = message_type
        self.message_timer = 180

    def draw(self):

        self.draw_background()
        self.draw_main_profile()
        self.draw_back_button()

        if self.message:
            self.draw_message()

        if self.editing:
            self.draw_edit_popup()

        if self.confirm_delete:
            self.draw_delete_popup()

    def draw_background(self):

        self.screen.fill(self.bg)

        for star in self.stars:

            pygame.draw.circle(
                self.screen,
                (80, 125, 150),
                (
                    int(star["x"]),
                    int(star["y"])
                ),
                star["size"]
            )

        pygame.draw.line(
            self.screen,
            (10, 45, 65),
            (0, 80),
            (800, 80),
            1
        )

        pygame.draw.line(
            self.screen,
            (10, 45, 65),
            (0, 570),
            (800, 570),
            1
        )

    def draw_main_profile(self):

        panel = pygame.Rect(
            40,
            100,
            720,
            460
        )

        pygame.draw.rect(
            self.screen,
            (0, 50, 70),
            panel.inflate(6, 6),
            border_radius=14
        )

        pygame.draw.rect(
            self.screen,
            self.panel,
            panel,
            border_radius=12
        )

        pygame.draw.rect(
            self.screen,
            self.border,
            panel,
            2,
            border_radius=12
        )

        title = self.title_font.render(
            "PLAYER PROFILE",
            True,
            self.cyan
        )

        self.screen.blit(
            title,
            (65, 125)
        )

        pygame.draw.line(
            self.screen,
            self.cyan_dark,
            (65, 160),
            (735, 160),
            1
        )

        self.draw_player_section()
        self.draw_statistics()

    def draw_player_section(self):

        avatar_rect = self.avatar.get_rect(
            center=(140, 240)
        )

        self.screen.blit(
            self.avatar,
            avatar_rect
        )

        label = self.tiny_font.render(
            "PLAYER NAME",
            True,
            self.cyan
        )

        self.screen.blit(
            label,
            (325, 180)
        )

        display_name = self.username.upper()

        if len(display_name) > 15:
            display_name = display_name[:15] + "..."

        name = self.name_font.render(
            display_name,
            True,
            self.white
        )

        self.screen.blit(
            name,
            (325, 202)
        )

        self.draw_button(
            self.edit_button,
            "EDIT PROFILE",
            self.cyan,
            self.cyan_dark
        )

        self.draw_button(
            self.delete_button,
            "DELETE",
            self.red,
            self.red_dark
        )

        pygame.draw.line(
            self.screen,
            (30, 70, 90),
            (325, 255),
            (735, 255),
            1
        )

        info = self.small_font.render(
            "Manage your pilot information",
            True,
            self.gray
        )

        self.screen.blit(
            info,
            (325, 275)
        )

    def draw_statistics(self):

        stats_title = self.medium_font.render(
            "COMBAT STATISTICS",
            True,
            self.cyan
        )

        self.screen.blit(
            stats_title,
            (65, 320)
        )

        pygame.draw.line(
            self.screen,
            (20, 65, 85),
            (65, 348),
            (735, 348),
            1
        )

        current_box = pygame.Rect(
            65,
            365,
            205,
            130
        )

        best_box = pygame.Rect(
            297,
            365,
            205,
            130
        )

        games_box = pygame.Rect(
            530,
            365,
            205,
            130
        )

        self.draw_stat_card(
            current_box,
            "CURRENT SCORE",
            self.current_score
        )

        self.draw_stat_card(
            best_box,
            "BEST SCORE",
            self.highest_score
        )

        self.draw_stat_card(
            games_box,
            "GAMES PLAYED",
            self.games_played
        )

    def draw_stat_card(
        self,
        rect,
        label,
        value
    ):

        pygame.draw.rect(
            self.screen,
            self.panel2,
            rect,
            border_radius=10
        )

        pygame.draw.rect(
            self.screen,
            (25, 80, 105),
            rect,
            2,
            border_radius=10
        )

        pygame.draw.line(
            self.screen,
            self.cyan,
            (rect.x + 15, rect.y + 2),
            (rect.right - 15, rect.y + 2),
            2
        )

        value_text = self.stat_font.render(
            str(value),
            True,
            self.white
        )

        self.screen.blit(
            value_text,
            (
                rect.centerx -
                value_text.get_width() // 2,
                rect.y + 32
            )
        )

        label_text = self.small_font.render(
            label,
            True,
            self.cyan
        )

        self.screen.blit(
            label_text,
            (
                rect.centerx -
                label_text.get_width() // 2,
                rect.y + 92
            )
        )

    def draw_button(
        self,
        rect,
        text,
        color,
        dark_color
    ):

        hovered = rect.collidepoint(
            pygame.mouse.get_pos()
        )

        if hovered:

            fill = dark_color
            border = color

        else:

            fill = (12, 25, 40)
            border = dark_color

        pygame.draw.rect(
            self.screen,
            fill,
            rect,
            border_radius=7
        )

        pygame.draw.rect(
            self.screen,
            border,
            rect,
            2,
            border_radius=7
        )

        text_surface = self.small_font.render(
            text,
            True,
            color
        )

        self.screen.blit(
            text_surface,
            (
                rect.centerx -
                text_surface.get_width() // 2,
                rect.centery -
                text_surface.get_height() // 2
            )
        )

    def draw_back_button(self):

        hovered = self.back_button.collidepoint(
            pygame.mouse.get_pos()
        )

        if hovered:

            fill = (15, 45, 60)
            border = self.cyan
            text_color = self.cyan

        else:

            fill = (8, 18, 30)
            border = self.cyan_dark
            text_color = self.gray

        pygame.draw.rect(
            self.screen,
            fill,
            self.back_button,
            border_radius=7
        )

        pygame.draw.rect(
            self.screen,
            border,
            self.back_button,
            1,
            border_radius=7
        )

        arrow = self.medium_font.render(
            "←",
            True,
            text_color
        )

        self.screen.blit(
            arrow,
            (
                self.back_button.x + 12,
                self.back_button.centery -
                arrow.get_height() // 2
            )
        )

        text = self.small_font.render(
            "BACK TO HOME",
            True,
            text_color
        )

        self.screen.blit(
            text,
            (
                self.back_button.x + 40,
                self.back_button.centery -
                text.get_height() // 2
            )
        )

    def draw_edit_popup(self):

        overlay = pygame.Surface(
            (self.w, self.h),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 175)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        popup = pygame.Rect(
            150,
            130,
            500,
            330
        )

        pygame.draw.rect(
            self.screen,
            (5, 15, 28),
            popup,
            border_radius=12
        )

        pygame.draw.rect(
            self.screen,
            self.cyan,
            popup,
            2,
            border_radius=12
        )

        title = self.medium_font.render(
            "EDIT PLAYER ID",
            True,
            self.cyan
        )

        self.screen.blit(
            title,
            (
                popup.centerx -
                title.get_width() // 2,
                160
            )
        )

        label = self.small_font.render(
            "NEW PLAYER ID",
            True,
            self.gray
        )

        self.screen.blit(
            label,
            (200, 260)
        )

        pygame.draw.rect(
            self.screen,
            (8, 20, 35),
            self.username_box,
            border_radius=7
        )

        pygame.draw.rect(
            self.screen,
            self.cyan_dark,
            self.username_box,
            2,
            border_radius=7
        )

        text_surface = self.small_font.render(
            self.edit_text,
            True,
            self.white
        )

        self.screen.blit(
            text_surface,
            (
                self.username_box.x + 12,
                self.username_box.y + 15
            )
        )

        if self.cursor_visible:

            cursor_x = (
                self.username_box.x
                + 12
                + text_surface.get_width()
            )

            pygame.draw.line(
                self.screen,
                self.cyan,
                (
                    cursor_x,
                    self.username_box.y + 10
                ),
                (
                    cursor_x,
                    self.username_box.y + 37
                ),
                2
            )

        self.draw_button(
            self.save_edit,
            "SAVE",
            self.green,
            (20, 100, 70)
        )

        self.draw_button(
            self.cancel_edit,
            "CANCEL",
            self.gray,
            (45, 55, 70)
        )

    def draw_delete_popup(self):

        overlay = pygame.Surface(
            (self.w, self.h),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 180)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        popup = pygame.Rect(
            150,
            160,
            500,
            280
        )

        pygame.draw.rect(
            self.screen,
            (8, 15, 28),
            popup,
            border_radius=12
        )

        pygame.draw.rect(
            self.screen,
            self.red,
            popup,
            2,
            border_radius=12
        )

        pygame.draw.circle(
            self.screen,
            self.red,
            (400, 205),
            20,
            2
        )

        warning = self.medium_font.render(
            "!",
            True,
            self.red
        )

        self.screen.blit(
            warning,
            (
                400 -
                warning.get_width() // 2,
                205 -
                warning.get_height() // 2
            )
        )

        title = self.medium_font.render(
            "DELETE PLAYER ACCOUNT?",
            True,
            self.white
        )

        self.screen.blit(
            title,
            (
                popup.centerx -
                title.get_width() // 2,
                235
            )
        )

        line1 = self.small_font.render(
            "This action cannot be undone.",
            True,
            self.gray
        )

        line2 = self.small_font.render(
            "Are you sure you want to delete this account?",
            True,
            self.gray
        )

        self.screen.blit(
            line1,
            (
                popup.centerx -
                line1.get_width() // 2,
                267
            )
        )

        self.screen.blit(
            line2,
            (
                popup.centerx -
                line2.get_width() // 2,
                289
            )
        )

        self.draw_button(
            self.confirm_yes,
            "DELETE",
            self.red,
            self.red_dark
        )

        self.draw_button(
            self.confirm_no,
            "CANCEL",
            self.gray,
            (45, 55, 70)
        )

    def draw_message(self):

        if self.message_type == "success":
            color = self.green

        elif self.message_type == "error":
            color = self.red

        else:
            color = self.cyan

        box = pygame.Rect(
            220,
            65,
            360,
            32
        )

        pygame.draw.rect(
            self.screen,
            (8, 18, 30),
            box,
            border_radius=6
        )

        pygame.draw.rect(
            self.screen,
            color,
            box,
            1,
            border_radius=6
        )

        text = self.small_font.render(
            self.message,
            True,
            color
        )

        self.screen.blit(
            text,
            (
                box.centerx -
                text.get_width() // 2,
                box.centery -
                text.get_height() // 2
            )
        )