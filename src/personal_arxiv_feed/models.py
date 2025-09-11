from typing import List, Optional
from sqlmodel import Field, SQLModel
import datetime
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str

    class Config:
        env_file = ".env"




class Interest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str = Field(index=True)


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)


class Article(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    entry_id: str = Field(unique=True)
    title: str
    abstract: str
    published: datetime.date
    is_relevant: bool = Field(default=False)
    relevance_reason: Optional[str] = None
