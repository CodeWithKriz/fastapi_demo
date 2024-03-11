from datetime import datetime
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, oauth2, utils
from ..database import get_db

router = APIRouter(prefix="/users/{username}/posts")

# Posts API

@router.get("/", response_model=List[schemas.GetPost])
def read_posts(username: str, page: int = 10, db: Session = Depends(get_db)):
    user_query = db.query(models.UserModel).filter(models.UserModel.username == username)
    user = user_query.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"username {username} not found!"
        )
    posts = db.query(models.PostModel).filter(models.PostModel.owner_id == user.id).all()
    return posts

@router.post("/", response_model=schemas.GetPost, status_code=status.HTTP_201_CREATED)
def create_post(username: str, post: schemas.CreatePost, db: Session = Depends(get_db), current_user: schemas.GetUser = Depends(oauth2.get_current_user)):
    if username != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized!"
        )
    puid = utils.get_random_number()
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
    new_post = post_query.first()
    if new_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post id {puid} already exists!"
        )
    post = post.model_dump(exclude_none=True)
    post["puid"] = puid
    post["owner_id"] = current_user.id
    new_post = models.PostModel(**post)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/{puid}", response_model=schemas.GetPost)
def read_post(username: str, puid: int, db: Session = Depends(get_db)):
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
    post = post_query.first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post id {puid} not found!"
        )
    return post

@router.put("/{puid}", response_model=schemas.GetPost)
def update_post(username: str, puid: int, post: schemas.UpdatePost, db: Session = Depends(get_db), current_user: schemas.GetUser = Depends(oauth2.get_current_user)):
    if (not current_user) or (username != current_user.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized!"
        )
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
    updated_post = post.model_dump(exclude_none=True)
    updated_post["modified_at"] = datetime.utcnow()
    post_query.update(updated_post, synchronize_session=False)
    db.commit()
    return existing_post

@router.delete("/{puid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(username: str, puid: int, db: Session = Depends(get_db), current_user: schemas.GetUser = Depends(oauth2.get_current_user)):
    if (not current_user) or (username != current_user.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized!"
        )
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
    # post_query.delete(synchronize_session=False)
    # db.commit()
    db.delete(existing_post)
    db.commit()
    print(f"Post Id {puid} deleted!")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
