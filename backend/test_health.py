import urllib.request
try:
    resp = urllib.request.urlopen('http://localhost:8000/health', timeout=5)
    print(resp.read().decode())
except Exception as e:
    print(f'Error: {e}')