#!/bin/sh
until curl -s http://elasticsearch:9200/_cluster/health | grep -q '"status":"green"' || \
      curl -s http://elasticsearch:9200/_cluster/health | grep -q '"status":"yellow"'; do
    echo "Waiting for Elasticsearch..."
    sleep 5
done
echo "Elasticsearch is ready."