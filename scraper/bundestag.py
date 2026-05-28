import os
import requests
from dotenv import load_dotenv

load_dotenv()


class BundestagAPI:
    def __init__(self):
        self.api_key = os.environ["BUNDESTAG_API_KEY"]
        self.base_url = "https://search.dip.bundestag.de/api/v1/plenarprotokoll"

    def fetch_protocols(self, start_date=None, offset=0, limit=50, wahlperiode):
        params = {
            "f.zuordnung": "BT",
            "format": "json",
            "apikey": self.api_key,
            "limit": limit,
            "f.wahlperiode": wahlperiode,
            "offset": offset
        }

        if start_date:
            params["f.datum.start"] = start_date

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[API ERROR] Error while requesting bundestag(Offset {offset}): {e}")
            return None

    def download_pdf(self, url):
        try:
            res = requests.get(url)
            res.raise_for_status()
            return res.content
        except Exception as e:
            print(f"[API ERROR] Could not download PDF ({url}): {e}")
            return None