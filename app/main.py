from fastapi import FastAPI

from app.internal.utils import create_db_and_tables, engine, predefine_tables
from .routers import rooms, users, auth, messages
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(rooms.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(messages.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event('startup')
def on_startup():
    tables_to_predefine = create_db_and_tables(engine)
    predefine_tables(engine, tables_to_predefine)

