from sqlalchemy import select

from app.internal.utils import SessionDep
from app.models.users import UserDB


def get_all_users(session: SessionDep):
    statement = select(UserDB)
    users = [user[0] for user in session.exec(statement).all() if user is not None]

    return users
