from annotated_types import Gt, Ge
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, Literal, List
from fastapi import UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm

# User Schemas

class CreateUser(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str
    verified_user: Literal[True, False, None] = Field(None, description="is a verified user? Choices: ['true', 'false']")

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        username: str = Form(...),
        email: EmailStr = Form(...),
        password: str = Form(...),
        verified_user: Optional[Literal["true", "false", "1", "0"]] = Form(None)
    ):
        if verified_user and verified_user.lower() in ["true", "1"]:
            verified_user = True
        elif verified_user and verified_user.lower() in ["false", "0"]:
            verified_user = False
        elif verified_user == None:
            verified_user = None
        else:
            raise ValueError(f"Input should be 'true' or 'false'")
        return cls(name=name, username=username.lower(), email=email.lower(), password=password, verified_user=verified_user)

class GetUser(BaseModel):
    name: str
    username: str
    email: EmailStr
    verified_user: bool
    modified_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UpdateUser(BaseModel):
    name: Optional[str] = Field(None, description="update name")
    verified_user: Literal[True, False, None] = Field(None, description="is a verified user? Choices: ['true', 'false']")

    @classmethod
    def as_form(
        cls,
        name: str = Form(None),
        verified_user: Optional[Literal["true", "false", "1", "0"]] = Form(None)
    ):
        if verified_user and verified_user.lower() in ["true", "1"]:
            verified_user = True
        elif verified_user and verified_user.lower() in ["false", "0"]:
            verified_user = False
        elif verified_user == None:
            verified_user = None
        else:
            raise ValueError(f"Input should be 'true' or 'false'")
        return cls(name=name, verified_user=verified_user)

class GetUsername(BaseModel):
    username: str

    model_config = ConfigDict(from_attributes=True)

class GetEmail(BaseModel):
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

# Vote Schemas

class GetVote(BaseModel):
    vote: int
    user: GetUsername

    model_config = ConfigDict(from_attributes=True)

class UpdateVote(BaseModel):
    vote: Literal[0, 1, 2, 3, 4, 5]

# Comment Schemas

class CreateComment(BaseModel):
    comment: str

class GetComment(BaseModel):
    cuid: int
    comment: str
    user: GetUsername

    model_config = ConfigDict(from_attributes=True)

class UpdateComment(BaseModel):
    comment: str

# Post Object Schemas

class GetPostMediaId(BaseModel):
    muid: int
    media_type: str

    model_config = ConfigDict(from_attributes=True)

class GetPostMedia(GetPostMediaId):
    media: bytes

    model_config = ConfigDict(from_attributes=True)

# Post Schemas

class CreatePost(BaseModel):
    title: str
    description: Optional[str] = Field(None, description="update post description")
    post_medias: List[UploadFile] = File([])

    @classmethod
    def as_form(cls, title: str = Form(...), description: str = Form(...), post_medias: List[UploadFile] = File([])):
        return cls(title=title, description=description, post_medias=post_medias)

class GetPost(BaseModel):
    puid: int
    title: str
    description: str
    modified_at: datetime
    created_at: datetime
    owner: GetUsername
    # post_medias: Optional[List[GetPostMediaId]]
    # post_votes: Optional[List[GetVote]]
    # post_comments: Optional[List[GetComment]]

    model_config = ConfigDict(from_attributes=True)

class UpdatePost(BaseModel):
    title: Optional[str] = Field(None, description="update post title")
    description: Optional[str] = Field(None, description="update post description")

    @classmethod
    def as_form(cls, title: str = Form(None), description: str = Form(None)):
        return cls(title=title, description=description)

# Login Schemas

class OAuth2PasswordRequestFormExtended(OAuth2PasswordRequestForm):
    def __init__(
        self,
        grant_type: str = Form("password", description="Grant type"),
        username: str = Form(None, description="Username"),
        password: str = Form(None, description="Password"),
        scope: str = Form("", description="Auth Scope"),
        client_id: str = Form(None, description="Client ID"),
        client_secret: str = Form(None, description="Client Secret"),
    ):
        super().__init__(grant_type=grant_type, username=username, password=password, scope=scope)
        self.client_id = client_id
        self.client_secret = client_secret

class UserLogin(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(from_attributes=True)

class AccessToken(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int]
    exp: Optional[datetime]

# Paginated Schemas

class GetPagination(BaseModel):
    total_count: int
    page: int
    page_size: int

class GetPaginatedUser(GetPagination):
    items: List[GetUser]

    model_config = ConfigDict(from_attributes=True)

class GetPaginatedPost(GetPagination):
    items: List[GetPost]

    model_config = ConfigDict(from_attributes=True)

class GetPaginatedComments(GetPagination):
    items: List[GetComment]

    model_config = ConfigDict(from_attributes=True)
