import chromadb
from chromadb.config import Settings
from .embedding_service import get_embedding
from app.models import NoteMetadata
from datetime import datetime

# Persistent client setup
chroma_client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(allow_reset=True, persist_directory="./chroma_db")
)

def get_user_collection(user_id: str):
    collection_name = f"user_{user_id}_notes"
    return chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
        embedding_function=None  # CRITICAL FIX
    )


def add_note(user_id: str, text: str) -> str:
    collection = get_user_collection(user_id)
    embedding = get_embedding(text).tolist()
    # Create metadata instance (will generate new ID/timestamp)
    metadata = NoteMetadata(text=text)  # Don't call .dict() here
    
    collection.add(
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata.dict()],  # Call .dict() HERE
        ids=[metadata.id]
    )
    return metadata.id



# def query_notes(user_id: str, query: str, n_results: int = 5) -> list[dict]:
#     collection = get_user_collection(user_id)
#     query_embedding = get_embedding(query).tolist()
    
#     results = collection.query(
#         query_embeddings=[query_embedding],
#         n_results=n_results,
#         include=["documents", "metadatas", "distances"]
#     )
    
#     return [
#         {
#             "text": doc,
#             "id": meta["id"],
#             "timestamp": meta["timestamp"],
#             "similarity": 1 - dist
#         }
#         for doc, meta, dist in zip(
#             results["documents"][0],
#             results["metadatas"][0],
#             results["distances"][0]
#         )
#     ]




def query_notes(user_id: str, query: str) -> list[dict]:
    collection = get_user_collection(user_id)
    query_embedding = get_embedding(query).tolist()
    
    # Query ALL documents in the collection
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=collection.count(),  # Get all documents
        include=["documents", "metadatas", "distances"]
    )
    
    # Filter results where similarity > 0.5 (50%)
    return [
        {
            "text": doc,
            "id": meta["id"],
            "timestamp": meta["timestamp"],
            "similarity": 1 - dist
        }
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )
        if (1 - dist) > 0.5  # Similarity threshold filter
    ]




def has_notes(user_id: str) -> bool:
    try:
        collection = get_user_collection(user_id)
        return collection.count() > 0
    except Exception as e:
        print(f"Error checking if user has notes: {e}")
        return False

def get_all_notes_chroma(user_id: str) -> list[dict]:
    try:
        print(f"Getting collection for user: {user_id}")
        collection = get_user_collection(user_id)
        
        # Check if collection has any notes
        count = collection.count()
        print(f"Collection count: {count}")
        
        if count == 0:
            return []
        
        # Get all documents from the collection
        results = collection.get(include=["documents", "metadatas"])
        
        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])
        
        print(f"Retrieved {len(documents)} documents from ChromaDB")
        
        # Format the results
        formatted_notes = []
        for doc, meta in zip(documents, metadatas):
            if meta:  # Ensure metadata exists
                formatted_note = {
                    "text": doc,
                    "id": meta.get("id", "unknown"),
                    "timestamp": meta.get("timestamp", "")
                }
                formatted_notes.append(formatted_note)
                print(f"Note: {doc[:50]}... (ID: {meta.get('id', 'unknown')})")
        
        return formatted_notes
        
    except Exception as e:
        print(f"Error fetching notes for user {user_id}: {e}")
        import traceback
        traceback.print_exc()
        return []


def delete_note(user_id: str, note_id: str) -> bool:
    try:
        collection = get_user_collection(user_id)
        collection.delete(ids=[note_id])
        return True
    except Exception as e:
        print(f"Error deleting note: {e}")
        return False
    


def edit_note(user_id: str, note_id: str, new_text: str) -> bool:
    try:
        collection = get_user_collection(user_id)
        
        # Check if note exists
        existing = collection.get(ids=[note_id], include=["metadatas"])
        if not existing['ids']:
            return False
            
        # Update metadata and embedding
        old_metadata = existing['metadatas'][0]
        new_metadata = old_metadata.copy()
        new_metadata['text'] = new_text
        new_metadata['timestamp'] = datetime.now().isoformat()
        
        new_embedding = get_embedding(new_text).tolist()
        
        collection.update(
            ids=[note_id],
            documents=[new_text],
            embeddings=[new_embedding],
            metadatas=[new_metadata]
        )
        return True
    except Exception as e:
        print(f"Error editing note: {e}")
        return False
    
def count_note(user_id:str) -> int:
    try:
        collection = get_user_collection(user_id)
        count = collection.count()
        return count
    except Exception as e:
        print(f"Could not access the collection: {e}")
        return 0