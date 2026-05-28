import time

from ingestion import create_client, ingest_data, initialize_hybrid_collection
from chunking import get_all_chunks_to_import

if __name__ == '__main__':
    client = create_client()
    initialize_hybrid_collection(client, "bundestag_collection")
    while True:
        chunks = get_all_chunks_to_import()
        if len(chunks) > 0:
            ingest_data(client, chunks, "bundestag_collection")

        time.sleep(3600)