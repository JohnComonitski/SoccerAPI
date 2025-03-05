from .lib.postgres import PostgreSQL
from .lib.tm import TM
from .lib.fapi import FAPI
from .lib.fbref import FBRef
from .lib.understat import Understat
from .lib.visualize import Visualize
from .obj.fixture import Fixture
import json
import csv
from typing import Any


class SoccerAPI():
    r"""The main object.

       :ivar db: PostgreSQL database initalization.
       :vartype: PostgreSQL
       :ivar app: app data configuration.

       Example:
           Import the ``soccerapi.soccerapi`` module, then:

           >>> config = {"fapi_host" : "API-FOOTBALL HOST", "fapi_key" : "API-FOOTBALL API KEY"}
           >>> api = soccerapi.soccerapi.SoccerAPI(config)
           >>> haaland = api.db.get("players", "82172")
           >>> stat = haaland.statistic("shots")
        """

    def __init__(self, config: dict={}):
        r"""Create a new instance.

        :param config: This object has a few values and defaults:

            - **debug** (*int*): if set to ``1`` print errors out to the console.
              If set to ``0`` it will not. Defaults to ``0``.
            - **fapi_host** (*str*): the hostname used to make requests to API-Football.
            - **fapi_key** (*str*): API-Football API Key used for authentication.
            - **rate_limit_call_interval** (*int*): rate limit interval in seconds.

              .. admonition:: Purpose
                 :class: purposeAdmonition

                 Help avoiding rate limiting FBRef puts in place that prevents
                 data scraping. Too many requests to FBRef can
                 trigger a 24 hour IP Block.

              .. admonition:: Recommended value
                 :class: recommendedValueAdmonition

                 60

            - **rate_limit_max_calls** (*int*): number of rate limited calls Soccer API
              can make over the time set by ``rate_limit_call_interval``.

              .. admonition:: Purpose
                 :class: purposeAdmonition

                 Helps avoid rate limiting FBRef puts in place that prevents
                 data scraping.

              .. admonition:: Recommended value
                 :class: recommendedValueAdmonition

                 5

            Example:
        
            .. code-block:: python

               config = {
                   'debug': 1,
                   'fapi_host': 'API-FOOTBALL HOST',
                   'fapi_key': 'API KEY',
                   'rate_limit_call_interval': 60,
                   'rate_limit_max_calls': 5,
               }

        :type config: dict
        """
        debug = 0
        if "debug" in config:
            debug = config["debug"]

        app = {
            "debug" : debug,
            "config" : config,
            "fbref" : FBRef(config=config),
            "tm" : TM(),
            "understat" : Understat(),
            "visualize" : Visualize(),
            "fapi" : FAPI(config=config),
        }
        self.db = PostgreSQL(app) 
        self.visualize = Visualize()
        self.app = app

    def import_object(self, path: str) -> Any:
        r"""Import a JSON object.

        :param path: the name of the JSON file.
        :type path: str
        :returns: an object from the database.
        :rtype: Any
        """
        object = None
        with open(path, 'r') as file:
            obj_data = json.load(file)
            obj_type = obj_data["object"]
            obj_id = obj_data["id"]
            
            tables = {
                "player" : "players",
                "team" : "teams",
                "league" : "leagues"
            }
            table_name = None
            if obj_type in tables:
                table_name = tables[obj_type]

            if(table_name):
                object = self.db.get(table_name, obj_id)
                if(object):
                    object.import_data(obj_data)
            else:
                if(obj_type == "fixture"):
                    return Fixture(obj_data["match_data"], self.db)

        return object
    
    def export_csv(self, objects, filename="soccer_api_objects.csv"):
        r"""Export objects to a CSV file.

        :param objects: a list of objects.
        :param filename: the output file name. Defaults to ``soccer_api_objects.csv``.
        :type objects: list[Any]
        :type filename: str
        """
        data = []
        for object in objects:
            data.append({
                "ID" : str(object.id),
                "Table" : object.table,
                "Name" : object.name(),
            })

        with open(filename, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=[ "ID", "Name", "Table" ])
            writer.writeheader() 
            writer.writerows(data)

    def import_csv(self, path) -> list:
        r"""Import data from a CSV file into an object.

        :param path: the input file name.
        :type path: str
        :returns: a list of objects.
        :rtype: list[Any]
        """
        objects: list = []

        with open(path, mode='r') as file:
            reader = list(csv.reader(file))
            reader = reader[1:]

            for row in reader:
                id = row[0]
                table = row[2]
                if(table in [ "teams", "leagues", "players" ]):
                    objects.append(self.db.get(table, str(id)))

        return objects


if __name__ == '__main__':
    pass
