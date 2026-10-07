from sqlalchemy import Column, Integer, String
from pydantic import BaseModel, ConfigDict

from app.core.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    age_group = Column(String, nullable=False)
    cover_url = Column(String, nullable=True)


class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    age_group: str
    cover_url: str | None = None
