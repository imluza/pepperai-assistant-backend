import base64

async def read_upload_file(file):
    data = await file.read()
    b64 = base64.b64encode(data).decode("utf-8")
    return data, b64
