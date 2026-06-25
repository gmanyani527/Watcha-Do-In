import os
import requests

def get_events(keyword,city):
  api_key = os.getenv("TICKETMASTER_API_KEY")
  url = "https://app.ticketmaster.com/discovery/v2/events.json"

  params = {
    "apikey": api_key,
    "keyword": keyword,
    "city": city,
    "size": 5
  }
  response = requests.get(url, params=params)
  if response.status_code == 200:
    return response.json()
  print("Error:", response.status_code)
  return None