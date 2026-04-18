from pydantic import BaseModel


class SummarizeRequest(BaseModel):
    article_id: str
    title: str
    content: str


class SummarizeResponse(BaseModel):
    article_id: str
    summary: str
    tags: list[str]
