from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_auth, routes_user, routes_chat, routes_image, routes_video

app = FastAPI(title="Ура, ура, хакатон",
    version="6.7")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_auth.router)
app.include_router(routes_user.router)
app.include_router(routes_chat.router)
app.include_router(routes_image.router)
app.include_router(routes_video.router)

@app.get("/")
def root():
    return {"status": "ok"}
