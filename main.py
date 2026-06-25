import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from ticketmaster import get_events
from pydantic import BaseModel

load_dotenv()
class TicketmasterParams(BaseModel):
    keyword: list[str]
    classificationName: str
    city: str
    stateCode: str
    localStartDateTime: list[str]


class GoogleEventsParams(BaseModel):
    q: str
    location: str


class EventSearch(BaseModel):
    ticketmaster: TicketmasterParams
    google_events: GoogleEventsParams



genai_key = os.getenv('GENAI_KEY')
genai.api_key = genai_key

client = genai.Client(
    api_key=genai_key,
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=EventSearch.model_json_schema()
    ),
    contents=(
        "I like dancing and learning new cultures "
        "through music and I live in New York"),
)

events = response.text
search_terms = json.loads(events)

print(f"Ticketmaster Keyword: {search_terms['ticketmaster']['keyword']}")
print(f"Ticketmaster City: {search_terms['ticketmaster']['city']}")
print(f"Google Events Query: {search_terms['google_events']['q']}")

ticketmaster_keywords = search_terms["ticketmaster"]["keyword"]
ticketmaster_city = search_terms["ticketmaster"]["city"]

ticketmaster_results = get_events(
  ticketmaster_keywords[0],
  ticketmaster_city
)
if ticketmaster_results and "_embedded" in ticketmaster_results:
  for event in ticketmaster_results["_embedded"]["events"]:
    print(f"Name: {event['name']}")
    print(f"Date: {event['dates']['start'].get('localDate', 'N/A')}")
    print(f"Venue: {event['_embedded']['venues'][0]['names']}")
    print(f"City: {event['_embedded']['venues'][0]['city']['name']}")
    print(f"URL: {event['url']}")
else:
  print("No Ticketmaster events found")