from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

class NoteRequest(BaseModel):
    user_id: str
    text: str

class QueryRequest(BaseModel):
    user_id: str
    query: str

class UserCheckRequest(BaseModel):
    user_id: str

class NoteMetadata(BaseModel):
    id: str = str(uuid.uuid4())
    timestamp: str = datetime.now().isoformat()
    text: str