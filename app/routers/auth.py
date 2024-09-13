from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, schemas, utils, oauth2
from ..database import get_db

router = APIRouter(prefix="/auth")

@router.post("/", response_model=schemas.AccessToken)
# def generate_token(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
def generate_token(credentials: schemas.OAuth2PasswordRequestFormExtended = Depends(), db: Session = Depends(get_db)):
    print(credentials.username, credentials.password)
    print(credentials.client_id, credentials.client_secret)
    print(credentials.grant_type, credentials.scopes)
    if credentials.username and credentials.password:
        cred_query = (
            db.query(models.UserModel)
            .filter(
                (models.UserModel.username == credentials.username.lower()) | 
                (models.UserModel.email == credentials.username.lower())
            )
        )
        user = cred_query.first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"invalid username!"
            )
        if not utils.verify_password(password=credentials.password, hashed_password=user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"invalid password!"
            )
    elif credentials.client_id and credentials.client_secret:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=f"client authentication not allowed!"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"authentication method not found!"
        )
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
