import requests

url = "https://api.sarvam.ai/text-to-speech"

payload = {
    "text": "foo",
    "target_language_code": "bn-IN"
}
headers = {
    "api-subscription-key": "f050c5ca-f2f6-4c5b-807f-c8f1c3a74d14",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())