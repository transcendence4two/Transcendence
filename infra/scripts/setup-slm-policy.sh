#!/bin/bash
set -e

# Path to SLM JSON policies
SLM_DIR="./infra/elasticsearch/slm"

# Check if the folder exists and has JSON files
if [ ! -d "$SLM_DIR" ] || [ -z "$(ls $SLM_DIR/*.json 2>/dev/null)" ]; then
  echo "Error: No JSON files found in $SLM_DIR"
  exit 1
fi

for file in "$SLM_DIR"/*.json; do
  policy_name=$(basename "$file" .json)
  echo "Creating SLM policy: $policy_name"

  curl --fail -u elastic:$ELASTIC_PASSWORD \
       -X PUT "http://localhost:9200/_slm/policy/$policy_name" \
       -H "Content-Type: application/json" \
       -d @"$file"
done

echo "All SLM policies have been created successfully!"
