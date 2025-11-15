import json
from typing import List, Optional, AsyncGenerator
import httpx

from app.services.chat_history import load_messages

OLLAMA_CHAT_URL = "http://host.docker.internal:11434/api/chat"


async def ollama_chat_stream(
    db,
    chat_id,
    model: str,
    prompt: str,
    images_b64: Optional[List[str]],
    thinking: Optional[str]
) -> AsyncGenerator[dict, None]:
    history = await load_messages(db, chat_id)

    msg = {"role": "user", "content": prompt}
    if images_b64:
        msg["images"] = images_b64
    history.append(msg)

    payload = {"model": model, "messages": history, "stream": True}
    if thinking:
        payload["options"] = {"thinking": thinking}

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", OLLAMA_CHAT_URL, json=payload) as resp:
            async for line in resp.aiter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except:
                    continue
                yield data


async def ollama_chat_generate(
    db,
    chat_id,
    model: str,
    prompt: str,
    images_b64: Optional[List[str]],
    thinking: Optional[str]
):
    history = await load_messages(db, chat_id)

    msg = {"role": "user", "content": prompt}
    if images_b64:
        msg["images"] = images_b64
    history.append(msg)

    payload = {"model": model, "messages": history, "stream": False}
    if thinking:
        payload["options"] = {"thinking": thinking}

    async with httpx.AsyncClient(timeout=None) as client:
        resp = await client.post(OLLAMA_CHAT_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()

    text = data["message"]["content"]
    tokens = (
        data.get("prompt_eval_count", 0)
        + data.get("eval_count", 0)
    )

    return text, tokens


async def ollama_chat(
    db,
    chat_id,
    model: str,
    prompt: str,
    images_b64: Optional[List[str]] = None,
    thinking: Optional[str] = None,
    stream: bool = True,
):
    if stream:
        return ollama_chat_stream(
            db=db,
            chat_id=chat_id,
            model=model,
            prompt=prompt,
            images_b64=images_b64,
            thinking=thinking
        )
    else:
        return await ollama_chat_generate(
            db=db,
            chat_id=chat_id,
            model=model,
            prompt=prompt,
            images_b64=images_b64,
            thinking=thinking
        )
