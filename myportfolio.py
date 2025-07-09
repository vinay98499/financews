import requests
access_token='eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI3RkFMUjQiLCJqdGkiOiI2ODZjYTQ1NTViOTIzYTJlZmEwNWViMzgiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc1MTk1MDQyMSwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzUyMDEyMDAwfQ.f3rE3tLNIpa88wEuzzX0LJHt1D0bE-NRNUyp7Mm8imc'

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