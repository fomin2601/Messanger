from typing import Annotated
from fastapi import FastAPI, Depends
from sqlmodel import Session

from .models.utils import create_db_engine, create_db_and_tables, get_session
from .routers import rooms, users

engine = create_db_engine()

app = FastAPI()
app.include_router(rooms.router)
#app.include_router(users.router)

@app.on_event('startup')
def on_startup():
    create_db_and_tables(engine)

