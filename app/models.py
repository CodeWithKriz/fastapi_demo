from datetime import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    verified_user = Column(Boolean, default=False)
    modified_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow())
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow())

    posts = relationship("PostModel", back_populates="owner", cascade="all, delete-orphan", lazy=True)
    post_votes = relationship("PostVoteModel", back_populates="user", cascade="all, delete-orphan", lazy=True)
    post_comments = relationship("PostCommentModel", back_populates="user", cascade="all, delete-orphan", lazy=True)

class PostModel(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)

    puid = Column(Integer, nullable=False, unique=True)
    title = Column(String, nullable=False)
    description = Column(String, default=None)
    modified_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow())
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow())

    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("UserModel", back_populates="posts")

    post_votes = relationship("PostVoteModel", back_populates="post", cascade="all, delete-orphan", lazy=True)
    post_comments = relationship("PostCommentModel", back_populates="post", cascade="all, delete-orphan", lazy=True)

class PostVoteModel(Base):
    __tablename__ = "post_votes"

    id = Column(Integer, primary_key=True)

    vote = Column(Integer, default=0)

    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    post = relationship("PostModel", back_populates="post_votes")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("UserModel", back_populates="post_votes")

class PostCommentModel(Base):
    __tablename__ = "post_comments"

    id = Column(Integer, primary_key=True)

    comment = Column(String, nullable=True)

    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    post = relationship("PostModel", back_populates="post_comments")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("UserModel", back_populates="post_comments")
