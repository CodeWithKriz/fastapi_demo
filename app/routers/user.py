from datetime import datetime
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, utils, oauth2
from ..database import get_db

router = APIRouter(prefix="/users")

# Users API

@router.get("/", response_model=List[schemas.GetUser])
def read_users(page: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.UserModel).all()
    return users

@router.post("/", response_model=schemas.GetUser, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.CreateUser, db: Session = Depends(get_db)):
    user_query = db.query(models.UserModel).filter(models.UserModel.email == user.email)
    new_user = user_query.first()
    if new_user:
        raise HTTPException(
            status_code=status.HTTP_226_IM_USED,
            detail=f"email {user.email} already exists!"
        )
    user_query = db.query(models.UserModel).filter(models.UserModel.username == user.username)
    new_user = user_query.first()
    if new_user:
        raise HTTPException(
            status_code=status.HTTP_226_IM_USED,
            detail=f"username {user.username} already exists!"
        )
    new_user = user.model_dump(exclude_none=True)
    new_user["hashed_password"] = utils.hash_password(password=new_user["hashed_password"])
    new_user = models.UserModel(**new_user)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{username}", response_model=schemas.GetUser)
def read_user(username: str, db: Session = Depends(get_db)):
    user_query = db.query(models.UserModel).filter(models.UserModel.username == username)
    user = user_query.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"username {username} not found!"
        )
    return user

@router.put("/{username}", response_model=schemas.GetUser)
def update_user(username: str, user: schemas.UpdateUser, db: Session = Depends(get_db), current_user: schemas.GetUser = Depends(oauth2.get_current_user)):
    if (not current_user) or (username != current_user.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized!"
        )
    user_query = db.query(models.UserModel).filter(models.UserModel.username == username)
    existing_user = user_query.first()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"username {username} not found!"
        )
    updated_user = user.model_dump(exclude_none=True)
    updated_user["modified_at"] = datetime.utcnow()
    user_query.update(updated_user, synchronize_session=False)
    db.commit()
    return existing_user

@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(username: str, db: Session = Depends(get_db), current_user: schemas.GetUser = Depends(oauth2.get_current_user)):
    if (not current_user) or (username != current_user.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized!"
        )
    user_query = db.query(models.UserModel).filter(models.UserModel.id == current_user.id)
    existing_user = user_query.first()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"username {username} not found!"
        )
    # user_query.delete(synchronize_session=False)
    # db.commit()
    db.delete(existing_user)
    db.commit()
    print(f"user {username} deleted!")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
