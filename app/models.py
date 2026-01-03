from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime

# JWT

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# Notes

class NoteRequest(BaseModel):
    # user_id: str
    text: str

class QueryRequest(BaseModel):
    query: str

# class UserCheckRequest(BaseModel):
#     user_id: str

# class NoteMetadata(BaseModel):
#     id: str = str(uuid.uuid4())
#     timestamp: str = datetime.now().isoformat()
#     text: str

class NoteMetadata(BaseModel):
<<<<<<< HEAD
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    text: str


=======
    id: str = str(uuid.uuid4())
    timestamp: str = datetime.now().isoformat()
    text: str

>>>>>>> 36d4cad592ebe84dd3ddf7ff88904d87270a96c5
class DeleteNoteRequest(BaseModel):
    note_id: str
    

# models.py - Add this new model
class EditNoteRequest(BaseModel):
    note_id: str
    new_text: str