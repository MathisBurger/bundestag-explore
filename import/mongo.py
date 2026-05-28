# mongo.py
from pymongo import MongoClient
from bson.objectid import ObjectId


class MongoController:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="parlaments_data", collection_name="protocols"):
        """
        Initializes the connection to the MongoDB raw data store.
        """
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def get_pending_protocols(self):
        """
        Fetches all documents that have been scraped but not yet processed
        by the embedding/vector ingestion pipeline.
        """
        return self.collection.find({"pipeline_status.embedding_status": "pending"})

    def mark_as_completed(self, doc_id, timestamp_str):
        """
        Updates the pipeline flag of a document to prevent re-processing.
        Takes either a string representation or a BSON ObjectId.
        """
        if isinstance(doc_id, str):
            doc_id = ObjectId(doc_id)

        self.collection.update_one(
            {"_id": doc_id},
            {
                "$set": {
                    "pipeline_status.embedding_status": "completed",
                    "pipeline_status.embedded_at": timestamp_str
                }
            }
        )
        print(f"MongoDB Document {doc_id} successfully marked as completed.")

    def close(self):
        """Closes the active database connection safely."""
        self.client.close()