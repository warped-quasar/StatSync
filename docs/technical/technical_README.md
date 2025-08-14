# NBA Data Ingestion – Technical Documentation

## Overview
This script ingests NBA data using the `balldontlie` Python SDK and sends it to Splunk via an HTTP Event Collector (HEC).  
It supports teams, per-player box scores, and seasonal player stats.  
The design uses cursor-based pagination, batch sending, and minimal API delays to balance throughput and reliability.

## Code Structure
### 1. `send_batches(rows, sourcetype, batch=500)`
- Sends events to Splunk in fixed-size batches.
- Improves throughput while keeping memory use predictable.

### 2. `ingest_box_scores(date_str)`
- Fetches per-player box scores for a specific date.
- Uses cursor-based pagination until all pages are processed.
- Sends data in batches.

### 3. `ingest_teams()`
- Retrieves a static list of NBA teams in a single request.
- Sends data to Splunk with the `nba:team` sourcetype.

### 4. `ingest_stats_for_season(season, postseason=False)`
- Retrieves seasonal player stats, optionally including postseason data.
- Follows the same pagination and batching pattern as `ingest_box_scores`.

### 5. `__main__`
- Sends a health event to Splunk to confirm HEC connectivity.
- Runs ingestion tasks in sequence: teams → box scores → optional season stats.

## Dependencies
- **Python 3.8+**
- `balldontlie` Python SDK
- `hec_client` (custom Splunk HEC wrapper)
- Standard library: `os`, `time`

## Configuration
| Variable      | Purpose                                     |
|---------------|---------------------------------------------|
| `API_KEY`     | balldontlie API key (if required)           |
| `HEC_URL`     | Splunk HEC endpoint URL                     |
| `HEC_TOKEN`   | Splunk HEC token value                      |
| `INDEX`       | Default Splunk index (e.g., `sports`)       |
| `VERIFY`      | Enable TLS certificate verification         |

## Flow Control
- Cursor-based pagination.
- Batch size defaults to **500**.
- `0.2s` delay between API calls to avoid rate limits.

## Error Handling & Logging
- Prints detailed progress at page and batch level.
- Exits when pagination cursor is missing or falsy.

## Extending the Script
- To add new endpoints:
  1. Follow the pagination pattern.
  2. Use `send_batches()` to send events.
  3. Define a new `ingest_` function for clarity.
