import datetime
from typing import Optional

from pydantic import BaseModel


class DestinyNameModel(BaseModel):
    name: str


class DestinyStatModel(BaseModel):
    value: int | float


class DestinyCharacterModel(BaseModel):
    character_id: int
    character_class: str
    character_race: str
    character_gender: str


class DestinyCharactersModel(BaseModel):
    characters: list[DestinyCharacterModel] = []


class DestinyTimeModel(BaseModel):
    time_played: int  # in seconds


class DestinyTimeInputModel(BaseModel):
    start_time: datetime.datetime
    end_time: datetime.datetime
    modes: list[int]
    activity_ids: Optional[list[int]]
    character_class: Optional[str] = None


class DestinyLastInputModel(BaseModel):
    activity_ids: [int]  # if this is supplied, mode is ignored
    mode: int
    character_class: Optional[str] = None
