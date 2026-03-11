#!/bin/bash
set -e

# Wait for Elasticsearch to start
until curl -u elastic:$ELASTIC_PASSWORD http://localhost:9200 > /dev/null 2>&1; do
  sleep 5
done

# Loop through all ILM JSON files and create policies
for file in /usr/share/elasticsearch/ilm/*.json; do
  policy_name=$(basename "$file" .json)
  echo "Creating ILM policy: $policy_name"
  curl -u elastic:$ELASTIC_PASSWORD -X PUT "http://localhost:9200/_ilm/policy/$policy_name" \
       -H "Content-Type: application/json" \
       -d @"$file"
done

echo "All ILM policies have been created successfully!"
