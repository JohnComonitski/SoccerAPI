from ..lib.utils import key_to_name, traverse_dict


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
      :ivar context: dictionary describing the context (year and objects) this statistic was generated from
      :vartype name: dict
    """
    def __init__(self, stat_data: dict):
        r"""Create a new instance.

        :param stat_data: The data to be populated into a Statistic object.
        :type stat_data: dict
        """
        self.key = stat_data["key"]
        self.percentile = None

        self.context = {}
        if("context" in stat_data):
            if "object" in stat_data["context"]:
                self.context["object"] = stat_data["context"]["object"]
            if "player" in stat_data["context"]:
                self.context["player"] = stat_data["context"]["player"]
            if "team" in stat_data["context"]:
                self.context["team"] = stat_data["context"]["team"]
            if "league" in stat_data["context"]:
                self.context["league"] = stat_data["context"]["league"]
            if "year" in stat_data["context"]:
                self.context["year"] = stat_data["context"]["year"]
            if "age" in stat_data["context"]:
                self.context["age"] = stat_data["context"]["age"]

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
    
    def __neg__(self):
        return Statistic(-self.value)

    def __pos__(self):
        return Statistic(+self.value)

    def __abs__(self):
        return Statistic(abs(self.value))

    def __eq__(self, other):
        return self.value == self._unwrap(other)

    def __ne__(self, other):
        return self.value != self._unwrap(other)

    def __lt__(self, other):
        return self.value < self._unwrap(other)

    def __le__(self, other):
        return self.value <= self._unwrap(other)

    def __gt__(self, other):
        return self.value > self._unwrap(other)

    def __ge__(self, other):
        return self.value >= self._unwrap(other)

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __add__(self, other):
        return Statistic({
            "key": self.key,
            "value": self.value + self._unwrap(other),
            "percentile": self.percentile
        })

    def __radd__(self, other):
        return Statistic({
            "key": self.key,
            "value": self._unwrap(other) + self.value,
            "percentile": self.percentile
        })

    def __sub__(self, other):
        return Statistic({
            "key": self.key,
            "value": self.value - self._unwrap(other),
            "percentile": self.percentile
        })

    def __rsub__(self, other):
        return Statistic({
            "key": self.key,
            "value": self._unwrap(other) - self.value,
            "percentile": self.percentile
        })

    def __mul__(self, other):
        return Statistic({
            "key": self.key,
            "value": self.value * self._unwrap(other),
            "percentile": self.percentile
        })

    def __rmul__(self, other):
        return Statistic({
            "key": self.key,
            "value": self._unwrap(other) * self.value,
            "percentile": self.percentile
        })

    def __truediv__(self, other):
        return Statistic({
            "key": self.key,
            "value": self.value / self._unwrap(other),
            "percentile": self.percentile
        })

    def __rtruediv__(self, other):
        return Statistic({
            "key": self.key,
            "value": self._unwrap(other) / self.value,
            "percentile": self.percentile
        })

    def __floordiv__(self, other):
        return Statistic({
            "key": self.key,
            "value": self.value // self._unwrap(other),
            "percentile": self.percentile
        })

    def __rfloordiv__(self, other):
        return Statistic({
            "key": self.key,
            "value": self._unwrap(other) // self.value,
            "percentile": self.percentile
        })

    def __mod__(self, other):
        return Statistic({
            "key": self.key,
            "value": self.value % self._unwrap(other),
            "percentile": self.percentile
        })

    def __rmod__(self, other):
        return Statistic({
            "key": self.key,
            "value": self._unwrap(other) % self.value,
            "percentile": self.percentile
        })

    def __pow__(self, other):
        return Statistic({
            "key": self.key,
            "value": self.value ** self._unwrap(other),
            "percentile": self.percentile
        })

    def __rpow__(self, other):
        return Statistic({
            "key": self.key,
            "value": self._unwrap(other) ** self.value,
            "percentile": self.percentile
        })
    
    def _unwrap(self, other):
        if isinstance(other, Statistic):
            return other.value
        return other
    
    def to_json(self) -> dict:
        r"""Get a JSON representation of the Statistic object.

        :rtype: dict
        """
        flatten_context = {}
        context = self.context
        if "player" in context and context["player"]:
            if "str" in str(type(context["player"])):
                flatten_context["player"] = context["player"]      
            else:   
                flatten_context["player"] = context["player"].id
        if "team" in context and context["team"]:
            if "str" in str(type(context["team"])):
                flatten_context["team"] = context["team"]      
            else:   
                flatten_context["team"] = context["team"].id
        if "league" in context and context["league"]:
            if "str" in str(type(context["league"])):
                flatten_context["league"] = context["league"]      
            else:   
                flatten_context["league"] = context["league"].id
        if "object" in context:
            flatten_context["object"] = context["object"]
        if "year" in context:
            flatten_context["year"] = context["year"]

        return {
            "object" : "statistic",
            "key" : self.key,
            "name" : self.name,
            "value" : self.value,
            "percentile" : self.percentile,
            "context": traverse_dict(flatten_context)
        }
