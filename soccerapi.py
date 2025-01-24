from SoccerAPI.lib.postgres import PostgreSQL
from SoccerAPI.lib.tm import TM
from SoccerAPI.lib.fapi import FAPI
from SoccerAPI.lib.fbref import FBRef
from SoccerAPI.lib.understat import Understat
from SoccerAPI.lib.visualize import Visualize
from SoccerAPI.obj.fixture import Fixture
import json

class SoccerAPI():
    def __init__(self, debug=0):
        app = {
            "fbref" : FBRef(),
            "tm" : TM(),
            "understat" : Understat(),
            "visualize" : Visualize(),
            "fapi" : FAPI(),
            "debug" : debug
        }
        self.db = PostgreSQL(app) 
        self.visualize = Visualize()

    def import_object(self, path):
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
                object.import_data(obj_data)
            else:
                if(obj_type == "fixture"):
                    return Fixture(obj_data["match_data"], self.db)

        return object