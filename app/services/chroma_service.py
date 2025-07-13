import chromadb
from chromadb.config import Settings
from .embedding_service import get_embedding
from app.models import NoteMetadata

# Persistent client setup
chroma_client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(allow_reset=True)
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
    embedding = get_embedding(text).tolist()  # Convert to list
    metadata = NoteMetadata(text=text).dict()
    
    collection.add(
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata],
        ids=[metadata["id"]]
    )
    return metadata["id"]

def query_notes(user_id: str, query: str, n_results: int = 5):
    collection = get_user_collection(user_id)
    query_embedding = get_embedding(query).tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    # Format results
    return [
        {
            "text": doc,
            "id": meta["id"],
            "timestamp": meta["timestamp"],
            "similarity": 1 - dist  # Convert distance to similarity
        }
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )
    ]

def has_notes(user_id: str) -> bool:
    collection = get_user_collection(user_id)
    return collection.count() > 0