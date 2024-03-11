from annotated_types import Gt, Ge
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, Literal, List

# User Schemas

class CreateUser(BaseModel):
    name: str
    username: str
    email: EmailStr
    hashed_password: str
    verified_user: Optional[Literal[True, False]] = Field(False, description="is a verified user? Choices: [true, false]")

class GetUser(BaseModel):
    id: int
    name: str
    username: str
    email: EmailStr
    verified_user: bool
    modified_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UpdateUser(BaseModel):
    name: Optional[str] = Field(None, description="update name")
    verified_user: Optional[Literal[True, False]] = Field(False, description="is a verified user? Choices: [true, false]")

class GetUsername(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)

class GetEmail(BaseModel):
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

# Vote Schemas

class GetVote(BaseModel):
    vote: int
    post_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)

class UpdateVote(BaseModel):
    vote: Literal[0, 1, 2, 3, 4, 5]

# Comment Schemas

class CreateComment(BaseModel):
    comment: str

class GetComment(BaseModel):
    comment: str
    id: int

    model_config = ConfigDict(from_attributes=True)

class UpdateComment(BaseModel):
    comment: str

# Post Schemas

class CreatePost(BaseModel):
    title: str
    description: Optional[str] = Field(None, description="update post description")

class GetPost(BaseModel):
    id: int
    puid: int
    title: str
    description: str
    modified_at: datetime
    created_at: datetime
    owner: GetUsername
    post_votes: Optional[List[GetVote]]
    post_comments: Optional[List[GetComment]]

    model_config = ConfigDict(from_attributes=True)

class UpdatePost(BaseModel):
    title: Optional[str] = Field(None, description="update post title")
    description: Optional[str] = Field(None, description="update post description")

# Login Schemas

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
