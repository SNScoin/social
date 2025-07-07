from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum, Text, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Platform(str, Enum):
    youtube = "youtube"
    tiktok = "tiktok"
    instagram = "instagram"
    facebook = "facebook"

class SocialLink(Base):
    __tablename__ = "social_links"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    platform = Column(SQLEnum(Platform), nullable=False)
    title = Column(String)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Profile Information
    display_name = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)  # URL to profile picture
    bio = Column(Text, nullable=True)
    timezone = Column(String, default="UTC")
    
    # Account Security
    email_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    companies = relationship("Company", back_populates="owner")
    links = relationship("Link", back_populates="user")
    monday_connections = relationship("MondayConnection", back_populates="user")

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner = relationship("User", back_populates="companies")
    links = relationship("Link", back_populates="company")
    monday_config = relationship("MondayConfig", back_populates="company", uselist=False)

class Link(Base):
    __tablename__ = "links"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    title = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="links")
    company = relationship("Company", back_populates="links")
    metrics = relationship("LinkMetrics", back_populates="link", uselist=False, cascade="all, delete-orphan")
    monday_item_id = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Link(id={self.id}, url='{self.url}', platform='{self.platform}')>"

class LinkMetrics(Base):
    __tablename__ = "link_metrics"
    id = Column(Integer, primary_key=True, index=True)
    link_id = Column(Integer, ForeignKey("links.id"), nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    link = relationship("Link", back_populates="metrics")

class MondayConnection(Base):
    __tablename__ = "monday_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    api_token = Column(String, nullable=True)
    workspace_id = Column(String, nullable=True)
    workspace_name = Column(String, nullable=True)
    board_id = Column(String, nullable=True)
    board_name = Column(String, nullable=True)
    item_id = Column(String, nullable=True)
    item_name = Column(String, nullable=True)
    views_column_id = Column(String, nullable=True)
    views_column_name = Column(String, nullable=True)
    likes_column_id = Column(String, nullable=True)
    likes_column_name = Column(String, nullable=True)
    comments_column_id = Column(String, nullable=True)
    comments_column_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="monday_connections")
    company = relationship("Company", backref="monday_connection")

class MondayConfig(Base):
    __tablename__ = "monday_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), unique=True)
    company = relationship("Company", back_populates="monday_config")
    api_key = Column(String)
    board_id = Column(String)
    workspace_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 