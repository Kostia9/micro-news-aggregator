# Use Cases / Product Backlog

## UC-1: User Registration
**Actor:** Reader
**Flow:** POST `/auth/register` -> password hashing -> Postgres write -> JWT issuance.

## UC-2: Login
**Actor:** Reader
**Flow:** POST `/auth/login` -> hash validation -> JWT issuance -> Redis write (allowlist).

## UC-3: Logout
**Actor:** Reader
**Flow:** POST `/auth/logout` -> token removal from Redis allowlist (revoke).

## UC-4: Feed Browsing
**Actor:** Reader
**Flow:** GET `/feed` through the API Gateway with JWT -> feed-service -> Mongo read model.

## UC-5: News Ingestion (background)
**Actor:** System
**Flow:** ingestion-service reads RSS -> stores seen URLs in MongoDB `ingestion` -> publishes new articles to Kafka `articles.raw`.

## UC-6: Article Processing (background)
**Actor:** System
**Flow:** processing-service consumes `articles.raw` -> deduplication/tags -> Mongo + `articles.processed`.

## UC-7: Feed Read Model (background)
**Actor:** System
**Flow:** feed-service consumes `articles.processed` -> upsert into MongoDB `feed`.

## Backlog
- [x] Auth: registration/login/logout + JWT in Redis
- [x] API Gateway: proxying + JWT/Redis allowlist validation
- [x] Ingestion: RSS fetcher + Mongo seen URLs + Kafka producer
- [x] Processing: Kafka consumer + deduplication/tagger + Mongo write
- [x] Feed: Kafka read model + REST feed API
- [x] HA: two auth-service instances + nginx + Redis tokens
- [x] Mongo replica set initialization
- [ ] Future: LLM summarization
- [ ] Future: Elasticsearch full-text search
