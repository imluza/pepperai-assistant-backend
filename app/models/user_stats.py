from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from sqlalchemy.orm import relationship

class UserStats(Base):
    __tablename__ = "user_stats"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    requests_count = Column(Integer, default=0, nullable=False)
    chats_count = Column(Integer, default=0, nullable=False)
    tokens_used = Column(Integer, default=0, nullable=False)

    hourly_requests = Column(Integer, default=0, nullable=False)
    daily_requests = Column(Integer, default=0, nullable=False)
    weekly_requests = Column(Integer, default=0, nullable=False)
    monthly_requests = Column(Integer, default=0, nullable=False)

    hourly_tokens = Column(Integer, default=0, nullable=False)
    daily_tokens = Column(Integer, default=0, nullable=False)
    weekly_tokens = Column(Integer, default=0, nullable=False)
    monthly_tokens = Column(Integer, default=0, nullable=False)

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="stats")
