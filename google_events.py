import serpapi
import os
import json

def fetch_google_events(query):
  serpapi_key = os.getenv('SERPAPI_KEY')

  client = serpapi.Client(api_key=serpapi_key)
  results = client.search({
    "engine": "google_events",
    "q": query
  })
  events_results = results.get("events_results", [])

  for event in events_results:
      for key, value in event.items():
          if isinstance(value, (dict, list)):
              event[key] = json.dumps(value)

  return events_results