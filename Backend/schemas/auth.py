from typing import Optional

from pydantic import BaseModel


class BackendUserModel(BaseModel):
    user_name: str
    allowed_scopes: list[str]
    has_write_permission: bool
    has_read_permission: bool
    disabled: bool

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
