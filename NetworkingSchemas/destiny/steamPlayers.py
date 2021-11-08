import datetime

from pydantic import BaseModel


class DestinySteamPlayerCountModel(BaseModel):
    date: datetime.date
    number_of_players: int


class DestinySteamPlayersCountModel(BaseModel):
    entries: list[DestinySteamPlayerCountModel] = []