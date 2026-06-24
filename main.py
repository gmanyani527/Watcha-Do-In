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

print("*" * 60)
print("Welcome to WATCHA DO-IN!")
print("*" * 60)

user_input = input("\n What kind of events are you looking for? ")
print("\n[1/4] Analyzing user intent...")

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
    contents=user_input,
)

events = response.text
search_terms = json.loads(events)
google_query = search_terms['google_events']['q']

print(f"/n ↳ Translated into Search Query: {google_query}")
print("[2/4] Fetching live data from Google Events API")

#print(f"Ticketmaster Keyword: {search_terms['ticketmaster']['keyword']}")
#print(f"Ticketmaster City: {search_terms['ticketmaster']['city']}")
#print(f"Google Events Query: {search_terms['google_events']['q']}")

google_events = fetch_google_events(search_terms['google_events']['q'])
print(f"Found {len(google_events)} events!")
print("[3/4] Normalizing data and caching to DB...")

engine = db.create_engine('sqlite:///events.db')
normalize_and_save(google_events, 'google', engine)

print("[4/4] Here are your personalized results!")
print("=" * 60)

with engine.connect() as connection:
    query_result = connection.execute(db.text("SELECT * FROM events;")).fetchall()
    df = pd.DataFrame(query_result)

    if df.empty:
      print("No events matched your search. Try another prompt!")
    else:
      for index, row in df.iterrows():
        date_info = str(row['date'])
        try:
          date_dict = ast.literal_eval(date_info)
          if isinstance(date_dict, dict):
            date_info = date_dict.get('when', date_info)
        except (ValueError, SyntaxError):
          pass

        print(f" EVENT: {row['title']}")
        print(f" WHEN:  {date_info}")
        print(f" WHERE: {row['address']}")
        print("-" * 60)

print("Thanks for using WATCHA DO-IN")