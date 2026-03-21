import threading
import requests
import time
import os

def keep_alive():
    url = os.getenv("RAILWAY_URL", "")
    if not url:
        return
    while True:
        try:
            requests.get(f"{url}/health")
        except:
            pass
        time.sleep(300)  # ping every 5 minutes

def start_keep_alive():
    t = threading.Thread(target=keep_alive, daemon=True)
    t.start()