from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# Модель для жанров ИЗМЕНИТСЯ
class Genre(BaseModel):
    id: str
    name: str
    description: str
    created: datetime
    modified: datetime
