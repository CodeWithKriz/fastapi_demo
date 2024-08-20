from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, oauth2, utils
from ..database import get_db

router = APIRouter(prefix="/users/{username}/posts/{puid}/comments")

# Comments API

@router.get("/", response_model=schemas.GetPaginatedComments)
def read_comments(username: str, puid: int, page: int = 1, page_size: int = 8, db: Session = Depends(get_db)):
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
    existing_post = post_query.first()
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post id {puid} not found!"
        )

    post_comments_query = db.query(models.PostCommentModel).filter(models.PostCommentModel.post_id == existing_post.id)
    total_count = post_comments_query.count()
    paginated_post_comments = post_comments_query.offset((page - 1) * page_size).limit(page_size).all()
    response = {
        "items": paginated_post_comments,
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
    }
    return response

@router.post("/", response_model=schemas.GetComment, status_code=status.HTTP_201_CREATED)
def create_comments(username: str, puid: int, comment: schemas.CreateComment, db: Session = Depends(get_db), current_user: schemas.GetUser = Depends(oauth2.get_current_user)):
    if (not current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized!"
        )

    # generate unique id for comment
    cuid = utils.get_random_number()

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
    existing_post = post_query.first()
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post id {puid} not found!"
        )

    comments_query = db.query(models.PostCommentModel).filter(
        (models.PostCommentModel.post_id == existing_post.id) & 
        (models.PostCommentModel.user_id == current_user.id) & 
        (models.PostCommentModel.cuid == cuid)
    )
    new_comment = comments_query.first()
    if new_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Commnet id {cuid} already exists!"
        )

    new_comment = comment.model_dump(exclude_none=True)
    new_comment["post_id"] = existing_post.id
    new_comment["user_id"] = current_user.id
    new_comment["cuid"] = cuid
    new_comment = models.PostCommentModel(**new_comment)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@router.get("/{cuid}", response_model=schemas.GetComment)
def read_comments(username: str, puid: int, cuid: int, db: Session = Depends(get_db)):
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
    existing_post = post_query.first()
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post id {puid} not found!"
        )

    post_comments_query = db.query(models.PostCommentModel).filter(models.PostCommentModel.cuid == cuid)
    post_comments = post_comments_query.first()
    if not post_comments_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment id {cuid} not found!"
        )

    return post_comments

@router.put("/{cuid}", response_model=schemas.GetComment)
def update_comments(username: str, puid: int, cuid: int, comment: schemas.UpdateComment, db: Session = Depends(get_db), current_user: schemas.GetUser = Depends(oauth2.get_current_user)):
    if (not current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized!"
        )

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
    existing_post = post_query.first()
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post id {puid} not found!"
        )

    post_comments_query = db.query(models.PostCommentModel).filter(models.PostCommentModel.cuid == cuid)
    post_comments = post_comments_query.first()
    if not post_comments_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment id {cuid} not found!"
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

@router.delete("/{cuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comments(username: str, puid: int, cuid: int, db: Session = Depends(get_db), current_user: schemas.GetUser = Depends(oauth2.get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized!"
        )

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
    existing_post = post_query.first()
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post id {puid} not found!"
        )

    post_comments_query = db.query(models.PostCommentModel).filter(models.PostCommentModel.cuid == cuid)
    post_comments = post_comments_query.first()
    if not post_comments_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment id {cuid} not found!"
        )

    if not current_user.id in [existing_post.owner_id, post_comments.user_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized!"
        )
    db.delete(post_comments)
    db.commit()
    print(f"Comment Id {cuid} deleted!")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
