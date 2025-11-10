import httpx
from typing import AsyncGenerator, List, Optional

OLLAMA_URL = "http://host.docker.internal:11434/api/chat"

async def stream_chat(model: str, messages: List[dict], thinking: Optional[str] = None) -> AsyncGenerator[str, None]:
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
    }
    if thinking:
        payload["think"] = thinking

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", OLLAMA_URL, json=payload) as response:
            async for line in response.aiter_lines():
                if line:
                    yield line
