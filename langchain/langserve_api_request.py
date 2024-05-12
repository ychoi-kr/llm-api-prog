import requests

response = requests.post(
    "http://localhost:8000/lyrics/invoke",
    json={'input': {'topic': 'LLM'}}
)

print(response.json())
