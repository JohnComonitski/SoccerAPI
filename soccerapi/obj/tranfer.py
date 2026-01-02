class Transfer:
    r"""The Transfer object.

      :ivar player: Player being transfered
      :vartype player: Player
      :ivar to_team: Team player was transfered to
      :vartype to_team: Team
      :ivar from_team: Team player was transfered from
      :vartype to_team: Team
      :ivar type: Type of transfer
      :vartype type: str
      :ivar fee: Transfer fee paid
      :vartype fee: float
      :ivar year: Year the transfer took place
      :vartype year: str
    """
    def __init__(self, team_data, db):
        self.player = None
        self.to_team = None
        self.from_team = None
        self.type = "Transfer"
        self.fee  = 0
        self.year = None