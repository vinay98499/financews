import requests
import os

# Read secrets from local JSON file
import json as _json

secrets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'secrets.json')
if not os.path.exists(secrets_path):
    secrets_path = os.path.join(os.path.dirname(__file__), 'secrets.json')

if os.path.exists(secrets_path):
    with open(secrets_path, 'r') as f:
        secrets = _json.load(f)
else:
    secrets = {}

access_token = secrets.get('UPSTOX_ACCESS_TOKEN')

url = 'https://api.upstox.com/v3/historical-candle/NSE_EQ%7CINE848E01016/days/1/2025-01-02/2025-01-01'
headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {access_token}'
}

response = requests.get(url, headers=headers)

# Check the response status
if response.status_code == 200:
    # Do something with the response data (e.g., print it)
    print(response.json())
else:
    # Print an error message if the request was not successful
    print(f"Error: {response.status_code} - {response.text}")
