import requests
from utils import SecretsUtil

access_token = SecretsUtil.get_token()


url = 'https://api.upstox.com/v2/user/get-funds-and-margin?segment=SEC'

headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {access_token}'
}

response = requests.get(url, headers=headers)

print(response.status_code)
print(response.json())


url = 'https://api.upstox.com/v2/logout'
headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {access_token}'
}

response = requests.delete(url, headers=headers)

print(response.status_code)
print(response.json())



url = 'https://api.upstox.com/v2/charges/brokerage'
headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {access_token}'
}

params = {
    'instrument_token': 'NSE_EQ|INE669E01016',
    'quantity': '10',
    'product': 'D',
    'transaction_type': 'BUY',
    'price': '13.7'
}

response = requests.get(url, headers=headers, params=params)

print(response.json())



access_token = SecretsUtil.get_token()


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
