from pydantic import BaseModel
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

class NoteMetadata(BaseModel):
    id: str = str(uuid.uuid4())
    timestamp: str = datetime.now().isoformat()
    text: str

class DeleteNoteRequest(BaseModel):
    note_id: str
    

# models.py - Add this new model
class EditNoteRequest(BaseModel):
    note_id: str
    new_text: str