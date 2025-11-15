from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.chat import Chat, Message

from app.services.ollama_client import ollama_chat
from app.services.video_analyzer import extract_frames_bytes
from app.utils.files import read_upload_file
from app.services.stats import increment_requests

router = APIRouter(prefix="/v1/video", tags=["Video"])


@router.post("/analyze")
async def analyze_video(
    prompt: str,
    file: UploadFile = File(...),
    step: int = 30,
    stream: bool = False,
    thinking: str | None = None,
    chat_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    file_bytes, file_b64 = await read_upload_file(file)

    if chat_id:
        chat = await db.get(Chat, chat_id)
        if not chat or chat.user_id != user.id:
            raise HTTPException(404, "Chat not found")
    else:
        chat = Chat(user_id=user.id, title=prompt[:80])
        db.add(chat)
        await db.flush()

    frames_b64 = await extract_frames_bytes(file_bytes, step)
    if not frames_b64:
        raise HTTPException(400, "Cannot decode video")

    thumb_b64 = frames_b64[0]

    user_msg = Message(
        chat_id=chat.id,
        role="user",
        type="video",
        content=prompt,
        video_full=file_b64,
        image_thumb=thumb_b64,
    )
    db.add(user_msg)
    await db.commit()

    system_prompt = (
        "Это видео разбитое по кадрам. Выполни требование пользователя.\n"
        f"{prompt}"
    )

    if stream:
        gen = await ollama_chat(
            db=db,
            chat_id=str(chat.id),
            model="qwen2.5vl",
            prompt=system_prompt,
            images_b64=frames_b64,
            thinking=thinking,
            stream=True,
        )

        async def generator():
            async for chunk in gen:
                msg = chunk.get("message", {})
                if "content" in msg:
                    yield msg["content"]

        return StreamingResponse(generator(), media_type="text/plain")

    text, tokens = await ollama_chat(
        db=db,
        chat_id=str(chat.id),
        model="qwen2.5vl",
        prompt=system_prompt,
        images_b64=frames_b64,
        thinking=thinking,
        stream=False,
    )

    assistant_msg = Message(
        chat_id=chat.id,
        role="assistant",
        type="text",
        content=text,
        tokens_used=tokens,
    )
    db.add(assistant_msg)
    await db.commit()

    await increment_requests(db, user.id, tokens_used=tokens)

    return {
        "chat_id": str(chat.id),
        "response": text,
        "tokens_used": tokens,
    }
