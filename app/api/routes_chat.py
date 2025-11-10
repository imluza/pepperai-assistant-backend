from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.chat import Chat, Message
from app.services.ollama_client import stream_chat
from app.schemas.chat import ChatRequest
import json

router = APIRouter(prefix="/v1/chat", tags=["Chat"])

@router.post(
    "/completions",
    response_class=StreamingResponse,
    response_description="Возвращает потоковый ответ от модели (text/plain). В заголовке X-Chat-Id - айди чата для юзера",
    status_code=status.HTTP_200_OK,
)
async def chat_completions(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Пример запроса
    ```json
    {
      "prompt": "Сколько айкью у тимура",
      "chat_id": "timur-lox-hahaha-7904-447-5865",
      "thinking": "medium"
    }
    ```
    Если не должна думать -  не отправляй thkinking. Если должна - степень: low, medium, high.\n
    При отправке без chat_id - создается чат. Для ведения контекста - отправляй последующий, который получаешь в X-Chat-Id
    """
    if payload.chat_id:
        chat = await db.get(Chat, payload.chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
    else:
        chat = Chat(user_id=user.id, title=payload.prompt[:80])
        db.add(chat)
        await db.flush()

    db.add(Message(chat_id=chat.id, role="user", content=payload.prompt))
    await db.commit()

    res = await db.execute(select(Message).where(Message.chat_id == chat.id).order_by(Message.created_at))
    messages = [{"role": m.role, "content": m.content} for m in res.scalars().all()]

    async def event_stream():
        collected = []
        in_thinking = False

        async for chunk in stream_chat("gpt-oss:20b", messages, payload.thinking):
            try:
                data = json.loads(chunk)
            except json.JSONDecodeError:
                continue

            message = data.get("message", {})
            thinking = message.get("thinking")
            content = message.get("content")

            if thinking and not in_thinking:
                in_thinking = True
                yield "\n--- Thinking ---\n"
            if thinking:
                yield thinking
            elif content:
                if in_thinking:
                    yield "\n\n--- Answer ---\n"
                    in_thinking = False
                yield content

            if data.get("done"):
                break

        full_reply = "".join(collected)
        db.add(Message(chat_id=chat.id, role="assistant", content=full_reply))
        await db.commit()

    return StreamingResponse(
        event_stream(),
        media_type="text/plain",
        headers={"X-Chat-Id": str(chat.id)},
    )
