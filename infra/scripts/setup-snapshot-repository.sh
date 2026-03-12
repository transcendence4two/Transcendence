#!/bin/bash

# Create snapshot repository for Elasticsearch log archiving

curl -X PUT "http://elasticsearch:9200/_snapshot/transcendence_local" \
-H "Content-Type: application/json" \
-d '{
  "type": "fs",
  "settings": {
    "location": "/snapshots",
    "compress": true
  }
}'
