import urllib.request
import json

base = "http://localhost:8000/api/v1"

endpoints = [
    "/health",
    "/sectors",
    "/companies",
    "/prices/latest",
    "/fx/rates",
    "/commodities/prices",
    "/news",
    "/anomalies",
]

for ep in endpoints:
    try:
        resp = urllib.request.urlopen(f"{base}{ep}", timeout=5)
        data = resp.read().decode()
        print(f"GET {ep}: {resp.status} - {data[:200]}")
    except Exception as e:
        print(f"GET {ep}: ERROR - {e}")