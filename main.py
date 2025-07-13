from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import NoteRequest, QueryRequest, UserCheckRequest
from app.services.chroma_service import add_note, query_notes, has_notes
import os

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/notes/add")
async def add_user_note(request: NoteRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    note_id = add_note(request.user_id, request.text)
    return {
        "message": "Note added successfully",
        "note_id": note_id,
        "user_id": request.user_id
    }

@app.post("/notes/query")
async def query_user_notes(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    results = query_notes(request.user_id, request.query)
    if not results:
        return {"message": "No matching notes found", "results": []}
    
    return {
        "message": f"Found {len(results)} results",
        "results": results
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