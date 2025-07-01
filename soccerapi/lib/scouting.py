from typing import Any, Optional
from ..obj.player import Player

class Scouting:
    r"""The Scouting object. This class is provides a series of methods which
    can be used as tools for scouting players.
    """
    def __init__(self):
        pass

    def same_position(self, player: Player, players_to_scount: Player) -> bool:
        r"""Compares two Player objects and returns true if they play the same position.

        :param player: the player you are comparing against.
        :type player: Player
        :param players_to_scount: the player you are scouting.
        :type players_to_scount: Player
        :returns: returns True if the Players play the same position, otherwise False.
        :rtype: bool
        """
        positions_to_compare = players_to_scount.positions()
        for position in player.positions():
            if(position in positions_to_compare):
                return True
        return False

    def cheaper_better_younger(self, player: Player, players_to_scout: list[Player], stat_key: str) -> dict:
        r"""Using a Player object, a list of Players to scout and a statistic this method performs a 'Cheaper, Younger, Better' styled scouting analysis across that list of Players to scout.

        :param player: the player you are comparing against.
        :type player: Player
        :param players_to_scout: the players you are scouting.
        :type players_to_scout: list[Player]
        :param stat_key: the statistic name you are using to compare these players.
        :type stat_key: str
        :returns: returns a dictionary containing the results from the cheaper, younger, better analysis.
        :rtype: dict
        """

        stat = player.statistic(stat_key).value
        age = player.profile()["age"]
        mv = player.market_value()

        cheaper_better_younger = []
        cheaper = []
        younger = []
        better = []
        for scouted_player in players_to_scout:
            scouted_player_stat = scouted_player.statistic(stat_key).value
            scouted_player_age = scouted_player.profile()["age"]
            scouted_player_mv = scouted_player.market_value()

            res = {
                "cheaper" : 0,
                "better" : 0,
                "younger" : 0
            }

            if( scouted_player_stat >= stat ):
                res["better"] = 1
                better.append(scouted_player)

            if( scouted_player_age <= age ):
                res["younger"] = 1
                younger.append(scouted_player)

            if( scouted_player_mv <= mv ):
                res["cheaper"] = 1
                cheaper.append(scouted_player)

            if( res["cheaper"] and res["younger"] and res["better"]):
                cheaper_better_younger.append(scouted_player)

        return {
            "Cheaper" : cheaper,
            "Younger" : younger,
            "Better" : better,
            "cheaper_better_younger" : cheaper_better_younger
        }
    
    def top_10_by_stat(self, players: list[Player], stat: str, year: Optional[str] = None) -> list[Player]:
        r"""Scout a list of players and return (in order) the top 10 players for a given stat.

        :param player: the players you are scouting.
        :type player: Player
        :param stat: the statistic name you are using to compare these players.
        :type stat: str
        :param year: the year the statistic is from. If this parameter is not set, get
          the current year.
        :type year: Optional[str]
        :returns: returns a list of the top 10 players by a given stat
        :rtype: list[Player]
        """

        stats_list = [ { stat: player.statistic(stat, year), "player" : player } for player in players ]
        stats_list.sort(key=lambda x: x[stat].value)
        stats_list.reverse()

        return stats_list[0:10]
