import time

from assistant_mes_droits.data_processing.main import process_publications
from assistant_mes_droits.vector_store.vector_store import PublicationVectorStore

if __name__ == "__main__":
    store = PublicationVectorStore()

    publications = process_publications()

    store.add_publications(publications)

    time.sleep(30)

    # Search
    results = store.search("Permis de conduire")
    for doc in results:
        print(doc.page_content)
