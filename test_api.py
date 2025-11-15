import base64
import json
import requests

OLLAMA = "http://host.docker.internal:11434"

MODEL = "qwen2.5vl"
IMAGE_FILE = "test.png"


def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def check_endpoint(path):
    url = f"{OLLAMA}{path}"
    try:
        r = requests.get(url, timeout=5)
        print(f"[CHECK] {url} → {r.status_code}")
    except Exception as e:
        print(f"[CHECK] {url} → ERROR {e}")


def test_chat():
    print("\n=== TEST: /api/chat SIMPLE ===")

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": "Скажи число 5"}
        ]
    }

    r = requests.post(f"{OLLAMA}/api/chat", json=payload)
    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)


def test_chat_stream():
    print("\n=== TEST: /api/chat STREAM ===")

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": "Генерируй числа от 1 до 5"}
        ],
        "stream": True
    }

    with requests.post(f"{OLLAMA}/api/chat", json=payload, stream=True) as r:
        print("STATUS:", r.status_code)
        print("STREAM:")
        for line in r.iter_lines():
            if line:
                print(line.decode(), end="", flush=True)
        print()


def test_generate():
    print("\n=== TEST: /api/generate SIMPLE ===")

    payload = {
        "model": MODEL,
        "prompt": "Скажи слово 'тест'",
        "stream": False
    }

    try:
        r = requests.post(f"{OLLAMA}/api/generate", json=payload)
        print("STATUS:", r.status_code)
        print("RESPONSE:", r.text)
    except Exception as e:
        print("ERROR:", e)


def test_generate_stream():
    print("\n=== TEST: /api/generate STREAM ===")

    payload = {
        "model": MODEL,
        "prompt": "Генерируй числа 1 2 3 4 5",
        "stream": True
    }

    try:
        with requests.post(f"{OLLAMA}/api/generate", json=payload, stream=True) as r:
            print("STATUS:", r.status_code)
            print("STREAM:")
            for line in r.iter_lines():
                if line:
                    print(line.decode(), end="", flush=True)
        print()
    except Exception as e:
        print("ERROR:", e)


def test_chat_image():
    print("\n=== TEST: /api/chat WITH IMAGE ===")

    img = encode_image(IMAGE_FILE)

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Что на изображении?",
                "images": [img]
            }
        ]
    }

    r = requests.post(f"{OLLAMA}/api/chat", json=payload)
    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)


def test_generate_image():
    print("\n=== TEST: /api/generate WITH IMAGE ===")

    img = encode_image(IMAGE_FILE)

    payload = {
        "model": MODEL,
        "prompt": "Опиши картинку",
        "images": [img],
        "stream": False
    }

    try:
        r = requests.post(f"{OLLAMA}/api/generate", json=payload)
        print("STATUS:", r.status_code)
        print("RESPONSE:", r.text)
    except Exception as e:
        print("ERROR:", e)


if __name__ == "__main__":
    print("=== CHECKING ENDPOINTS ===")
    check_endpoint("/api/tags")
    check_endpoint("/api/chat")
    check_endpoint("/api/generate")

    test_chat()
    test_chat_stream()

    test_generate()
    test_generate_stream()

    test_chat_image()
    test_generate_image()
