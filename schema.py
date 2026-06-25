import pandas as pd
import sqlalchemy as db

def normalize_and_save(events, source, engine):
    if not events:
      print("No events found.")
      return

    cleaned_events = []

    for event in events:
      if source == 'google':
        cleaned_event = {
          "title": event.get("title"),
          "date": str(event.get("date")),
          "address": str(event.get("address")),
          "description": event.get("description")       
          }
        cleaned_events.append(cleaned_event)
      else:
        continue

    df = pd.DataFrame.from_dict(cleaned_events)
    df.to_sql('events', con=engine, if_exists='replace', index=False)


