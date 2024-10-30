from typing import Annotated
from sqlmodel import create_engine, SQLModel, Session
from fastapi import Depends



def create_db_engine():
    postgresql_url = f"postgresql://postgres:AsDf1235!@localhost:5432/postgres"

    connect_args = {}
    engine = create_engine(postgresql_url, connect_args=connect_args)

    return engine

engine = create_db_engine()

def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
