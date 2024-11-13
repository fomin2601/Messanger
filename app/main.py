from fastapi import FastAPI

from app.internal.utils import create_db_and_tables, engine
from .routers import rooms, users, auth
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.include_router(rooms.router)
app.include_router(users.router)
app.include_router(auth.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event('startup')
def on_startup():
    create_db_and_tables(engine)



