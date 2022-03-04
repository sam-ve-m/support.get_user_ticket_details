# Standards

# Third part
from pydantic import BaseModel, validator


class Filter(BaseModel):
    id: str

    @validator('id')
    def is_numeric(id):
        if id.isnumeric():
            id = int(id)
            return id
        raise ValueError('Invalid type id')
