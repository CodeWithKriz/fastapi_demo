from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List
from starlette.responses import StreamingResponse
import io

from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(prefix="/users/{username}/posts/{puid}/medias")

# Post Objects API

@router.get("/", response_model=List[schemas.GetPostMediaId])
def read_medias(username: str, puid: int, db: Session = Depends(get_db)):
    user_query = db.query(models.UserModel).filter(models.UserModel.username == username)
    user = user_query.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"username {username} not found!"
        )
    post_query = (
        db.query(models.PostModel)
        .filter(
            (models.PostModel.owner_id == user.id) & 
            (models.PostModel.puid == puid)
        )
    )
    existing_post = post_query.first()
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post id {puid} not found!"
        )
    medias = db.query(models.PostMediaModel).filter(models.PostMediaModel.post_id == existing_post.id).all()
    return medias

@router.get("/{muid}", response_model=schemas.GetPostMedia)
def read_media(username: str, puid: int, muid: int, db: Session = Depends(get_db)):
    user_query = db.query(models.UserModel).filter(models.UserModel.username == username)
    user = user_query.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"username {username} not found!"
        )
    post_query = (
        db.query(models.PostModel)
        .filter(
            (models.PostModel.owner_id == user.id) & 
            (models.PostModel.puid == puid)
        )
    )
    existing_post = post_query.first()
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post id {puid} not found!"
        )
    post_media_query = db.query(models.PostMediaModel).filter(models.PostMediaModel.muid == muid)
    post_media = post_media_query.first()
    if not post_media_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Media id {muid} not found!"
        )
    return StreamingResponse(io.BytesIO(post_media.media), media_type=post_media.media_type)
