from fastapi import FastAPI

from app.internal.utils import create_db_and_tables, engine
from .routers import rooms, users, auth
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware

middleware = [Middleware(CORSMiddleware, allow_origins=True)]

app = FastAPI(middleware=middleware)

app.include_router(rooms.router)
app.include_router(users.router)
app.include_router(auth.router)



@app.on_event('startup')
def on_startup():
    create_db_and_tables(engine)



