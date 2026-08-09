from pydantic import BaseModel


class Address(BaseModel):
    street: str | None = None
    city: str | None = None
    postcode: str | None = None
