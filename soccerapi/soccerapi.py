from .lib.postgres import PostgreSQL
from .lib.tm import TM
from .lib.fapi import FAPI
from .lib.fbref import FBRef
from .lib.understat import Understat
from .lib.visualize import Visualize
from .obj.fixture import Fixture
import json
import csv


class SoccerAPI():
    """Docstring for class Foo.

       :ivar db: Database initalization.
       :ivar visualize: test
       :ivar app: App data.
    """

    def __init__(self, config={}):
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

    def import_object(self, path):
        r"""Import a JSON object.
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
        r"""Export objects to a CSV file."""
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

    def import_csv(self, path):
        r"""Import data from a CSV file into an object."""
        objects = []

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
