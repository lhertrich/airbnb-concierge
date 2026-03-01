from pydantic import BaseModel

class Booking(BaseModel):
    name: str
    check_in: str
    check_out: str
    num_guests: int
    animals: bool