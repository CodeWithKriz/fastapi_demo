from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .routers import root, user, post, auth, votes, comments
from .config import settings

# run command
# uvicorn app.main:app --port 5000 --reload

# models.Base.metadata.create_all(bind=engine)
app = FastAPI()

origins = settings.allowed_origins.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print(f"running app in {settings.environment}")

app.include_router(root.router)
app.include_router(user.router, prefix="/api/v1", tags=["Users"])
app.include_router(post.router, prefix="/api/v1", tags=["User Posts"])
app.include_router(votes.router, prefix="/api/v1", tags=["Post Votes"])
app.include_router(comments.router, prefix="/api/v1", tags=["Post Comments"])
app.include_router(auth.router, tags=["Auth"])
