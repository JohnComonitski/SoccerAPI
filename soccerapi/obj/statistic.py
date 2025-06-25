from ..lib.utils import key_to_name


class Statistic:
    r"""Statistics object.

      :ivar key: internal name for a Statistic object.
      :vartype key: str
      :ivar value: numeric value of the Statistic object.
      :vartype value: float
      :ivar percentile: percentile representation of a Statistic's value.
      :vartype percentile: float
      :ivar name: display name for a Statistic object.
      :vartype name: str
    """
    def __init__(self, stat_data: dict):
        r"""Create a new instance.

        :param stat_data: The data to be populated into a Statistic object.
        :type stat_data: dict
        """
        self.key = stat_data["key"]
        self.percentile = None
        name = key_to_name(stat_data["key"])
        if(name):
            self.name = name
        else:
            self.name = stat_data["key"]
            self.value = 0
            return
        
        val = ""
        if str(stat_data["value"]) == 'None':
            val = "0"
        else:
            val = str(stat_data["value"])

        if "," in val:
            val = val.replace(",", "")
        if "%" in val:
            self.value = float(float(val[:-1])/100)
        elif( val[0] == "+"):
            self.value = float(val[1:])
        elif(val[0] == "-" ):
            self.value = -1 * float(val[1:])
        else:
            self.value = float(val)

        if("percentile" in stat_data):
            if(stat_data["percentile"]):
                self.percentile = float(stat_data["percentile"])
            else:
                self.percentile = 0
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return str(self.value)
    
    def to_json(self) -> dict:
        r"""Get a JSON representation of the Statistic object.

        :rtype: dict
        """
        return {
            "object" : "statistic",
            "key" : self.key,
            "name" : self.name,
            "value" : self.value,
            "percentile" : self.percentile
        }
