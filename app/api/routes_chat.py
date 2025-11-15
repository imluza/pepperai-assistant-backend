from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import json
import base64

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.chat import Chat, Message
from app.schemas.chat import ChatRequest, ChatCreate, ChatRename
from app.services.ollama_client import ollama_chat
from app.services.stats import increment_requests

router = APIRouter(prefix="/v1/chat", tags=["Chat"])


@router.post("/completions", response_class=StreamingResponse)
async def chat_completions(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    if payload.chat_id:
        chat = await db.get(Chat, payload.chat_id)
        if not chat or chat.user_id != user.id:
            raise HTTPException(404, "Chat not found")
    else:
        chat = Chat(user_id=user.id, title=payload.prompt[:80])
        db.add(chat)
        await db.flush()

    db.add(Message(
        chat_id=chat.id,
        role="user",
        type="text",
        content=payload.prompt
    ))
    await db.commit()

    async def stream():
        collected = []
        total_tokens = 0

        async for chunk in ollama_chat(
            db=db,
            chat_id=chat.id,
            model="qwen2.5vl",
            prompt=payload.prompt,
            images_b64=payload.images,
            thinking=payload.thinking,
            stream=True
        ):
            msg = chunk.get("message", {})
            thinking = msg.get("thinking")
            content = msg.get("content")

            if thinking:
                yield thinking
                total_tokens += len(thinking.split())

            if content:
                yield content
                collected.append(content)
                total_tokens += len(content.split())

            if chunk.get("done"):
                break

        final = "".join(collected)

        db.add(Message(
            chat_id=chat.id,
            role="assistant",
            type="text",
            content=final,
            tokens_used=total_tokens
        ))
        await db.commit()

        await increment_requests(db, user.id, tokens_used=total_tokens)

    return StreamingResponse(
        stream(),
        media_type="text/plain",
        headers={"X-Chat-Id": str(chat.id)}
    )


@router.get("/history")
async def get_chats_history(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    res = await db.execute(
        select(Chat)
        .where(Chat.user_id == user.id)
        .order_by(Chat.created_at.desc())
    )
    chats = res.scalars().all()

    out = []

    for c in chats:
        last_msg_res = await db.execute(
            select(Message)
            .where(Message.chat_id == c.id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        last_msg = last_msg_res.scalar()

        if last_msg:
            chat_type = last_msg.type
        else:
            chat_type = "empty"

        out.append({
            "id": str(c.id),
            "title": c.title,
            "type": chat_type,
            "created_at": c.created_at
        })

    return out


@router.get("/{chat_id}/messages")
async def get_chat_messages(
    chat_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    chat = await db.get(Chat, chat_id)
    if not chat or chat.user_id != user.id:
        raise HTTPException(404, "Chat not found")

    res = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at)
    )
    msgs = res.scalars().all()

    out = []
    for m in msgs:
        if m.type == "image":
            out.append({
                "id": str(m.id),
                "role": m.role,
                "type": "image",
                "thumbnail": f"data:image/jpeg;base64,{m.image_thumb}",
                "created_at": m.created_at
            })
        elif m.type == "video":
            out.append({
                "id": str(m.id),
                "role": m.role,
                "type": "video",
                "thumbnail": f"data:image/jpeg;base64,{m.image_thumb}",
                "created_at": m.created_at
            })
        else:
            out.append({
                "id": str(m.id),
                "role": m.role,
                "type": "text",
                "content": m.content,
                "created_at": m.created_at
            })

    return out



@router.get("/image/{message_id}")
async def get_full_image(
    message_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    msg = await db.get(Message, message_id)
    if not msg:
        raise HTTPException(404, "Message not found")

    chat = await db.get(Chat, msg.chat_id)
    if not chat or chat.user_id != user.id:
        raise HTTPException(403, "Forbidden")

    if msg.type != "image":
        raise HTTPException(400, "This message is not an image")

    if not msg.image_full:
        raise HTTPException(400, "This message has no image")

    return Response(
        content=base64.b64decode(msg.image_full),
        media_type="image/jpeg"
    )


@router.get("/video/{message_id}")
async def get_full_video(
    message_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    msg = await db.get(Message, message_id)
    if not msg:
        raise HTTPException(404, "Message not found")

    chat = await db.get(Chat, msg.chat_id)
    if not chat or chat.user_id != user.id:
        raise HTTPException(403, "Forbidden")

    if not msg.video_full:
        raise HTTPException(400, "This message has no video")

    try:
        video_bytes = base64.b64decode(msg.video_full)
    except:
        raise HTTPException(500, "Video decode error")

    return Response(
        content=video_bytes,
        media_type="video/mp4",
        headers={
            "Content-Disposition": "inline; filename=\"video.mp4\""
        }
    )
    
@router.post("/create")
async def create_chat(
    payload: ChatCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    chat = Chat(user_id=user.id, title=payload.title)
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return {"chat_id": str(chat.id), "title": chat.title}


@router.put("/{chat_id}/rename")
async def rename_chat(
    chat_id: UUID,
    payload: ChatRename,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    chat = await db.get(Chat, chat_id)
    if not chat or chat.user_id != user.id:
        raise HTTPException(404, "Chat not found")

    chat.title = payload.new_title
    await db.commit()
    return {"chat_id": str(chat.id), "title": chat.title}


@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    chat = await db.get(Chat, chat_id)
    if not chat or chat.user_id != user.id:
        raise HTTPException(404, "Chat not found")

    await db.delete(chat)
    await db.commit()
    return {"detail": f"Chat {chat_id} deleted"}
