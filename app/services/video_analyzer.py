import base64
import subprocess
import tempfile

async def extract_frames_bytes(video_bytes: bytes, step: int):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(video_bytes)
        path = tmp.name

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-i", path,
        "-vf", f"select='not(mod(n,{step}))'",
        "-vsync", "vfr",
        "-qscale:v", "3",
        "-f", "image2pipe",
        "-vcodec", "mjpeg",
        "pipe:1"
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    raw = proc.stdout.read()

    if not raw:
        return []

    import re
    jpgs = re.findall(rb'\xff\xd8.*?\xff\xd9', raw, flags=re.DOTALL)
    return [base64.b64encode(j).decode("utf-8") for j in jpgs]
