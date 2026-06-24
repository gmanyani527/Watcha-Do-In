import pandas as pd
pd.set_option('display.max_colwidth', None)
import sqlalchemy as db
from main import google_events

if not google_events:
    print("No events found.")
else:
    df = pd.DataFrame.from_dict(google_events)
    engine = db.create_engine('sqlite:///events.db')
    df.to_sql('google_events', con=engine, if_exists='replace', index=False)

    with engine.connect() as connection:
        query_result = connection.execute(db.text("SELECT * FROM google_events;")).fetchall()
        print(pd.DataFrame(query_result))
