# import chromadb
# from chromadb.config import Settings
# from .embedding_service import get_embedding
# from app.models import NoteMetadata

# # Persistent client setup
# chroma_client = chromadb.PersistentClient(
#     path="./chroma_db",
#     settings=Settings(allow_reset=True)
# )

# def get_user_collection(user_id: str):
#     collection_name = f"user_{user_id}_notes"
#     return chroma_client.get_or_create_collection(
#         name=collection_name,
#         metadata={"hnsw:space": "cosine"},
#         embedding_function=None  # CRITICAL FIX
#     )

# def add_note(user_id: str, text: str) -> str:
#     collection = get_user_collection(user_id)
#     embedding = get_embedding(text).tolist()  # Convert to list
#     metadata = NoteMetadata(text=text).dict()
    
#     collection.add(
#         documents=[text],
#         embeddings=[embedding],
#         metadatas=[metadata],
#         ids=[metadata["id"]]
#     )
#     return metadata["id"]

# # def query_notes(user_id: str, query: str, n_results: int = 5):
# #     collection = get_user_collection(user_id)
# #     query_embedding = get_embedding(query).tolist()
    
# #     results = collection.query(
# #         query_embeddings=[query_embedding],
# #         n_results=n_results,
# #         include=["documents", "metadatas", "distances"]
# #     )
    
# #     # Format results
# #     return [
# #         {
# #             "text": doc,
# #             "id": meta["id"],
# #             "timestamp": meta["timestamp"],
# #             "similarity": 1 - dist  # Convert distance to similarity
# #         }
# #         for doc, meta, dist in zip(
# #             results["documents"][0],
# #             results["metadatas"][0],
# #             results["distances"][0]
# #         )
# #     ]


# # Keep this function focused on vector DB queries
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

# def has_notes(user_id: str) -> bool:
#     collection = get_user_collection(user_id)
#     return collection.count() > 0


# # Add to chroma_service.py
# # def get_all_notes_chroma(user_id: str) -> list[dict]:
# #     collection = get_user_collection(user_id)
# #     # This is a simplified approach - you'll need to implement 
# #     # actual retrieval of all notes from ChromaDB
# #     # This might involve querying with a neutral vector or 
# #     # accessing the collection directly
# #     results = collection.get(include=["documents", "metadatas"])
    
# #     return [
# #         {
# #             "text": doc,
# #             "id": meta["id"],
# #             "timestamp": meta["timestamp"]
# #         }
# #         for doc, meta in zip(results["documents"], results["metadatas"])
# #     ]


# def get_all_notes_chroma(user_id: str) -> list[dict]:
#     collection = get_user_collection(user_id)

#     try:
#         results = collection.get(include=["documents", "metadatas"])

#         documents = results.get("documents", [])
#         metadatas = results.get("metadatas", [])

#         return [
#             {
#                 "text": doc,
#                 "id": meta.get("id", ""),
#                 "timestamp": meta.get("timestamp", "")
#             }
#             for doc, meta in zip(documents, metadatas)
#         ]

#     except Exception as e:
#         # Log the error or raise it as needed
#         print(f"Error fetching notes: {e}")
#         return []










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

def query_notes(user_id: str, query: str, n_results: int = 5) -> list[dict]:
    collection = get_user_collection(user_id)
    query_embedding = get_embedding(query).tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
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