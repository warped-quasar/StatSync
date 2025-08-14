## **`nba_ingestion_highlevel.md`**

# NBA Data Ingestion – High-Level Guide

## Purpose
This script pulls NBA data from the balldontlie API and sends it to Splunk for analytics.  
It includes teams, box scores, and seasonal stats, all tagged with specific Splunk sourcetypes.

## What You’ll Need
- **Splunk v10.0+** with HTTP Event Collector (HEC) enabled
- **Python 3.8+**
- Required Python libraries:
  ```bash
  pip install balldontlie

(Plus your custom `hec_client` module)

## Setting Up HEC in Splunk 10.0

1. Log in to Splunk as an admin.
2. Navigate to:

   ```
   Settings → Data Inputs → HTTP Event Collector
   ```
3. Click **New Token**.
4. Name it (e.g., `nba_ingestion`).
5. Select the correct index (e.g., `sports`).
6. Set sourcetype to `Automatic` or a custom type (e.g., `nba:boxscore`).
7. Enable the token and save.
8. Copy the **Token Value** for use in the script.
9. Ensure HEC is globally enabled:

   ```
   Settings → Data Inputs → HTTP Event Collector → Global Settings
   ```

## Configuring the Script

Edit the variables in the script:

```python
API_KEY   = "YOUR_API_KEY"
HEC_URL   = "https://yoursplunkserver:8088"
HEC_TOKEN = "YOUR_HEC_TOKEN"
INDEX     = "sports"
VERIFY    = True
```

## Running the Script

Run the script from your terminal:

```bash
python nba_ingestion.py
```

### Default Workflow

1. Ingest team list (one-time fetch)
2. Ingest box scores for a given date (default: `2024-11-01`)
3. (Optional) Ingest full season stats

## Checking Data in Splunk

Example search:

```spl
index="sports" sourcetype="nba:boxscore"
```

## Troubleshooting

* **No Data** – Check HEC token, index permissions, and endpoint URL.
* **TLS Errors** – Set `VERIFY=False` temporarily.
* **Partial Data** – Verify API pagination and batch size.

```