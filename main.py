import os
import json
from dotenv import load_dotenv
from ticketmaster import get_events
import ast
import pandas as pd
import sqlalchemy as db
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from google_events import fetch_google_events
from schema import normalize_and_save

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

title = r"""                                                                                                                                  
                                                                                                                                  
                             ___                ,---,                                                                             
                           ,--.'|_            ,--.' |                              ,---,                      ,--,                
         .---.             |  | :,'           |  |  :                            ,---.'|   ,---.      ,---,.,--.'|         ,---,  
        /. ./|             :  : ' :           :  :  :                            |   | :  '   ,'\   ,'  .' ||  |,      ,-+-. /  | 
     .-'-. ' |  ,--.--.  .;__,'  /     ,---.  :  |  |,--.  ,--.--.               |   | | /   /   |,---.'   ,`--'_     ,--.'|'   | 
    /___/ \: | /       \ |  |   |     /     \ |  :  '   | /       \            ,--.__| |.   ; ,. :|   |    |,' ,'|   |   |  ,"' | 
 .-'.. '   ' ..--.  .-. |:__,'| :    /    / ' |  |   /' :.--.  .-. |          /   ,'   |'   | |: ::   :  .' '  | |   |   | /  | | 
/___/ \:     ' \__\/: . .  '  : |__ .    ' /  '  :  | | | \__\/: . .         .   '  /  |'   | .; ::   |.'   |  | :   |   | |  | | 
.   \  ' .\    ," .--.; |  |  | '.'|'   ; :__ |  |  ' | : ," .--.; |         '   ; |:  ||   :    |`---'     '  : |__ |   | |  |/  
 \   \   ' \ |/  /  ,.  |  ;  :    ;'   | '.'||  :  :_:,'/  /  ,.  |         |   | '/  ' \   \  /           |  | '.'||   | |--'   
  \   \  |--";  :   .'   \ |  ,   / |   :    :|  | ,'   ;  :   .'   \        |   :    :|  `----'            ;  :    ;|   |/       
   \   \ |   |  ,     .-./  ---`-'   \   \  / `--''     |  ,     .-./         \   \  /                      |  ,   / '---'        
    '---"     `--`---'                `----'             `--`---'              `----'                        ---`-'               
                                                                                                                                  """

print(title)
print("*" * 60)
print("There's a hundred and four days of summer vacation ⋆｡♬ﾟ\n")
print("And school comes along just to end it ₊˚♬ﾟ\n")
print("So the annual problem for our generation ｡♪♫ ₊\n")
print("Is finding a good way to spend it ｡♪♫ ₊\n")
print("Like maybeee ♪♫ ₊˚...")
print("*" * 60)
print("Don't stress about strict keywords, dates, or locations!")
print("Just type what you're in the mood for naturally, and WATCHA DO-IN")
print("will figure out exactly what to look for.")
print("Example: 'I want to go dancing in NYC this weekend'")
print("-" * 60)

genai_key = os.getenv('GENAI_KEY')
genai.api_key = genai_key

client = genai.Client(
    api_key=genai_key,
)
engine = db.create_engine('sqlite:///events.db')

while True:
    
  user_input = input("\n What kind of events are you looking for? (or type 'q' to exit) ")

  if user_input.lower() == "q":
    print("\nThanks for using WATCHA DO-IN!")
    break

  print("\n[1/4] Analyzing user intent...")

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
  google_loc = search_terms['google_events']['location']

  tm_keywords = search_terms["ticketmaster"]["keyword"]
  tm_keyword = tm_keywords[0] if tm_keywords else "music"
  tm_city = search_terms["ticketmaster"]["city"]

  print(f"\n ↳ Translated into Google Events Query: {google_query}")
  print(f"\n ↳ Translated into Ticketmaster Query: {tm_keyword}")
  print("\n[2/4] Checking local cache for previous searches...")

  search_term_lower = google_query.lower()
  df = pd.DataFrame()

  with engine.connect() as connection:
    tables = db.inspect(engine).get_table_names()

    if 'events' in tables:
      query = db.text("SELECT * FROM events WHERE search_term = :term")
      result = connection.execute(query, {"term": search_term_lower}).fetchall()

      if result:
        df = pd.DataFrame(result)

  if not df.empty:
    print(f"Found {len(df)} saved events! Skipping APIs...")
    print("[3/4] Skipping Normalization")
  else:
    google_events = fetch_google_events(google_query)
    tm_response = get_events(tm_keyword, tm_city)
    tm_events = tm_response.get('_embedded', {}).get('events', []) if tm_response else []

    print(f"Found {len(google_events)} Google events and {len(tm_events)} Ticketmaster events!")
    print("[3/4] Normalizing data and caching to DB...")

    normalize_and_save(google_events, 'google', engine, google_query)
    normalize_and_save(tm_events, 'ticketmaster', engine, google_query)

    print("[4/4] Here are your personalized results!")
    print("=" * 60)

    with engine.connect() as connection:
      tables = db.inspect(engine).get_table_names()

      if 'events' in tables:
        query = db.text("SELECT * FROM events WHERE search_term = :term")
        query_result = connection.execute(query, {"term": search_term_lower}).fetchall()
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
      print(f" LINK: {row.get('link', 'N/A')}")
      print("-" * 60)
    
  cont = input("\n Would you like to search for something else? (y/n)")
  if cont.lower() != "y":
    print("\nThanks for using WATCHA DO-IN!!\n")
    break
