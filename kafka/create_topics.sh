#!/bin/bash

docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create --if-not-exists \
  --topic telemetry_raw \
  --partitions 1 \
  --replication-factor 1

docker exec -it kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create --if-not-exists \
  --topic telemetry_analytics \
  --partitions 1 \
  --replication-factor 1
