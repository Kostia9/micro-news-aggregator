#!/usr/bin/env bash
set -e

KAFKA=kafka:9092

kafka-topics --bootstrap-server $KAFKA --create --if-not-exists \
  --topic articles.raw --partitions 3 --replication-factor 1

kafka-topics --bootstrap-server $KAFKA --create --if-not-exists \
  --topic articles.processed --partitions 3 --replication-factor 1

echo "Kafka topics created."
