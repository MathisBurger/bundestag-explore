import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


class MongoDBClient:
    def __init__(self):
        uri = os.environ["MONGO_URI"]
        db_name = os.environ["MONGO_DB_NAME"]

        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db["protocols"]
        self.collection.create_index("protocol_id", unique=True)

    def protocol_exists(self, protocol_id):
        return self.collection.find_one({"protocol_id": str(protocol_id)}) is not None

    def save_protocol(self, protocol_data):
        self.collection.update_one(
            {"protocol_id": protocol_data["protocol_id"]},
            {"$set": protocol_data},
            upsert=True
        )

    def get_last_scrape_date(self):
        last_doc = self.collection.find_one(
            {"meta_data.herausgeber": "BT"},
            sort=[("pipeline_status.scraped_at", -1)]
        )
        return last_doc["pipeline_status"]["scraped_at"] if last_doc else None