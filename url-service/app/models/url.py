from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class URL(Base):
    __tablename__ = "urls"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, nullable=False, index=True)
    click_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
