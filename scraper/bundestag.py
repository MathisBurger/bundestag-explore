import os
import requests
from dotenv import load_dotenv

load_dotenv()


class BundestagAPI:
    def __init__(self):
        self.api_key = os.environ["BUNDESTAG_API_KEY"]
        self.base_url = "https://search.dip.bundestag.de/api/v1/plenarprotokoll-text"

    def fetch_vorgang_details(self, vorgang_id):
        url = f"https://search.dip.bundestag.de/api/v1/vorgang/{vorgang_id}"
        params = {"format": "json", "apikey": self.api_key}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None

    def fetch_protocols(self, start_date=None, cursor=None, wahlperiode=21):
        params = {
            "f.zuordnung": "BT",
            "format": "json",
            "apikey": self.api_key,
            "f.wahlperiode": wahlperiode,
        }

        if cursor:
            params["cursor"] = cursor

        if start_date:
            params["f.datum.start"] = start_date

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except:
            return None