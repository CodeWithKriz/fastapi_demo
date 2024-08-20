from datetime import datetime
from fastapi import Response, status, HTTPException, Depends, APIRouter, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import models, schemas, utils, oauth2
from ..database import get_db

router = APIRouter(prefix="/users")

# Users API

@router.get("/", response_model=schemas.GetPaginatedUser)
def read_users(query: Optional[str] = Query(None), page: int = 1, page_size: int = 8, db: Session = Depends(get_db)):
    users_query = db.query(models.UserModel)
    if query:
        users_query = users_query.filter(
            (models.UserModel.username.ilike(f"%{query}%")) | 
            (models.UserModel.name.ilike(f"%{query}%"))
        )
    total_count = users_query.count()
    paginated_users = users_query.offset((page - 1) * page_size).limit(page_size).all()
    response = {
        "items": paginated_users,
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
    }
    return response

@router.post("/", response_model=schemas.GetUser, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.CreateUser = Depends(schemas.CreateUser.as_form), db: Session = Depends(get_db)):
    user_query = db.query(models.UserModel).filter(
        (models.UserModel.email == user.email) |
        (models.UserModel.username == user.username)
    )
    new_user = user_query.first()
    if new_user:
        if new_user.email == user.email:
            detail = f"email {user.email} already exists!"
        elif new_user.username == user.username:
            detail = f"username {user.username} already exists!"
        else:
            detail = "given ids already exists!"
        raise HTTPException(status_code=status.HTTP_226_IM_USED, detail=detail)
    new_user_data = user.model_dump(exclude_none=True)
    new_user_data["hashed_password"] = utils.hash_password(password=new_user_data["password"])
    new_user_data.pop("password", None)
    new_user = models.UserModel(**new_user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{username}", response_model=schemas.GetUser)
def read_user(username: str, db: Session = Depends(get_db)):
    user_query = db.query(models.UserModel).filter(models.UserModel.username == username.lower())
    user = user_query.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"username {username} not found!"
        )
    return user

@router.put("/{username}", response_model=schemas.GetUser)
def update_user(username: str, user: schemas.UpdateUser = Depends(schemas.UpdateUser.as_form), db: Session = Depends(get_db), current_user: schemas.GetUser = Depends(oauth2.get_current_user)):
    if (not current_user) or (username.lower() != current_user.username):
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
    updated_user = user.model_dump(exclude_none=True)
    updated_user["modified_at"] = datetime.utcnow()
    user_query.update(updated_user, synchronize_session=False)
    db.commit()
    return existing_user

@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(username: str, db: Session = Depends(get_db), current_user: schemas.GetUser = Depends(oauth2.get_current_user)):
    if (not current_user) or (username.lower() != current_user.username):
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
