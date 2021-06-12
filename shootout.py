from src.gamemodes import game_mode, GameMode
from src.functions import get_players, get_all_players, get_main_role, change_role
from src.status import get_absent
from src.messages import messages
from src.events import EventListener
import math  # never a bad idea

messages.messages["shootout_win"] = "Game over! The remaining shaman removes their bulletproof vest and begins to fashion a totem of alcohol..."
messages.messages["_gamemodes"]["shootout"] = "shootout"

@game_mode("shootout", minp=2, maxp=24, likelihood=10)
class Shootout(GameMode):
    def __init__(self, arg=""):
        super().__init__(arg)
        self.LIMIT_ABSTAIN = True
        self.DAY_TIME_LIMIT = 45
        self.DAY_TIME_WARN = 30
        self.SHORT_DAY_LIMIT = 45
        self.SHORT_DAY_WARN = 30
        self.NIGHT_TIME_LIMIT = 45
        self.NIGHT_TIME_WARN = 30

        # 70% chance of hitting, 30% chance of headshot upon hit, 5% chance of explosion
        self.GUN_CHANCES = {
            "gunner": (0.7, 0.25, 0.3),
            "wolf gunner": (0.7, 0.25, 0.3),
            "sharpshooter": (1, 0, 1)
        }

        # gunners get more bullets every night; start them off with 0
        self.SHOTS_MULTIPLIER = {
            "gunner": 0,
            "sharpshooter": 0,
            "wolf gunner": 0
        }

        # for display only; gets overridden in role_attribution and role_attribution_end so
        # that everyone is shaman + gunner
        self.ROLE_GUIDE = {
            2: ["shaman", "gunner"]
        }

        self.EVENTS = {
            "transition_night_begin": EventListener(self.on_transition_night_begin),
            "role_attribution": EventListener(self.on_role_attribution),
            "role_attribution_end": EventListener(self.on_role_attribution_end),
            "num_totems": EventListener(self.on_num_totems),
            "chk_win": EventListener(self.on_chk_win, priority=0),
            "player_win": EventListener(self.on_player_win),
        }

        self.TOTEM_CHANCES = {totem: {} for totem in self.DEFAULT_TOTEM_CHANCES}
        self.set_default_totem_chances()
        for totem, roles in self.TOTEM_CHANCES.items():
            for role in roles:
                self.TOTEM_CHANCES[totem][role] = 0
        self.TOTEM_CHANCES["silence"]["shaman"] = 5
        self.TOTEM_CHANCES["revealing"]["shaman"] = 30
        self.TOTEM_CHANCES["desperation"]["shaman"] = 10
        self.TOTEM_CHANCES["impatience"]["shaman"] = 10
        self.TOTEM_CHANCES["influence"]["shaman"] = 5
        self.TOTEM_CHANCES["narcolepsy"]["shaman"] = 5
        self.TOTEM_CHANCES["luck"]["shaman"] = 15
        self.TOTEM_CHANCES["misdirection"]["shaman"] = 20

        self.original_settings = None

    def on_role_attribution(self, evt, var, chk_win_conditions, villagers):
        # dirty hack incoming; this shuts off validation that our mode has to have wolves
        self.original_settings = var.ORIGINAL_SETTINGS
        var.ORIGINAL_SETTINGS = None
        # add shamans equal to the number of players and ignore ROLE_GUIDE
        evt.data["addroles"]["shaman"] = len(villagers)
        evt.prevent_default = True

    def on_role_attribution_end(self, evt, var, main_roles, all_roles):
        # requirement for dirty hack is over, restore original settings
        var.ORIGINAL_SETTINGS = self.original_settings
        # make everyone a gunner
        for player in get_players("shaman", mainroles=main_roles):
            evt.data["actions"].append(("add", player, "gunner"))

    def on_num_totems(self, evt, var, player, role):
        lpl = len(get_players())
        if role == "shaman":
            if lpl < 4 or (lpl == 4 and var.NIGHT_COUNT > 1):
                evt.data["num"] = 1
            elif 4 <= lpl < 8 or lpl >= 9:
                evt.data["num"] = 2

    def on_transition_night_begin(self, evt, var):
        from src.roles.shaman import LASTGIVEN
        from src.roles.gunner import GUNNERS
        # let shamans give totems out to everyone
        LASTGIVEN.clear()
        # give gunners more bullets
        div = len(get_players()) + 1
        add_bullets = int(max(20 / div, 1))
        for p in GUNNERS:
            GUNNERS[p] += add_bullets

    def on_chk_win(self, evt, var, rolemap, mainroles, lpl, lwolves, lrealwolves):
        evt.stop_processing = True
        alive = len(get_players())
        if lpl == 0 and alive > 0:
            # don't stop game if there are alive but injured people
            # (lpl excludes absent players)
            evt.data["winner"] = None
        elif alive == 1:
            evt.data["winner"] = "no_team_wins"
            evt.data["message"] = messages["shootout_win"]

    def on_player_win(self, evt, var, player, main_role, all_roles, winner, team_win, survived):
        if main_role == "shaman" and survived:
            evt.data["individual_win"] = True
