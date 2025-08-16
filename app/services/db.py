from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime


SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# class Note(Base):
#     __tablename__ = "notes"
#     id = Column(String, primary_key=True)
#     title = Column(String)
#     content = Column(Text)
#     user_id = Column(String, ForeignKey("users.id"))
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow)
#     user = relationship("User", back_populates="notes")

# User.notes = relationship("Note", order_by=Note.created_at.desc())



