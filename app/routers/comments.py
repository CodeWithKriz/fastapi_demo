from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(prefix="/users/{username}/posts/{puid}/comments")

# Comments API

@router.get("/", response_model=List[schemas.GetComment])
def read_comments(username: str, puid: int, db: Session = Depends(get_db)):
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
    post_comments = db.query(models.PostCommentModel).filter(models.PostCommentModel.post_id == existing_post.id).all()
    return post_comments

@router.post("/", response_model=schemas.GetComment, status_code=status.HTTP_201_CREATED)
def create_comments(username: str, puid: int, comment: schemas.CreateComment, db: Session = Depends(get_db), current_user: schemas.GetUser = Depends(oauth2.get_current_user)):
    if not current_user:
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
    comment = comment.model_dump(exclude_none=True)
    comment["post_id"] = existing_post.id
    comment["user_id"] = current_user.id
    new_comment = models.PostCommentModel(**comment)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@router.get("/{comment_id}", response_model=schemas.GetComment)
def read_comments(username: str, puid: int, comment_id: int, db: Session = Depends(get_db)):
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
    post_comments_query = db.query(models.PostCommentModel).filter(models.PostCommentModel.id == comment_id)
    post_comments = post_comments_query.first()
    if not post_comments_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment id {comment_id} not found!"
        )
    return post_comments

@router.put("/{comment_id}", response_model=schemas.GetComment)
def update_comments(username: str, puid: int, comment_id: int, comment: schemas.UpdateComment, db: Session = Depends(get_db), current_user: schemas.GetUser = Depends(oauth2.get_current_user)):
    if not current_user:
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

    post_comments_query = db.query(models.PostCommentModel).filter(models.PostCommentModel.id == comment_id)
    post_comments = post_comments_query.first()
    if not post_comments_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment id {comment_id} not found!"
        )
    if current_user.id != post_comments.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized!"
        )
    comment = comment.model_dump(exclude_none=True)
    post_comments_query.update(comment, synchronize_session=False)
    db.commit()
    return post_comments

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comments(username: str, puid: int, comment_id: int, db: Session = Depends(get_db), current_user: schemas.GetUser = Depends(oauth2.get_current_user)):
    if not current_user:
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

    post_comments_query = db.query(models.PostCommentModel).filter(models.PostCommentModel.id == comment_id)
    post_comments = post_comments_query.first()
    if not post_comments_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment id {comment_id} not found!"
        )
    if not current_user.id in [existing_post.owner_id, post_comments.user_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized!"
        )
    db.delete(post_comments)
    db.commit()
    print(f"Comment Id {comment_id} deleted!")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
