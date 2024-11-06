from fastapi import APIRouter

router = APIRouter(
    prefix='/users',
    tags=['users']
)

@router.get('/', tags=['users'])
async def get_user_rooms():
    pass