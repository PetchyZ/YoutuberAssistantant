import chromadb
from chromadb.utils import embedding_functions

class VectorService:
    def __init__(self):
        # Create Persistent Client or In-Memory Client
        self.client = chromadb.Client()

        # Use Default Embedding Function or HuggingFace / Sentence Transformers
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

        # Create or pull Collection for Channels
        self.collection = self.client.get_or_create_collection(
            name="youtube_channels",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"} # Use Cosine Similarity followed by Research Criteria  
        )

    def upsert_channel_profile(self, channel_id: str, profile_text: str, metadata: dict):
        """
        Save and update Profile Embedding channel in vector DB
        """
        clean_metadata = {
            "channel_id" : channel_id,
            "channel_title" : str(metadata.get("channel_title", metadata.get("title", "Unknown"))),
            "category" : str(metadata.get("category", "")),
            "subscriber_band" : str(metadata.get("subscriber_band", "")),
            "avg_views" : int(metadata.get("avg_views", 0))
        }

        self.collection.upsert(
            documents = [profile_text.strip()],
            metadatas = [clean_metadata],
            ids=[channel_id]
        )

        # เช็กจำนวนข้อมูลทั้งหมดใน Collection ที่กำลังใช้งาน
        count = self.collection.count()
        print(f"Total channels in DB: {count}")

        # ลองดึงข้อมูลทั้งหมดมาดู
        all_data = self.collection.get()
        print("Available IDs:", all_data.get("ids"))

    def find_similar_channels(self, profile_text: str, top_k: int = 5):
        """
        Find lookalike channels by Cosine Similarity score 
        """
        results = self.collection.query(
            query_texts=[profile_text],
            n_results=top_k,
            include=["metadatas", "documents", "distances"]
        )

        similar_channels = []

        # convert ChromaDB structure to List of Dictionary
        if results and results.get("ids") and len(results["ids"][0]) > 0:
            ids = results["ids"][0]
            metadatas = results["metadatas"][0]
            documents = results["documents"][0]
            distances = results["distances"][0]

            for i in range(len(ids)):
                distance = distances[i]
                # Convert Cosine Distance to Similarity Score (0 - 1)
                similarity_score = round(max(0.0, 1.0 - distance), 2)
                metadata = metadatas[i] if metadatas else {}

                similar_channels.append({
                    "channel_id": ids[i],
                    "channel_title": metadata.get("channel_title", "Unknown Channel"),
                    "category" : metadata.get("category", ""),
                    "subscriber_band" : metadata.get("subscriber_band", ""),
                    "avg_views" : metadata.get("avg_views", 0),
                    "similarity_score" : similarity_score, 
                    "profile_summary" : documents[i]
                })

        return similar_channels
