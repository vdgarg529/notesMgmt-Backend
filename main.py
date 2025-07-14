from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import RegisterRequest, LoginRequest, NoteRequest, QueryRequest, UserCheckRequest
from app.services.chroma_service import add_note, query_notes, has_notes
from app.services.db import SessionLocal, engine, User, Base
import os
from app.services.auth import (
    get_password_hash,
    create_access_token,
    get_current_user,
    verify_password,
)
import uuid


from fastapi import HTTPException, Depends
import asyncio
from app.services.llm_utils import generate_summary  # Import from new module




app = FastAPI()

Base.metadata.create_all(bind=engine)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT authentication

@app.post("/register")
async def register(user_in: RegisterRequest):
    db = SessionLocal()
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(id=str(uuid.uuid4()), email=user_in.email, password_hash=get_password_hash(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(data={"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/login")
async def login(login_data: LoginRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(data={"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}

# Notes creation

@app.post("/notes/add")
async def add_user_note(request: NoteRequest, current_user: User = Depends(get_current_user)):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    print(current_user)
    # note_id = add_note(request.user_id, request.text)
    note_id = add_note(current_user, request.text)
    return {
        "message": "Note added successfully",
        "note_id": note_id,
        "user_id": current_user
    }

# @app.post("/notes/query")
# async def query_user_notes(request: QueryRequest, current_user: User = Depends(get_current_user)):
#     if not request.query.strip():
#         raise HTTPException(status_code=400, detail="Query cannot be empty")
    
#     results = query_notes(current_user, request.query)
#     if not results:
#         return {"message": "No matching notes found", "results": []}
    
#     return {
#         "message": f"Found {len(results)} results",
#         "results": results
#     }



@app.post("/notes/query")
async def query_user_notes(request: QueryRequest, current_user: User = Depends(get_current_user)):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Get notes from vector DB (run in thread to avoid blocking)
    results = await asyncio.to_thread(
        query_notes, 
        current_user, 
        request.query
    )
    
    if not results:
        return {
            "summary": "No matching notes found",
            "results": []
        }
    
    # Extract text content for summarization
    note_texts = [res["text"] for res in results]
    
    # Generate summary asynchronously
    summary = await generate_summary(note_texts)
    
    return {
        "summary": summary,
        "results": results,
        "count": len(results)
    }



@app.get("/notes/check")
async def check_user_notes(request: UserCheckRequest):
    user_has_notes = has_notes(request.user_id)
    return {
        "user_id": request.user_id,
        "has_notes": user_has_notes
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}