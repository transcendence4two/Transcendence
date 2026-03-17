#!/bin/bash

ES_URL="${ES_URL:-http://elasticsearch:9200}"
ILM_DIR="${ILM_DIR:-/scripts/ilm}"
SLM_DIR="${SLM_DIR:-/scripts/slm}"

echo "Starting Elasticsearch bootstrap..."

# Wait for Elasticsearch
until curl -s -u "elastic:${ELASTIC_PASSWORD}" "${ES_URL}" | grep -q 'tagline'; do
  sleep 2
done
echo "Elasticsearch is ready."

# Snapshot repository
STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -u "elastic:${ELASTIC_PASSWORD}" \
  "${ES_URL}/_snapshot/transcendence_local")

if [ "$STATUS" != "200" ]; then
  curl --fail -s -u "elastic:${ELASTIC_PASSWORD}" \
    -X PUT "${ES_URL}/_snapshot/transcendence_local" \
    -H "Content-Type: application/json" \
    -d '{
      "type": "fs",
      "settings": {
        "location": "/snapshots",
        "compress": true
      }
    }'
  echo "Snapshot repository 'transcendence_local' created successfully!"
else
  echo "Snapshot repository already exists, skipping."
fi

# Setup ILM policies
if [ ! -d "$ILM_DIR" ] || ! ls "$ILM_DIR"/*.json >/dev/null 2>&1; then
  echo "Error: No ILM JSON files found in $ILM_DIR"
  exit 1
fi

for file in "$ILM_DIR"/*.json; do
  policy_name=$(basename "$file" .json)
  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    -u "elastic:${ELASTIC_PASSWORD}" \
    -X PUT "${ES_URL}/_ilm/policy/${policy_name}" \
    -H "Content-Type: application/json" \
    -d @"$file")

  if [ "$RESPONSE" -eq 200 ] || [ "$RESPONSE" -eq 201 ]; then
    echo "ILM policy '$policy_name' created successfully."
  fi
done

# Setup SLM policies
if [ ! -d "$SLM_DIR" ] || ! ls "$SLM_DIR"/*.json >/dev/null 2>&1; then
  echo "Error: No SLM JSON files found in $SLM_DIR"
  exit 1
fi

for file in "$SLM_DIR"/*.json; do
  policy_name=$(basename "$file" .json)
  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    --fail -u "elastic:${ELASTIC_PASSWORD}" \
    -X PUT "${ES_URL}/_slm/policy/${policy_name}" \
    -H "Content-Type: application/json" \
    -d @"$file")

  if [ "$RESPONSE" -eq 200 ] || [ "$RESPONSE" -eq 201 ]; then
    echo "SLM policy '$policy_name' created successfully."
  fi
done

# Bootstrap indices + templates
declare -A SERVICES=(
  ["usermanagement-service"]="usermanagement-logs-policy"
  ["emails-service"]="emails-logs-policy"
  ["game-service"]="game-logs-policy"
  ["friends-service"]="friends-logs-policy"
  ["tournament-service"]="tournament-logs-policy"
)

for SERVICE in "${!SERVICES[@]}"; do
  ALIAS="${SERVICE}-logs"
  POLICY="${SERVICES[$SERVICE]}"

  # Create index template
  curl -s -u "elastic:${ELASTIC_PASSWORD}" \
    -X PUT "${ES_URL}/_index_template/${ALIAS}-template" \
    -H "Content-Type: application/json" \
    -d "{
      \"index_patterns\": [\"${ALIAS}-*\"],
      \"template\": {
        \"settings\": {
          \"index.lifecycle.name\": \"${POLICY}\",
          \"index.lifecycle.rollover_alias\": \"${ALIAS}\"
        }
      }
    }"

  # Check if alias already exists
  ALIAS_EXISTS=$(curl -s -o /dev/null -w "%{http_code}" \
    -u "elastic:${ELASTIC_PASSWORD}" \
    "${ES_URL}/_alias/${ALIAS}")

  if [ "$ALIAS_EXISTS" != "200" ]; then
    curl -s -u "elastic:${ELASTIC_PASSWORD}" \
      -X PUT "${ES_URL}/%3C${ALIAS}-%7Bnow%2Fd%7D-000001%3E" \
      -H "Content-Type: application/json" \
      -d "{
        \"aliases\": {
          \"${ALIAS}\": {
            \"is_write_index\": true
          }
        }
      }"
    echo "Bootstrap index for '$ALIAS' created successfully."
  else
    echo "Alias '$ALIAS' already exists, skipping bootstrap index."
  fi
done

echo "Elasticsearch bootstrap completed successfully."
