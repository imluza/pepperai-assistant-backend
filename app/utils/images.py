import base64
import io
from PIL import Image

def make_thumbnail(b64: str, size: int = 256) -> str:
    img = Image.open(io.BytesIO(base64.b64decode(b64)))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img.thumbnail((size, size))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=70)

    return base64.b64encode(buf.getvalue()).decode()
