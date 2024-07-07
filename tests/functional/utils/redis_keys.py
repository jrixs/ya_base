from pydantic import BaseModel, Field


class Films(BaseModel):
    order_by: str = Field(default='None')
    search: str = Field(default='None')
    page: str = Field(default='1')
    page_size: str = Field(default='10')

    def __str__(self):
        return f"{self.order_by}_{self.search}_{self.page}_{self.page_size}_films"
