from sentence_transformers import SentenceTransformer

# Load model once at startup
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str) -> list:
    return model.encode(text)