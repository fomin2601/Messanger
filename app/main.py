from fastapi import FastAPI

from app.internal.utils import create_db_and_tables, engine
from .routers import rooms, users, auth

app = FastAPI()

app.include_router(rooms.router)
app.include_router(users.router)
app.include_router(auth.router)

@app.on_event('startup')
def on_startup():
    create_db_and_tables(engine)



