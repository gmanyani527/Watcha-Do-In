import pandas as pd
pd.set_option('display.max_colwidth', None)
import sqlalchemy as db
from main import google_events

def normalize_and_save(events, source, engine):
    if not events:
      print("No events found.")
      return

    cleaned_events = []

    for event in events:
      if source == 'google':
        cleaned_events = {
          "title": event.get("title")
          "date": str(event.get("date"))
,
          "address": str(event.get("address"))
          "description":         }
if not google_events:
    print("No events found.")
else:
    df = pd.DataFrame.from_dict(google_events)
    engine = db.create_engine('sqlite:///events.db')
    df.to_sql('google_events', con=engine, if_exists='replace', index=False)

    with engine.connect() as connection:
        query_result = connection.execute(db.text("SELECT * FROM google_events;")).fetchall()
        print(pd.DataFrame(query_result))
