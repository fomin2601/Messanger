from sqlalchemy import select

from app.internal.utils import SessionDep
from app.models.users import UserDB


def get_all_users(session: SessionDep):
    statement = select(UserDB)
    users = session.exec(statement).all()

    return users
