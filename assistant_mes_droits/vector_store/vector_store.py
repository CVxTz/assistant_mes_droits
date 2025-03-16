import os
from datetime import UTC, datetime
from pathlib import Path
from typing import List
from uuid import uuid4

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient, errors
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm

from assistant_mes_droits.logger import logger
from assistant_mes_droits.vector_store.embedding import GeminiAPIEmbeddings

# Load environment variables from root .env
env_path = Path(__file__).resolve().parents[2] / ".env"
if env_path.is_file():
    load_dotenv(dotenv_path=env_path)


class PublicationVectorStore:
    """MongoDB vector store for PublicationModel objects with Gemini embeddings."""

    def __init__(
        self,
        db_name: str = "assistant_mes_droits",
        collection_name: str = "publications",
        index_name: str = "publication_vector_index",
    ):
        self.client = MongoClient(os.getenv("MONGO_CONNECTION"))
        self.db_name = db_name
        self.collection_name = collection_name
        self.index_name = index_name

        self.embeddings = GeminiAPIEmbeddings(
            model="text-embedding-004",
        )

        self.collection = self.client[self.db_name][self.collection_name]
        self.vector_store = MongoDBAtlasVectorSearch(
            collection=self.collection,
            embedding=self.embeddings,
            index_name=self.index_name,
        )
        self._create_index()

    def _create_index(self):
        """Create vector search index if it doesn't exist, skip if already exists."""
        try:
            self.vector_store.create_vector_search_index(dimensions=768)
        except errors.OperationFailure as e:
            if e.code == 68:  # IndexAlreadyExists error code
                logger.info(
                    f"Index {self.index_name} already exists, skipping creation"
                )
            else:
                raise

    def add_publications(self, publications: List) -> None:
        """
        Add multiple publications to the vector store with retries and batching.

        Args:
            publications: List of PublicationModel instances
        """
        current_time = datetime.now(UTC)
        documents = []
        ids = []

        for pub in publications:
            pub_data = pub.dict()
            if not pub_data.get("id"):
                pub_data["id"] = str(uuid4())
            # Add timestamp metadata for cleanup
            pub_data["date_added"] = current_time
            documents.append(
                Document(page_content=pub.to_markdown(), metadata=pub_data)
            )
            ids.append(pub_data["id"])

        batch_size = 20
        for i in tqdm(range(0, len(documents), batch_size)):
            batch_docs = documents[i : i + batch_size]
            batch_ids = ids[i : i + batch_size]
            self._add_batch_with_retry(batch_docs, batch_ids)

        # Cleanup old documents after successful insertion
        self._delete_old_documents(current_time)

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=2, min=30, max=120),
    )
    def _add_batch_with_retry(self, batch_docs: List[Document], batch_ids: List[str]):
        """Retry a batch insertion up to 10 times with exponential backoff."""
        # Delete existing documents first to prevent conflicts
        if batch_ids:
            self.vector_store.delete(ids=batch_ids)
        # Insert new documents
        self.vector_store.add_documents(
            documents=batch_docs, ids=batch_ids, batch_size=len(batch_docs)
        )

    def _delete_old_documents(self, cutoff_time: datetime):
        """Delete documents older than given timestamp in batches."""
        logger.info("Starting gradual deletion of old documents...")
        collection = self.client[self.db_name][self.collection_name]
        query = {"metadata.date_added": {"$lt": cutoff_time}}

        batch_size = 200
        total_deleted = 0

        while True:
            # Get a batch of old document IDs
            cursor = collection.find(
                query, projection={"_id": 1}, batch_size=batch_size
            ).limit(batch_size)
            ids_to_delete = [doc["_id"] for doc in cursor]

            if not ids_to_delete:
                break  # No more documents to delete

            # Delete batch
            result = collection.delete_many({"_id": {"$in": ids_to_delete}})
            deleted_count = result.deleted_count
            total_deleted += deleted_count
            logger.info(
                f"Deleted {deleted_count} old documents in this batch. Total deleted: {total_deleted}"
            )

        logger.info(f"Completed old documents cleanup. Total deleted: {total_deleted}")

    def delete_publication(self, publication_id: str) -> bool:
        """
        Delete a publication by ID.

        Args:
            publication_id: ID of the publication to delete
        """
        return self.vector_store.delete(ids=[publication_id])

    def search(self, query: str, k: int = 5) -> List[Document]:
        """
        Search publications by semantic similarity.

        Args:
            query: Search query
            k: Number of results to return
        """
        return self.vector_store.similarity_search(query, k=k)
