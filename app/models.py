import peewee

from app.database import db


class User(peewee.Model):
    name = peewee.CharField(index=True)
    surname = peewee.CharField(index=True)
    username = peewee.CharField(unique=True, index=True)
    hashed_password = peewee.CharField(unique=True, index=True)
    is_active = peewee.BooleanField(default=True)

    class Meta:
        database = db


class Receipt(peewee.Model):
    title = peewee.CharField(unique=True)
    ingredients = peewee.CharField()
    description = peewee.CharField()
    is_public = peewee.BooleanField(default=False)
    owner = peewee.ForeignKeyField(User, backref="receipts")

    class Meta:
        database = db
