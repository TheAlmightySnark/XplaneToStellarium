
from urllib.parse import urlencode
import requests

r = requests.post("http://localhost:8090/api/location/setlocationfields", params=urlencode({'latitude': '52.00', 'longitude':'3.0'}).encode())
print(r.status_code, r.reason)
print(r.url)
print(r.text)
