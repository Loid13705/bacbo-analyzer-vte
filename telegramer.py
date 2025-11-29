# telegramer.py
import configparser
import requests

class Telegramer:
    def __init__(self, config):
        self.config = config
        self.token = config.get("telegram", "token", fallback="").strip()
        self.chat_id = config.get("telegram", "chat_id", fallback="").strip()

    def send_message(self, text):
        if not self.token or not self.chat_id or "SEU_TOKEN" in self.token:
            return False
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        try:
            r = requests.post(url, data={"chat_id": self.chat_id, "text": text}, timeout=6)
            return r.status_code == 200
        except Exception:
            return False
