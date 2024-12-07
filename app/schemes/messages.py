from pydantic import BaseModel
from app.models.messages import Message
from .users import UserPublicScheme


class MessageScheme(BaseModel):
    message: Message
    sender: UserPublicScheme


class RSAScheme(BaseModel):
    public_rsa_key: str


class AESScheme(BaseModel):
    aes_key: str
