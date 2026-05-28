from datetime import datetime
import time
from zoneinfo import ZoneInfo

from ingestion import create_client, ingest_data, initialize_hybrid_collection
from chunking import get_all_chunks_to_import
from mongo import MongoController
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    client = create_client()
    db = MongoController()
    initialize_hybrid_collection(client, "bundestag_collection")
    while True:
        pending_docs = db.get_pending_protocols()
        if len(pending_docs) > 0:
            for doc in pending_docs:
                print(f"Processing document {doc['protocol_id']}")
                chunks = get_all_chunks_to_import(doc)
                print("Generated chunks")
                ingest_data(client, chunks, "bundestag_collection")
                print("Moving on to next document.")
                db.mark_as_completed(doc_id=doc['protocol_id'], timestamp_str=datetime.now(ZoneInfo("Europe/Berlin")).strftime("%Y-%m-%d"))

        time.sleep(3600)