import requests
import json

url = "http://127.0.0.1:8000/api/v1/feedback/"
data = {
    "rating": 5,
    "comment": "Great app!",
    "feature_request": "Add support for more file types"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, data=json.dumps(data), headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")