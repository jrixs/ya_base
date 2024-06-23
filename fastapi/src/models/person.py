from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# Модель для людей (актеров, сценаристов, режиссеров) ИЗМЕНИТСЯ
class Person(BaseModel):
    id: str
    full_name: str
    gender: str
    created: datetime
    modified: datetime
