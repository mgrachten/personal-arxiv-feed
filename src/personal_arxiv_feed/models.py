import datetime
from sqlmodel import Field, SQLModel


class Interest(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str = Field(index=True)


class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)


class Article(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    entry_id: str = Field(unique=True)
    title: str
    authors: str
    abstract: str
    published: datetime.date
    relevance_reason: str | None = None
