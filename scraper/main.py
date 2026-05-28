import sys
from datetime import datetime
from mongo import MongoDBClient
from s3 import S3Client
from bundestag import BundestagAPI


def run_scraper(mode="daily"):
    db = MongoDBClient()
    s3 = S3Client()
    api = BundestagAPI()

    start_date = None

    if mode == "daily":
        last_date = db.get_last_scrape_date()
        if last_date:
            print(f"[INFO] Last scraped entry is from {last_date}. Starting at this date.")
            start_date = last_date
        else:
            print("[INFO] No entries found. Skip.")
            return

    offset = 0
    limit = 100
    total_new_docs = 0

    while True:
        print(f"[INFO] Requesting API (Offset: {offset})")
        data = api.fetch_protocols(start_date=start_date, offset=offset, limit=limit, wahlperiode=21)

        if not data or "documents" not in data:
            print("[INFO] No further data found. Skip.")
            break

        documents = data["documents"]
        if not documents:
            print("[INFO] No documents found. Skip.")
            break

        for doc in documents:
            doc_id = str(doc.get("id"))

            if db.protocol_exists(doc_id) and mode == "daily":
                continue
            elif db.protocol_exists(doc_id):
                continue

            wahlperiode = doc.get("wahlperiode")
            sitzung = doc.get("nummer")
            datum = doc.get("datum")
            pdf_url = doc.get("pdf_url")

            if not pdf_url:
                continue

            pdf_bytes = api.download_pdf(pdf_url)
            if not pdf_bytes:
                continue

            s3_key = f"bundestag/wahlperiode_{wahlperiode}/protokoll_{sitzung}_{datum}.pdf"
            if s3.upload_bytes(pdf_bytes, s3_key):
                protocol_data = {
                    "protocol_id": doc_id,
                    "parliament": "Bundestag",
                    "wahlperiode": wahlperiode,
                    "sitzung": sitzung,
                    "datum": datum,
                    "vorgangsbezug": doc.get("vorgangsbezug", []),
                    "s3_storage": {
                        "bucket": s3.bucket_name,
                        "pdf_key": s3_key
                    },
                    "pipeline_status": {
                        "scraped_at": datetime.utcnow().isoformat(),
                        "embedding_status": "pending",
                        "embedded_at": None
                    }
                }
                db.save_protocol(protocol_data)
                total_new_docs += 1

        offset += limit

    print(f"[BEREIT] Scraper beendet. {total_new_docs} neue Protokolle verarbeitet.")


if __name__ == "__main__":
    run_mode = "daily"
    if len(sys.argv) > 1 and sys.argv[1] == "full":
        run_mode = "full"

    run_scraper(mode=run_mode)