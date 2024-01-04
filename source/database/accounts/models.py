# External
from peewee import PrimaryKeyField, CharField, ForeignKeyField, IntegerField, TextField, DateField

# Internal
from database.accounts.context import BaseModel


class Role(BaseModel):
    role_id = PrimaryKeyField()

    role_name = CharField()

    class Meta:
        db_table = "Roles"

class User(BaseModel):
    user_id = PrimaryKeyField()

    username = CharField(unique=True)
    password = CharField()
    name = CharField()

    role = ForeignKeyField(Role, backref="Users")

    class Meta:
        db_table = "Users"
