import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TICKETMASTER_API_KEY")

def get_events(keyword, city):
  url = "https://app.ticketmaster.com/discovery/v2/events.json"

  params = {
    "apikey": API_KEY,
    "keyword": keyword,
    "city": city,
    "size": 5
  }

  response = requests.get(url, params=params)

  if response.status_code == 200:
    return response.json()
  else:
    print("Error:", response.status_code)
    return None
  
events = get_events("concert", "New York")
if events and "_embedded" in events:
  for event in events["_embedded"]["events"]:
    print(f"Name: {event['name']}")
    print(f"Date: {event['dates']['start']['localDate']}")
    print(f"Venue: {event['_embedded']['venues'][0]['name']}")
    print(f"City: {event['_embedded']['venues'][0]['city']['name']}")
    print(f"URL: {event['url']}")
    print("-" * 50)
