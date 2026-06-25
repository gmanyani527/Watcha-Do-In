import pandas as pd
import sqlalchemy as db

def normalize_and_save(events, source, engine, search_term):
    if not events:
      print("No events found.")
      return

    cleaned_events = []

    for event in events:
      if source == 'google':
        cleaned_event = {
          "search_term": search_term.lower(),
          "source": "Google Events",
          "title": event.get("title"),
          "date": str(event.get("date")),
          "address": str(event.get("address")),
          "description": event.get("description"),
          "link": event.get("link")       
          }
        cleaned_events.append(cleaned_event)
      elif source == 'ticketmaster':
        venues = event.get('_embedded', {}).get('venues', [])
        venue_name = venues[0].get('name', 'Venue TBD') if venues else 'Venue TBD'
        city_name = venues[0].get('city', {}).get('name', '') if venues else ''
        address = f"{venue_name}, {city_name}".strip(", ")
        start_date = event.get('dates', {}).get('start', {}).get('localDate', 'Date TBD')

        cleaned_event = {
          "search_term": search_term.lower(),
          "source": "Ticketmaster",
          "title": event.get("name"),
          "date": start_date,
          "address": address,
          "link": event.get("url")  
        }
        cleaned_events.append(cleaned_event)
      else:
        continue
    
    if not cleaned_events:
      return

    df = pd.DataFrame.from_dict(cleaned_events)
    df.to_sql('events', con=engine, if_exists='append', index=False)


