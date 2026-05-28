from datetime import datetime
from zoneinfo import ZoneInfo

from mongo import MongoDBClient
from bundestag import BundestagAPI
import time


def run_scraper():
    db = MongoDBClient()
    api = BundestagAPI()

    start_date = "2021-01-01"

    last_date = db.get_last_scrape_date()
    if last_date:
        print(f"[INFO] Last scraped entry is from {last_date}. Starting at this date.")
        start_date = last_date
    else:
        print("Doing full instead.")


    cursor = None
    total_new_docs = 0

    while True:
        data = api.fetch_protocols(start_date=start_date, cursor=cursor)

        if not data or "documents" not in data:
            print("[INFO] No further data found. Skip.")
            break

        documents = data["documents"]
        if not documents or len(documents) == 0:
            print("[INFO] No documents found. Skip.")
            break

        if "cursor" in data:
            cursor = data["cursor"]

        print(f"Batch importing {len(documents)} documents.")

        for doc in documents:
            doc_id = str(doc.get("id"))

            if db.protocol_exists(doc_id):
                continue

            angereicherte_vorgaenge = []
            flache_vorgaenge = doc.get("vorgangsbezug", [])

            for v in flache_vorgaenge:
                v_id = v.get("id")
                if not v_id:
                    continue

                details = api.fetch_vorgang_details(v_id)

                if details:
                    vorgangs_detail = {
                        "id": v_id,
                        "titel": details.get("titel"),
                        "vorgangstyp": details.get("vorgangstyp"),
                        "sachgebiet": details.get("sachgebiet", []),
                        "beratungsstand": details.get("beratungsstand"),
                        "initialtive": details.get("initialtive", []),
                        "abstract": details.get("abstract")
                    }
                    angereicherte_vorgaenge.append(vorgangs_detail)
                else:
                    angereicherte_vorgaenge.append(v)

            protocol_data = {
                "protocol_id": doc_id,
                "meta_data": {
                    "vorgangsbezug_anzahl": doc.get("vorgangsbezug_anzahl"),
                    "wahlperiode": doc.get("wahlperiode"),
                    "vorgangsbezug": angereicherte_vorgaenge,
                    "herausgeber": doc.get("herausgeber"),
                },
                "text": doc.get("text"),
                "pipeline_status": {
                    "scraped_at": datetime.now(ZoneInfo("Europe/Berlin")).strftime("%Y-%m-%d"),
                    "embedding_status": "pending",
                    "embedded_at": None
                }
            }
            db.save_protocol(protocol_data)
            total_new_docs += 1

    db.client.close()


def run_scraper_loop():
    while True:
        run_scraper()
        time.sleep(3600)

if __name__ == "__main__":
    run_scraper()