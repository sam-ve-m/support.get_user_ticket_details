# Standards

# Third part
from pydantic import BaseModel, StrictInt


class Filter(BaseModel):
    id: StrictInt
