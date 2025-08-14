"""
NBA data ingestion script using the balldontlie SDK and Splunk HEC.
Adds inline comments to explain design choices and flow control so that
runtime behavior is easy to debug. The code paths are unchanged.
"""

import os, time
from balldontlie import BalldontlieAPI
from hec_client import SplunkHEC  # thin wrapper around Splunk HTTP Event Collector

# External configuration values.
# API_KEY is for balldontlie if your SDK or gateway expects one
# HEC_URL and HEC_TOKEN point to your Splunk HEC endpoint
API_KEY   = "5022027f-a695-4901-80b4-62a005449560"
HEC_URL   = "https://localhost:8088"
HEC_TOKEN = "SPLUNK_HEC_TOKEN"
INDEX     = "sports"      # default Splunk index for all events
VERIFY    = False          # set to True in production to verify TLS certs

# Instantiate clients. These are long lived so we do this once at module import.
api = BalldontlieAPI(api_key=API_KEY)
hec = SplunkHEC(HEC_URL, HEC_TOKEN, verify=VERIFY, default_index=INDEX)

def send_batches(rows, sourcetype, batch=500):
    """
    Send a sequence of events to Splunk in fixed size chunks.

    rows       iterable of dicts to send
    sourcetype Splunk sourcetype to tag the events with
    batch      number of events per request to balance throughput and memory
    """
    print(f"Preparing to send {len(rows)} rows for {sourcetype} in batches of {batch}...")

    buf = []  # local buffer to accumulate a batch
    for i, r in enumerate(rows, start=1):
        buf.append(r)
        # When the buffer reaches the target batch size, flush to Splunk
        if len(buf) >= batch:
            print(f"Sending batch of {len(buf)} rows to Splunk ({i}/{len(rows)})...")
            hec.send(buf, sourcetype=sourcetype)  # single network call per batch
            buf.clear()                            # reuse the same list to avoid churn

    # Flush any remaining events that did not fill a complete batch
    if buf:
        print(f"Sending final batch of {len(buf)} rows to Splunk...")
        hec.send(buf, sourcetype=sourcetype)

def ingest_box_scores(date_str):
    """
    Pull per player box scores for a given date. The endpoint is paginated
    with a cursor token. We loop until the server indicates there are no
    more pages. Sleep between calls to avoid rate limits.
    """
    print(f"Starting box score ingestion for {date_str}...")

    cursor = None       # None on the first request means start at page one
    page_count = 0      # explicit counter for log readability

    while True:
        page_count += 1
        print(f"Fetching box scores page {page_count}...")

        # Build request parameters. Cursor is only included after the first call.
        kw = {"date": date_str, "per_page": 100}
        if cursor:
            kw["cursor"] = cursor

        # SDK call. Expected response shape is {"data": [...], "meta": {...}}
        resp = api.nba.box_scores.list(**kw)
        print(f"Retrieved {len(resp['data'])} records.")

        # Ship the page worth of records to Splunk
        send_batches(resp["data"], "nba:boxscore")

        # Update cursor from server metadata. When missing or falsy, we are done.
        cursor = resp.get("meta", {}).get("next_cursor")
        if not cursor:
            print("No more pages for box scores.")
            break

        # Be polite to the API and give the server a short breather
        time.sleep(0.2)

    print("Box score ingestion complete.")

def ingest_teams():
    """
    Fetch the static list of NBA teams. This endpoint is not paginated
    in the current SDK, so a single request returns the full set.
    """
    print("Fetching NBA teams...")

    resp = api.nba.teams.list()
    print(f"Retrieved {len(resp['data'])} teams.")

    send_batches(resp["data"], "nba:team")
    print("Teams ingestion complete.")

def ingest_stats_for_season(season=2024, postseason=False):
    """
    Pull player stats for a season with optional postseason flag.
    Uses the same cursor based pagination pattern as box scores.
    """
    print(f"Starting stats ingestion for season {season}, postseason={postseason}...")

    cursor = None
    page_count = 0

    while True:
        page_count += 1
        print(f"Fetching stats page {page_count}...")

        kw = {"seasons": [season], "postseason": postseason, "per_page": 100}
        if cursor:
            kw["cursor"] = cursor

        resp = api.nba.stats.list(**kw)
        print(f"Retrieved {len(resp['data'])} records.")

        send_batches(resp["data"], "nba:stat")

        cursor = resp.get("meta", {}).get("next_cursor")
        if not cursor:
            print("No more pages for stats.")
            break

        time.sleep(0.2)

    print("Stats ingestion complete.")

if __name__ == "__main__":
    # A lightweight health event to confirm HEC connectivity at the start
    print("Initializing Splunk NBA ingestion pipeline...")
    hec.send_one({"msg": "sdk pipeline up"}, sourcetype="nba:health")

    # Teams first, since it is a one shot and useful for lookups
    ingest_teams()

    # Pull a specific date worth of box scores. Adjust as needed for your run plan.
    ingest_box_scores("2024-11-01")

    # Optional backfill example
    # ingest_stats_for_season(2024, postseason=False)

    print("Pipeline run complete.")
