from pydantic import BaseModel


class Product(BaseModel):
    sl: int | None = None
    url: str | None = None
    image: str | None = None
    name: str | None = None
    price: str | None = None
    