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
        self.CUSTOM_SETTINGS.limit_abstain = True
        self.CUSTOM_SETTINGS.day_time_limit = 45
        self.CUSTOM_SETTINGS.day_time_warn = 30
        self.CUSTOM_SETTINGS.short_day_time_limit = 45
        self.CUSTOM_SETTINGS.short_day_time_warn = 30
        self.CUSTOM_SETTINGS.night_time_limit = 45
        self.CUSTOM_SETTINGS.night_time_warn = 30

        # 70% chance of hitting, 30% chance of headshot upon hit, 5% chance of explosion
        self.GUN_CHANCES = {
            "gunner": {
                "hit": -1/20, # 75 -> 70
                "headshot": 1/10, # 20 -> 30
            },
            "wolf gunner": {
                "hit": -1/20,
                "headshot": 1/10,
            },
            "sharpshooter": {
                "hit": 1,
                "headshot": 1,
                "explode": -1,
            },
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
            "gun_bullets": EventListener(self.gunner_bullets),
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

    def on_role_attribution(self, evt, var, villagers):
        # add shamans equal to the number of players and ignore ROLE_GUIDE
        evt.data["addroles"]["shaman"] = len(villagers)
        evt.prevent_default = True

    def on_role_attribution_end(self, evt, var, main_roles, all_roles):
        # make everyone a gunner
        for player in get_players(var, "shaman", mainroles=main_roles):
            evt.data["actions"].append(("add", player, "gunner"))

    def gunner_bullets(self, evt, var, player, role):
        evt.data["bullets"] = 0 # gunners get more bullets every night; start them off with 0

    def on_num_totems(self, evt, var, player, role):
        lpl = len(get_players(var))
        if role == "shaman":
            if lpl < 4 or (lpl == 4 and var.night_count > 1):
                evt.data["num"] = 1
            elif 4 <= lpl < 8 or lpl >= 9:
                evt.data["num"] = 2

    def on_transition_night_begin(self, evt, var):
        from src.roles.shaman import LASTGIVEN
        from src.roles.gunner import GUNNERS
        # let shamans give totems out to everyone
        LASTGIVEN.clear()
        # give gunners more bullets
        div = len(get_players(var)) + 1
        add_bullets = int(max(20 / div, 1))
        for p in GUNNERS:
            GUNNERS[p] += add_bullets

    def on_chk_win(self, evt, var, rolemap, mainroles, lpl, lwolves, lrealwolves):
        evt.stop_processing = True
        alive = len(get_players(var))
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
