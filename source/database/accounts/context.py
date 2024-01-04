# External
from peewee import Model, SqliteDatabase

db = SqliteDatabase(r'accounts.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': -1024 * 64})

class BaseModel(Model):
    class Meta:
        database = db