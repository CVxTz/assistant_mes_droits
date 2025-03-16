from unittest.mock import MagicMock, patch

import pytest

from assistant_mes_droits.data_processing.models import PublicationModel
from assistant_mes_droits.vector_store.vector_store import PublicationVectorStore


@pytest.fixture
def mock_vector_store():
    with patch("pymongo.MongoClient"), patch(
        "langchain_google_genai.GoogleGenerativeAIEmbeddings"
    ), patch("langchain_mongodb.MongoDBAtlasVectorSearch"), patch(
        "assistant_mes_droits.vector_store.vector_store.PublicationVectorStore._create_index"
    ):  # Mocked but no variable
        # Create instance with all dependencies mocked
        store = PublicationVectorStore()

        # Mock methods directly on the instance
        store.vector_store = MagicMock()
        store.vector_store.add_documents = MagicMock()
        store.vector_store.delete = MagicMock(return_value=True)
        store.vector_store.similarity_search = MagicMock()

        return store


def test_add_publications(mock_vector_store):
    publication = PublicationModel(title="Test", paragraphs=["Content"])
    mock_vector_store.add_publications([publication])
    mock_vector_store.vector_store.add_documents.assert_called_once()


def test_delete_publication(mock_vector_store):
    result = mock_vector_store.delete_publication("test_id")
    mock_vector_store.vector_store.delete.assert_called_once_with(ids=["test_id"])
    assert result is True


def test_search(mock_vector_store):
    mock_vector_store.search("query")
    mock_vector_store.vector_store.similarity_search.assert_called_once_with(
        "query", k=5
    )
