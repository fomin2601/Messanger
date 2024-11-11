from fastapi import APIRouter, Depends
from app.internal.utils import JWTBearer

router = APIRouter(
    prefix='/users',
    tags=['users'],
    dependencies=[Depends(JWTBearer())]
)


@router.get('/')
async def get_user_rooms():
    pass
