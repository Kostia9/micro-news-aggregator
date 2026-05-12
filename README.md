# Micro News Aggregator

Microservice platform for collecting RSS news, processing it asynchronously, and exposing a feed through an API Gateway.

## Documentation
- [Vision](docs/vision.md)
- [Use cases / backlog](docs/use-cases.md)
- [Architecture diagram](docs/architecture.png)
- [Demo checklist](docs/demo-checklist.md)

## MVP services
| Service | Purpose | Data storage |
|---|---|---|
| `api-gateway` | Single REST entry point, JWT validation, proxying | Redis allowlist validation |
| `auth-service` | Registration / login / logout, JWT | Postgres + Redis |
| `ingestion-service` | RSS polling -> Kafka `articles.raw` | MongoDB `ingestion` |
| `processing-service` | Deduplication, tagging, Mongo writes, Kafka `articles.processed` | MongoDB `processing` |
| `feed-service` | Read model from Kafka + `GET /feed` | MongoDB `feed` |

## Infrastructure
- Kafka (KRaft mode) for asynchronous processing.
- MongoDB replica set (`rs0`, 3 nodes) with separate logical databases: `ingestion`, `processing`, `feed`.
- Postgres for auth-service users.
- Redis for the JWT allowlist shared by duplicated auth-service instances.
- `auth-service` is duplicated behind nginx (`auth-lb`) for the HA scenario.

`llm-service` and Elasticsearch/search are left as future work and run through the Compose profile `future`.

## Running
```bash
cp .env.example .env
docker compose up -d
```

## API Gateway
```text
POST /auth/register
POST /auth/login
POST /auth/logout
GET  /feed?page=1&page_size=20&topic=technology
```
