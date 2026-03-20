# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/services/m365/graph_client.py
import requests


class GraphClient:

    BASE_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self, access_token):
        self.token = access_token

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def get_profile(self):
        url = f"{self.BASE_URL}/me"
        return requests.get(url, headers=self._headers()).json()

    def list_messages(self):
        url = f"{self.BASE_URL}/me/messages"
        return requests.get(url, headers=self._headers()).json()

