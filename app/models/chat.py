import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )

    messages = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chats.id"))
    role: Mapped[str] = mapped_column(String(32))
    type: Mapped[str] = mapped_column(String(32), default="text")
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_full: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_thumb: Mapped[str | None] = mapped_column(Text, nullable=True)
    video_full: Mapped[str | None] = mapped_column(Text, nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )

    chat = relationship("Chat", back_populates="messages")
