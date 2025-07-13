import chromadb

# Use the new PersistentClient interface
client = chromadb.PersistentClient(path="./chroma_db")  # update path if needed

def list_collections():
    print("📦 Available Collections:")
    collections = client.list_collections()
    if not collections:
        print("⚠️  No collections found.")
        return

    for col in collections:
        print(f" - {col.name}")
        collection = client.get_collection(name=col.name)

        try:
            # CRITICAL FIX: Include embeddings in the get() call
            data = collection.get(include=["documents", "metadatas", "embeddings"])
        except Exception as e:
            print(f"   ⚠️ Failed to fetch data: {e}")
            continue
        l = len(data.get('ids', []))
        print(f"   ➤ Total items: {l}")
        for i in range(l):
            if data.get("ids"):
                print(f"   ➤ Sample ID: {data['ids'][i]}")

                # Safe check for document
                docs = data.get("documents")
                print(f"   ➤ Sample Doc: {docs[i]}")  # Fixed: was docs[1], should be docs[0]
            

                # Safe check for embedding
                embeds = data.get("embeddings")
                print(f"   ➤ Embedding (truncated): {str(embeds[i])[:60]}...")
                print(f"   ➤ Embedding dimension: {len(embeds[i])}")

                    
                # Check metadata
                metas = data.get("metadatas")
                print(f"   ➤ Sample Metadata: {metas[i]}")
            print("\n")

        

if __name__ == "__main__":
    list_collections()