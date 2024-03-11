from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, schemas, utils, oauth2
from ..database import get_db

router = APIRouter(prefix="/auth")

@router.post("/token", response_model=schemas.AccessToken)
# def generate_token(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
def generate_token(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    cred_query = (
        db.query(models.UserModel)
        .filter(
            (models.UserModel.username == credentials.username) | 
            (models.UserModel.email == credentials.username)
        )
    )
    user = cred_query.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"invalid credentials!"
        )
    if not utils.verify_password(password=credentials.password, hashed_password=user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"invalid credentials!"
        )
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
