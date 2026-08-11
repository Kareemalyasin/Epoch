"""Article-related enums and Pydantic models."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class Section(str, Enum):
    new_models = "new_models"
    open_source = "open_source"
    ai_tools = "ai_tools"
    claude_ecosystem = "claude_ecosystem"


class Article(BaseModel):
    """An article as stored in the Supabase "articles" table."""

    id: UUID
    title: str
    source_url: str
    source_name: str
    section: Section
    hook: str
    summary_paragraph: str | None
    key_points: list[str]
    image_url: str | None
    published_at: datetime | None
    scraped_at: datetime
    created_at: datetime


class ArticleCreate(BaseModel):
    """Fields required to insert a new article from the pipeline, before the DB assigns id/created_at."""

    title: str
    source_url: str
    source_name: str
    section: Section
    hook: str
    summary_paragraph: str
    key_points: list[str]
    image_url: str | None
    published_at: datetime | None
