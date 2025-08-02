import requests
import json

url = "http://localhost:8000/requirement/stream"
headers = {
    "Content-Type": "application/json"
}
data = {
    "description": "测试需求"
}

response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)

print(f"Status Code: {response.status_code}")
for chunk in response.iter_content(chunk_size=1024):
    if chunk:
        print(chunk.decode('utf-8'), end='')