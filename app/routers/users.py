from fastapi import APIRouter
from app.controllers import users
from app.models.utils import SessionDep
from app.models.users import User


router = APIRouter(
    prefix='/users',
    tags=['users']
)

@router.get('/', tags=['users'])
async def get_user_rooms():
    pass