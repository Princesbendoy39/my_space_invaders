import pygame

from managers.game_manager import GameManager
from managers.auth_manager import AuthManager
from managers.home_manager import HomeManager
from managers.profile_manager import ProfileManager
from managers.leaderboard_manager import LeaderboardManager
from managers.settings_manager import SettingsManager


pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pygame.display.set_caption(
    "Space Invaders by Bendoy, Princes R."
)

auth = AuthManager(
    screen,
    SCREEN_WIDTH,
    SCREEN_HEIGHT
)

home = HomeManager(
    screen,
    SCREEN_WIDTH,
    SCREEN_HEIGHT
)

game = GameManager(
    screen,
    SCREEN_WIDTH,
    SCREEN_HEIGHT
)

profile = ProfileManager(
    screen,
    SCREEN_WIDTH,
    SCREEN_HEIGHT
)

leaderboard = LeaderboardManager(
    screen,
    SCREEN_WIDTH,
    SCREEN_HEIGHT
)

settings = SettingsManager(
    screen,
    SCREEN_WIDTH,
    SCREEN_HEIGHT
)

clock = pygame.time.Clock()

running = True
screen_mode = "auth"
player = None


while running:

    events = pygame.event.get()

    for event in events:

        if event.type == pygame.QUIT:
            running = False

    if screen_mode == "auth":

        result = auth.update(events)

        if isinstance(result, dict):

            player = result

            game.set_player(player)
            profile.set_player(player)
            leaderboard.set_player(player)

            screen_mode = "home"

    elif screen_mode == "home":

        result = home.update(events)

        home.draw(player)

        if result == "game":

            game.set_player(player)

            profile.set_current_score(0)

            screen_mode = "game"

        elif result == "profile":

            profile.set_player(player)

            screen_mode = "profile"

        elif result == "leaderboard":

            leaderboard.set_player(player)

            screen_mode = "leaderboard"

        elif result == "settings":

            settings.return_to_game = False

            screen_mode = "settings"

        elif result == "logout":

            player = None

            profile.clear_player()
            leaderboard.set_player(None)

            auth.clear_fields()

            screen_mode = "auth"

    elif screen_mode == "settings":

        result = settings.update(events)

        settings.draw()

        if result == "home":

            screen_mode = "home"

        elif result == "game":

            screen_mode = "game"

    elif screen_mode == "profile":

        result = profile.update(events)

        if hasattr(profile, "draw"):
            profile.draw()

        if result in ("home", "menu"):

            screen_mode = "home"

        elif result == "login":

            player = None

            profile.clear_player()
            leaderboard.set_player(None)

            auth.clear_fields()

            screen_mode = "auth"

    elif screen_mode == "game":

        result = game.update(events)

        if hasattr(game, "score"):

            profile.set_current_score(
                game.score
            )

        elif hasattr(game, "current_score"):

            profile.set_current_score(
                game.current_score
            )

        elif hasattr(game, "player_score"):

            profile.set_current_score(
                game.player_score
            )

        if result == "home":

            screen_mode = "home"

        elif result == "leaderboard":

            leaderboard.set_player(player)

            screen_mode = "leaderboard"

        elif result == "settings":

            settings.open_from_game()

            screen_mode = "settings"

    elif screen_mode == "leaderboard":

        result = leaderboard.update(events)

        if hasattr(leaderboard, "draw"):
            leaderboard.draw()

        if result == "home":

            screen_mode = "home"

    pygame.display.update()

    clock.tick(60)


pygame.quit()