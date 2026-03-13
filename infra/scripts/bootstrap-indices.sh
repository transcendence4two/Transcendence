#!/bin/bash
set -e

if [ -f .env ]; then
  source .env
elif [ -f ../../.env ]; then
  source ../../.env
else
  echo ".env file not found"
  exit 1
fi

ES_URL="${ES_URL:-http://localhost:9200}"

echo "Waiting for Elasticsearch at ${ES_URL}..."
until curl -s -u "elastic:${ELASTIC_PASSWORD}" "${ES_URL}" | grep -q 'tagline'; do
  sleep 2
done

ILM_DIR="${ILM_DIR:-./infra/elasticsearch/ilm}"
if [ -d "$ILM_DIR" ] && ls "$ILM_DIR"/*.json &>/dev/null; then
  for file in "$ILM_DIR"/*.json; do
    policy_name=$(basename "$file" .json)
    echo "Creating ILM policy: $policy_name"
    curl -s -u "elastic:${ELASTIC_PASSWORD}" -X PUT "${ES_URL}/_ilm/policy/$policy_name" \
      -H "Content-Type: application/json" \
      -d @"$file"
    echo ""
  done
else
  echo "No ILM JSON files found in $ILM_DIR, skipping."
fi

declare -A SERVICES
SERVICES=(
  ["usermanagement-service"]="usermanagement-logs-policy"
  ["emails-service"]="emails-logs-policy"
  ["game-service"]="game-logs-policy"
  ["friends-service"]="friends-logs-policy"
  ["tournament-service"]="tournament-logs-policy"
)

for SERVICE in "${!SERVICES[@]}"; do
  ALIAS="${SERVICE}-logs"
  POLICY="${SERVICES[$SERVICE]}"

  echo "--------------------------------------------------"
  echo "Bootstrapping $SERVICE..."

  echo "Creating template for ${ALIAS}..."
  curl -s -u "elastic:${ELASTIC_PASSWORD}" -X PUT "${ES_URL}/_index_template/${ALIAS}-template" \
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
  echo ""

  ALIAS_EXISTS=$(curl -s -o /dev/null -w "%{http_code}" -u "elastic:${ELASTIC_PASSWORD}" "${ES_URL}/_alias/${ALIAS}")
  if [ "$ALIAS_EXISTS" != "200" ]; then
    echo "Creating bootstrap index for ${ALIAS}..."
    curl -s -u "elastic:${ELASTIC_PASSWORD}" -X PUT "${ES_URL}/%3C${ALIAS}-%7Bnow%2Fd%7D-000001%3E" \
      -H "Content-Type: application/json" \
      -d "{
        \"aliases\": {
          \"${ALIAS}\": {
            \"is_write_index\": true
          }
        }
      }"
    echo ""
  else
    echo "Alias ${ALIAS} already exists, skipping bootstrap index."
  fi
done

echo "Bootstrapping complete!"
