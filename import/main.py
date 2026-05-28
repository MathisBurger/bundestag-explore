import time

from ingestion import create_client, ingest_data, initialize_hybrid_collection
from chunking import get_all_chunks_to_import
from mongo import MongoController

if __name__ == '__main__':
    client = create_client()
    db = MongoController()
    initialize_hybrid_collection(client, "bundestag_collection")
    while True:
        pending_docs = db.get_pending_protocols()
        if len(pending_docs) > 0:
            for doc in pending_docs:
                chunks = get_all_chunks_to_import(doc)
                ingest_data(client, chunks, "bundestag_collection")

        time.sleep(3600)