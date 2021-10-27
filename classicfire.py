import random

from src.functions import get_players
from src.gamemodes import GameMode, game_mode
from src.events import EventListener
from src.cats import Wolf
from src.messages import messages

messages.messages["_gamemodes"]["classicfire"] = "classicfire"

@game_mode("classicfire", minp=4, maxp=24, likelihood=10)
class ClassicfireMode(GameMode):
    """ <@misha> and "more balanced than maelstrom" isn't too difficult a bar to clear"""

    def __init__(self, arg=""):
        super().__init__(arg)
        self.ROLE_GUIDE = {
            4: ["wolf", "detective", "crazed shaman"],
            6: ["cursed villager"],
            7: ["cultist", "shaman"],
            8: ["harlot", "traitor", "-cultist"],
            9: ["crazed shaman(2)"],
            10: ["wolf cub"],
            11: ["matchmaker"],
            12: ["-wolf", "werecrow"],
            13: ["detective"],
            14: ["tough wolf"],
            15: ["hunter"],
            16: ["monster"],
            18: ["bodyguard"],
            20: ["sorcerer", "augur", "cursed villager(2)"],
            21: ["wolf", "wolf(2)", "gunner/sharpshooter"],
            23: ["amnesiac", "mayor"],
            24: ["hag"],
        }

        self.EVENTS = {
            "begin_night": EventListener(self.on_begin_night),
            "num_totems": EventListener(self.on_num_totems),
            "role_attribution_end": EventListener(self.on_role_attribution_end)
        }

    def on_begin_night(self, evt, var):
        from src.roles.crazedshaman import LASTGIVEN
        LASTGIVEN.clear()

    def on_num_totems(self, evt, var, player, role):
        if role == "crazed shaman":
            evt.data["num"] = len(get_players()) - 1

    def on_role_attribution_end(self, evt, var, main_roles, all_roles):
        target = random.choice(get_players(var, Wolf, mainroles=main_roles))
        evt.data["actions"].append(("add", target, "shaman"))
        evt.data["actions"].append(("add", target, "detective"))
