import urllib.request

ep = "/sectors"
try:
    resp = urllib.request.urlopen(f"http://localhost:8000/api/v1{ep}", timeout=3)
    data = resp.read().decode()
    print(f"GET {ep}: {resp.status} - {data[:300]}")
except Exception as e:
    print(f"GET {ep}: ERROR - {type(e).__name__}: {e}")