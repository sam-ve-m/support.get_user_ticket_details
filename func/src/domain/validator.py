from pydantic import BaseModel, validator


class TicketDetails(BaseModel):
    id: str

    @validator('id')
    def is_numeric(cls, id):
        if id.isnumeric():
            id = int(id)
            return id
        raise ValueError('Invalid type id')
