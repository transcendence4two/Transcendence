#!/bin/bash
set -e

# Create snapshot repository for Elasticsearch log archiving
curl --fail -u elastic:$ELASTIC_PASSWORD \
     -X PUT "http://localhost:9200/_snapshot/transcendence_local" \
     -H "Content-Type: application/json" \
     -d '{
       "type": "fs",
       "settings": {
         "location": "/snapshots",
         "compress": true
       }
     }'

echo "Snapshot repository 'transcendence_local' created successfully!"
