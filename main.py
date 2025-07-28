from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import RegisterRequest, LoginRequest, NoteRequest, QueryRequest, DeleteNoteRequest, EditNoteRequest
from app.services.chroma_service import add_note, query_notes, has_notes, get_all_notes_chroma, delete_note, edit_note
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
from app.services.llm_utils import generate_summary


# pdf downlaod feature
# Add to top of main.py
from io import BytesIO
import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from fastapi import Response

app = FastAPI()

Base.metadata.create_all(bind=engine)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/notes/add")
async def add_user_note(request: NoteRequest, current_user: User = Depends(get_current_user)):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    print(f"Adding note for user: {current_user}")
    
    # Use user ID (assuming current_user is a User object with .id attribute)
    user_id = current_user.id if hasattr(current_user, 'id') else str(current_user)
    note_id = add_note(user_id, request.text)
    
    return {
        "message": "Note added successfully",
        "note_id": note_id,
        "user_id": user_id
    }

@app.post("/notes/query")
async def query_user_notes(request: QueryRequest, current_user: User = Depends(get_current_user)):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Get user ID properly
    user_id = current_user.id if hasattr(current_user, 'id') else str(current_user)
    
    # Get notes from vector DB (run in thread to avoid blocking)
    results = await asyncio.to_thread(
        query_notes, 
        user_id, 
        request.query
    )
    
    if not results:
        return {
            "summary": "No matching notes found",
            "results": [],
            "count": 0
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
async def check_user_notes(current_user: User = Depends(get_current_user)):
    user_id = current_user.id if hasattr(current_user, 'id') else str(current_user)
    user_has_notes = has_notes(user_id)
    return {
        "user_id": user_id,
        "has_notes": user_has_notes
    }

@app.get("/notes/all")
async def get_all_notes(current_user: User = Depends(get_current_user)):
    try:
        # Get user ID properly
        user_id = current_user.id if hasattr(current_user, 'id') else str(current_user)
        print(f"Fetching all notes for user: {user_id}")
        
        # Get notes from ChromaDB
        notes = get_all_notes_chroma(user_id)
        print(f"Found {len(notes)} notes for user {user_id}")
        
        return {"notes": notes}
    except Exception as e:
        print(f"Error fetching all notes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch notes: {str(e)}")


@app.delete("/notes/delete")
async def delete_user_note(
    request: DeleteNoteRequest, 
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if hasattr(current_user, 'id') else str(current_user)
    success = await asyncio.to_thread(delete_note, user_id, request.note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted successfully"}



# Add to main.py after other note endpoints
@app.get("/notes/download")
async def download_notes(current_user: User = Depends(get_current_user)):
    try:
        # Get user ID
        user_id = current_user.id if hasattr(current_user, 'id') else str(current_user)
        
        # Get all notes
        notes = get_all_notes_chroma(user_id)
        if not notes:
            raise HTTPException(status_code=404, detail="No notes found")
        
        # Create PDF in memory
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # PDF styling
        margin = 40
        line_height = 14
        y_position = height - margin
        c.setFont("Helvetica-Bold", 16)
        
        # Add title
        c.drawString(margin, y_position, "Your Notes")
        y_position -= line_height * 2
        c.setFont("Helvetica", 12)
        
        # Add each note to PDF
        for note in notes:
            timestamp = note.get('timestamp', '')
            text = note.get('text', '')
            
            # Format timestamp
            formatted_time = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M") if timestamp else "Unknown time"
            
            # Add timestamp
            c.setFont("Helvetica-Bold", 12)
            c.drawString(margin, y_position, formatted_time)
            y_position -= line_height
            
            # Add note text with wrapping
            c.setFont("Helvetica", 12)
            wrapped_text = textwrap.wrap(text, width=80)
            for line in wrapped_text:
                if y_position < margin:
                    c.showPage()
                    y_position = height - margin
                c.drawString(margin + 10, y_position, line)
                y_position -= line_height
            
            # Add space between notes
            y_position -= line_height / 2
        
        c.save()
        
        # Return PDF response
        buffer.seek(0)
        return Response(
            content=buffer.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=my_notes.pdf",
                "Content-Type": "application/pdf"
            }
        )
    
    except Exception as e:
        print(f"PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

# main.py - Add this new endpoint
@app.put("/notes/edit")
async def edit_user_note(
    request: EditNoteRequest, 
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if hasattr(current_user, 'id') else str(current_user)
    
    if not request.new_text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    success = await asyncio.to_thread(
        edit_note, 
        user_id, 
        request.note_id, 
        request.new_text
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return {"message": "Note updated successfully"}
@app.get("/health")
def health_check():
    return {"status": "healthy"}