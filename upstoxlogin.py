import requests

url = 'https://api.upstox.com/v2/login/authorization/token'
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded',
}

data = {
    'code': '{your_code}',
    'client_id': '46fbe7a5-3171-4e6d-b692-fad29b0b6e81',
    'client_secret': '46fbe7a5-3171-4e6d-b692-fad29b0b6e81',
    'redirect_uri': 'https://127.0.0.1:5000/',
    'grant_type': 'authorization_code',
}
response = requests.post(url, headers=headers, data=data)

print(response.status_code)
print(response.json())