from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.chat import Message


async def load_messages(db: AsyncSession, chat_id: str):
    res = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at)
    )
    msgs = res.scalars().all()

    history = []

    for m in msgs:
        if m.content and not m.image_full:
            history.append({
                "role": m.role,
                "content": m.content
            })
            continue

        if m.image_full:
            history.append({
                "role": m.role,
                "content": "",
                "images": [m.image_full]
            })
            continue

    return history
