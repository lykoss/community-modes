from src.gamemodes import game_mode, GameMode
from src.functions import get_players, get_main_role, change_role
from src.messages import messages
from src.events import EventListener
import math

messages.messages["totemroyale_win"] = "Game over! Standing among their dead companions, the remaining crazed shaman learns a valuable lesson: the real totems were the friends we made along the way."
messages.messages["_gamemodes"]["totemfire"] = "totemfire"
messages.messages["_gamemodes"]["toteminferno"] = "toteminferno"
messages.messages["_gamemodes"]["totemroyale"] = "totemroyale"

class TotemMode(GameMode):
    def __init__(self, arg=""):
        super().__init__(arg)
        self.LIMIT_ABSTAIN = False
        self.DEFAULT_ROLE = "crazed shaman"
        self.EVENTS = {
            "transition_night_begin": EventListener(self.on_transition_night_begin),
            "num_totems": EventListener(self.on_num_totems)
        }
        self.ROLE_GUIDE = {
            4: ["wolf shaman"],
            6: ["jester", "gunner"],
            8: ["shaman", "minion"],
            10: ["wolf shaman(2)"],
            14: ["wolf shaman(3)", "jester(2)"],
            16: ["gunner(2)"]
        }

    def on_num_totems(self, evt, var, player, role):
        if role == "crazed shaman":
            evt.data["num"] = round(math.sqrt(len(get_players())))

    def on_transition_night_begin(self, evt, var):
        from src.roles.crazedshaman import LASTGIVEN
        LASTGIVEN.clear()

@game_mode("totemfire", minp=4, maxp=24, likelihood=10)
class PlebTotemMode(TotemMode):
    def __init__(self, arg=""):
        super().__init__(arg)
        for totem in ("narcolepsy", "impatience", "pacifism"):
            self.TOTEM_CHANCES[totem]["crazed shaman"] = 0

@game_mode("toteminferno", minp=4, maxp=24, likelihood=10)
class PlebTotemMode(TotemMode):
    def __init__(self, arg=""):
        super().__init__(arg)
        self.TOTEM_CHANCES["luck"]["crazed shaman"] = 30
        self.TOTEM_CHANCES["death"]["crazed shaman"] = 40
        self.TOTEM_CHANCES["retribution"]["crazed shaman"] = 20
        self.TOTEM_CHANCES["exchange"]["crazed shaman"] = 20
        self.TOTEM_CHANCES["lycanthropy"]["crazed shaman"] = 60
        self.TOTEM_CHANCES["misdirection"]["crazed shaman"] = 0

@game_mode("totemroyale", minp=2, maxp=24, likelihood=10)
class TotemRoyaleMode(TotemMode):
    def __init__(self, arg=""):
        super().__init__(arg)
        # reset default to villager so !roles doesn't get confused, we ignore ROLE_GUIDE anyway
        self.DEFAULT_ROLE = "villager"
        self.STATS_TYPE = "disabled"
        self.ROLE_GUIDE = {
            2: ["crazed shaman"]
        }

        self.EVENTS = {
            "chk_win": EventListener(self.on_chk_win, priority=0),
            "role_attribution": EventListener(self.on_role_attribution),
            "role_attribution_end": EventListener(self.on_role_attribution_end),
        }

        self.TOTEM_CHANCES = {
            "death"         : {"crazed shaman": 10},
            "protection"    : {"crazed shaman": 0},
            "silence"       : {"crazed shaman": 0},
            "revealing"     : {"crazed shaman": 25},
            "desperation"   : {"crazed shaman": 20},
            "impatience"    : {"crazed shaman": 0},
            "pacifism"      : {"crazed shaman": 0},
            "influence"     : {"crazed shaman": 40},
            "narcolepsy"    : {"crazed shaman": 0},
            "exchange"      : {"crazed shaman": 0},
            "lycanthropy"   : {"crazed shaman": 0},
            "luck"          : {"crazed shaman": 5},
            "pestilence"    : {"crazed shaman": 0},
            "retribution"   : {"crazed shaman": 0},
            "misdirection"  : {"crazed shaman": 0},
            "deceit"        : {"crazed shaman": 0},
        }
        self.set_default_totem_chances()

        self.original_settings = None

    def on_role_attribution(self, evt, var, chk_win_conditions, villagers):
        # dirty hack incoming; this shuts off validation that our mode has to have wolves
        self.original_settings = var.ORIGINAL_SETTINGS
        var.ORIGINAL_SETTINGS = None
        # add crazed shamans equal to the number of players and ignore ROLE_GUIDE
        evt.data["addroles"]["crazed shaman"] = len(villagers)
        evt.prevent_default = True

    def on_role_attribution_end(self, evt, var, main_roles, all_roles):
        # requirement for dirty hack is over, restore original settings
        var.ORIGINAL_SETTINGS = self.original_settings

    def on_chk_win(self, evt, var, rolemap, mainroles, lpl, lwolves, lrealwolves):
        evt.stop_processing = True
        if len(get_players()) == 1:
            evt.data["winner"] = "no_team_wins"
            evt.data["message"] = messages["totemroyale_win"]