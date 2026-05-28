from pymongo import MongoClient
import os


class MongoController:
    def __init__(self, collection_name="protocols"):
        """
        Initializes the connection to the MongoDB raw data store.
        """
        uri = os.environ["MONGO_URI"]
        db_name = os.environ["MONGO_DB_NAME"]
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def get_pending_protocols(self):
        """
        Fetches all documents that have been scraped but not yet processed
        by the embedding/vector ingestion pipeline.
        """
        return self.collection.find({"pipeline_status.embedding_status": "pending"}).to_list()

    def mark_as_completed(self, doc_id, timestamp_str):
        """
        Updates the pipeline flag of a document to prevent re-processing.
        Takes either a string representation or a BSON ObjectId.
        """
        self.collection.update_one(
            {"protocol_id": doc_id},
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