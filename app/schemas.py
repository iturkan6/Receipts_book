from typing import Any

import peewee
from pydantic import BaseModel
from pydantic.utils import GetterDict


class Settings(BaseModel):
    authjwt_secret_key: str = "8febf52869498bb2ca8fe4f7e3a55e626b49ab75c97ad04bdb5617079443103d"


class PeweeGetterDict(GetterDict):
    def get(self, key: Any, default: Any = None):
        res = getattr(self._obj, key, default)
        if isinstance(res, peewee.ModelSelect):
            return list(res)
        return res


class ReceiptBase(BaseModel):
    title: str
    ingredients: str
    description: str


class ReceiptCreate(ReceiptBase):
    pass


class Receipt(ReceiptBase):
    id: int
    owner_id: int
    is_public: bool

    class Config:
        orm_mode = True
        getter_dict = PeweeGetterDict


class UserBase(BaseModel):
    username: str


class UserLogin(UserBase):
    password: str


class UserCreate(UserLogin):
    name: str
    surname: str
    # birthdate: str


class User(UserBase):
    id: int
    is_active: bool
    receipts: list[Receipt] = []

    class Config:
        orm_mode = True
        getter_dict = PeweeGetterDict
