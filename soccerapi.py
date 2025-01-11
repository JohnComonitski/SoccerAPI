from SoccerAPI.lib.postgres import PostgreSQL
from SoccerAPI.lib.tm import TM
from SoccerAPI.lib.fapi import FAPI
from SoccerAPI.lib.fbref import FBRef
from SoccerAPI.lib.understat import Understat
from SoccerAPI.lib.visualize import Visualize

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