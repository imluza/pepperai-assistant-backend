from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import routes_auth, routes_user, routes_chat

app = FastAPI(title="Тимур лошпендус 228",
    version="1.3.3.7")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(routes_auth.router)
app.include_router(routes_user.router)
app.include_router(routes_chat.router)
