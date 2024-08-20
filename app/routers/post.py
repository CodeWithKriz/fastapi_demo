from datetime import datetime
from fastapi import Response, status, HTTPException, Depends, APIRouter, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import models, schemas, oauth2, utils
from ..database import get_db

router = APIRouter(prefix="/users/{username}/posts")

# Posts API

@router.get("/", response_model=schemas.GetPaginatedPost)
def read_posts(username: str, page: int = 1, page_size: int = 8, db: Session = Depends(get_db)):
    user_query = db.query(models.UserModel).filter(models.UserModel.username == username.lower())
    user = user_query.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"username {username} not found!"
        )
    posts_query = db.query(models.PostModel).filter(models.PostModel.owner_id == user.id)
    total_count = posts_query.count()
    paginated_posts = posts_query.offset((page - 1) * page_size).limit(page_size).all()
    response = {
        "items": paginated_posts,
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
    }
    return response

@router.post("/", response_model=schemas.GetPost, status_code=status.HTTP_201_CREATED)
def create_post(username: str, post: schemas.CreatePost = Depends(schemas.CreatePost.as_form), db: Session = Depends(get_db), current_user: schemas.GetUser = Depends(oauth2.get_current_user)):
    if (not current_user) or (username.lower() != current_user.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized!"
        )

    # generate unique id for post
    puid = utils.get_random_number()

    user_query = db.query(models.UserModel).filter(models.UserModel.id == current_user.id)
    user = user_query.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"username {username} not found!"
        )

    post_query = db.query(models.PostModel).filter(
        (models.PostModel.owner_id == user.id) & 
        (models.PostModel.puid == puid)
    )
    new_post = post_query.first()
    if new_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post id {puid} already exists!"
        )

    accepted_file_types = [
        "image/jpeg", "image/png", "image/gif", "image/bmp", "image/tiff", "image/webp", "image/heic",
        "video/mp4", "video/x-msvideo", "video/x-matroska", "video/quicktime", "video/x-ms-wmv",
        "video/x-flv", "video/webm", "video/mpeg", "video/3gpp", "video/ogg"
    ]
    for media in post.post_medias:
        if media.content_type not in accepted_file_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"File type {media.content_type} not accepted"
            )

    new_post_data = post.model_dump(exclude_none=True)
    new_post_data.pop("post_medias", None)
    new_post_data["puid"] = puid
    new_post_data["owner_id"] = current_user.id
    new_post = models.PostModel(**new_post_data)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    post_medias_list = []
    for media in post.post_medias:
        # generate unique id for media
        muid = utils.get_random_number()

        db_media = models.PostMediaModel(
            muid=muid, media=media.file.read(),
            media_type=media.content_type, post_id=new_post.id
        )
        db.add(db_media)
        post_medias_list.append(db_media)
    db.commit()

    new_post.post_medias = post_medias_list
    return new_post

@router.get("/{puid}", response_model=schemas.GetPost)
def read_post(username: str, puid: int, db: Session = Depends(get_db)):
    user_query = db.query(models.UserModel).filter(models.UserModel.username == username.lower())
    user = user_query.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"username {username} not found!"
        )

    post_query = db.query(models.PostModel).filter(
        (models.PostModel.owner_id == user.id) & 
        (models.PostModel.puid == puid)
    )
    post = post_query.first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post id {puid} not found!"
        )

    return post

@router.put("/{puid}", response_model=schemas.GetPost)
def update_post(username: str, puid: int, post: schemas.UpdatePost = Depends(schemas.UpdatePost.as_form), db: Session = Depends(get_db), current_user: schemas.GetUser = Depends(oauth2.get_current_user)):
    if (not current_user) or (username.lower() != current_user.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized!"
        )

    user_query = db.query(models.UserModel).filter(models.UserModel.id == current_user.id)
    user = user_query.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"username {username} not found!"
        )

    post_query = db.query(models.PostModel).filter(
        (models.PostModel.owner_id == user.id) & 
        (models.PostModel.puid == puid)
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
    if (not current_user) or (username.lower() != current_user.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized!"
        )

    user_query = db.query(models.UserModel).filter(models.UserModel.id == current_user.id)
    user = user_query.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"username {username} not found!"
        )

    post_query = db.query(models.PostModel).filter(
        (models.PostModel.owner_id == user.id) & 
        (models.PostModel.puid == puid)
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
