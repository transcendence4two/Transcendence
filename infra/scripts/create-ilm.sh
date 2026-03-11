#!/bin/bash
set -e

# Path to ILM JSONs on host
ILM_DIR="./infra/elasticsearch/ilm"

# Check if the folder exists and has JSON files
if [ ! -d "$ILM_DIR" ] || [ -z "$(ls $ILM_DIR/*.json 2>/dev/null)" ]; then
  echo "Error: No JSON files found in $ILM_DIR"
  exit 1
fi

for file in "$ILM_DIR"/*.json; do
  policy_name=$(basename "$file" .json)
  echo -e "Creating ILM policy: $policy_name"
  curl -u elastic:$ELASTIC_PASSWORD -X PUT "http://localhost:9200/_ilm/policy/$policy_name" \
       -H "Content-Type: application/json" \
       -d @"$file"
done

echo "All ILM policies have been created successfully!"
