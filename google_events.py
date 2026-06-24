import serpapi
import os
from main import search_terms

serpapi_key = os.getenv('SERPAPI_KEY')

client = serpapi.Client(api_key=serpapi_key)
results = client.search({
  "engine": "google_events",
  "q": search_terms['google_events']['q']
})
events_results = results["events_results"]
print(events_results)