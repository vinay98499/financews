import requests
access_token='eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI3RkFMUjQiLCJqdGkiOiI2ODYxNjViNmM5NTJjNDM5Y2YzZDhjYWQiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc1MTIxMzQ5NCwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzUxMjM0NDAwfQ.iqouroe7oRQM5vQFpTV9V7YUUI3mcUVdcqLrODHn-2c'


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