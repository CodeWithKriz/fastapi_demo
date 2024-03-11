from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(prefix="/users/{username}/posts/{puid}/votes")

# Votes API

@router.get("/", response_model=List[schemas.GetVote])
def read_votes(username: str, puid: int, db: Session = Depends(get_db)):
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
    post_votes = db.query(models.PostVoteModel).filter(models.PostVoteModel.post_id == existing_post.id).all()
    return post_votes

@router.put("/", response_model=schemas.GetVote)
def update_votes(username: str, puid: int, vote: schemas.UpdateVote, db: Session = Depends(get_db), current_user: schemas.GetUser = Depends(oauth2.get_current_user)):
    if (not current_user):
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

    vote_query = (
        db.query(models.PostVoteModel)
        .filter(
            (models.PostVoteModel.post_id == existing_post.id) & 
            (models.PostVoteModel.user_id == current_user.id)
        )
    )
    post_vote = vote_query.first()
    if not post_vote:
        print("new vote")
        vote = vote.model_dump(exclude_none=True)
        vote["user_id"] = current_user.id
        vote["post_id"] = existing_post.id
        post_vote = models.PostVoteModel(**vote)
        db.add(post_vote)
        db.commit()
        db.refresh(post_vote)
    elif post_vote.vote == vote.vote:
        print("same vote")
    else:
        print("update vote")
        vote = vote.model_dump(exclude_none=True)
        vote_query.update(vote, synchronize_session=False)
        db.commit()
    return post_vote
