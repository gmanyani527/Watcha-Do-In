import os
import json
import pandas as pd
import sqlalchemy as db
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from google_events import fetch_google_events
from schema import normalize_and_save


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

#print(f"Ticketmaster Keyword: {search_terms['ticketmaster']['keyword']}")
#print(f"Ticketmaster City: {search_terms['ticketmaster']['city']}")
#print(f"Google Events Query: {search_terms['google_events']['q']}")

google_events = fetch_google_events(search_terms['google_events']['q'])

engine = db.create_engine('sqlite:///events.db')
normalize_and_save(google_events, 'google', engine)

with engine.connect() as connection:
    query_result = connection.execute(db.text("SELECT * FROM events;")).fetchall()
    print(pd.DataFrame(query_result))
