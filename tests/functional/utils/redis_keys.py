from pydantic import BaseModel, Field


class Pagination(BaseModel):
    page: str = Field(default="1")
    page_size: str = Field(default="10")


class Films(Pagination):
    order_by: str = Field(default="None")
    search: str = Field(default="None")

    def __str__(self):
        return (
            f"{self.order_by}_{self.search}_{self.page}_{self.page_size}_films"
        )


class Persons(Pagination):
    name: str = Field(default="None")

    def __str__(self):
        return f"{self.name}_{self.page}_{self.page_size}_persons"


class Genres(Pagination):
    filtr: str = Field(default="None")

    def __str__(self):
        return f"{self.filtr}_genres"
