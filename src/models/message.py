from pydantic import BaseModel
from src.models.enums import MessageType

class Message(BaseModel):
    name: str
    message: str
    type: MessageType