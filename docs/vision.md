# Vision

## Purpose
Micro News Aggregator is a microservice platform for collecting, processing, and displaying news from open RSS sources.

## MVP Capabilities
- User registration / authentication through JWT.
- Logout with JWT revocation through a Redis allowlist.
- Automatic article collection from RSS sources.
- Asynchronous processing through Kafka.
- Deduplication, tagging, and a read model for the feed.
- System access through an API Gateway.

## Users
- **Reader** - registers, logs in, and browses the news feed.

## Non-Functional Requirements
- Fault tolerance for the auth service: two instances + nginx + Redis for tokens.
- MongoDB replication: replica set `rs0` with three nodes.
- Separate persistence model for services: Postgres for auth, Mongo DB `ingestion` for ingestion, Mongo DB `processing` for processing, Mongo DB `feed` for feed.
- Asynchronous integration between ingestion, processing, and feed through Kafka.

## Future Work
- AI summarization through an LLM.
- Elasticsearch full-text search.
- Separate frontend.
