#!/usr/bin/env bash
# Re-download the raw CFPB pull this project curates from.
# Public API, no authentication, no personal data. ~62 MB, a few minutes.
set -euo pipefail
mkdir -p data/raw
curl --fail --max-time 600 -o data/raw/cfpb_2026Q2.csv \
  "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?format=csv&no_aggs=true&has_narrative=true&date_received_min=2026-05-01&date_received_max=2026-08-01"
echo "Downloaded. Now run: python data_prep.py"
