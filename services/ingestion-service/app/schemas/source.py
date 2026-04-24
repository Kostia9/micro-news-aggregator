from pydantic import BaseModel, HttpUrl


class SourceConfig(BaseModel):
    name: str
    url: HttpUrl
    topics: list[str]
