# Internal
from database.accounts.models import Role, User


def roles():
    return Role.select()

def users():
    return User.select()