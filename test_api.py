import httpx
import json

API_URL = "http://localhost:8000/v1/chat/completions"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiaWF0IjoxNzYyODAzNjg1LCJleHAiOjE3NjI4MTQ0ODV9.7FSulwsRxVKEkB3IVrJsCpvJyREkQLMEXrYuq5zfl2U"

payload = {
    "prompt": "Какой вопрос я задавал до этого?",
    "chat_id": "f67b546f-ddc7-4f89-8ea3-19fd6bb56f3e"
}

async def main():
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            "POST",
            API_URL,
            headers={
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
            json=payload,
        ) as response:
            chat_id = response.headers.get("X-Chat-Id")
            print(f"\n🧩 Chat ID: {chat_id}\n")
            print("💬 Ответ модели:\n")

            async for line in response.aiter_text():
                print(line, end="", flush=True)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
