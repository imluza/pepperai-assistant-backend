import base64
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.chat import Chat, Message
from app.services.ollama_client import ollama_chat
from app.utils.images import make_thumbnail

router = APIRouter(prefix="/v1/image", tags=["Image"])


async def file_to_b64(file: UploadFile) -> str:
    data = await file.read()
    return base64.b64encode(data).decode("utf-8")


@router.post("/analyze")
async def analyze_image(
    prompt: str,
    file: UploadFile = File(...),
    chat_id: UUID | None = None,
    stream: bool = False,
    thinking: str | None = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    img_b64 = await file_to_b64(file)

    thumb_b64 = make_thumbnail(img_b64)

    if chat_id:
        chat = await db.get(Chat, chat_id)
        if not chat or chat.user_id != user.id:
            raise HTTPException(404, "Chat not found")
    else:
        chat = Chat(user_id=user.id, title=prompt[:80])
        db.add(chat)
        await db.flush()

    msg_image = Message(
        chat_id=chat.id,
        role="user",
        type="image",
        content=prompt,
        image_full=img_b64,
        image_thumb=thumb_b64
    )
    db.add(msg_image)

    await db.commit()

    text, tokens = await ollama_chat(
        db=db,
        chat_id=str(chat.id),
        model="qwen2.5vl",
        prompt=prompt,
        images_b64=[img_b64],
        thinking=thinking,
        stream=stream,
    )

    msg_assistant = Message(
        chat_id=chat.id,
        role="assistant",
        type="text",
        content=text,
        tokens_used=tokens
    )
    db.add(msg_assistant)
    await db.commit()

    return {
        "chat_id": str(chat.id),
        "response": text,
        "tokens_used": tokens,
    }
