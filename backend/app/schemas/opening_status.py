from pydantic import BaseModel


class OpeningStatus(BaseModel):
    is_open_now: bool | None = None
    raw: str | None = None
