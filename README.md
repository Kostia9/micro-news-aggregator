# Micro News Aggregator

Мікросервісна платформа для збору RSS-новин, асинхронної обробки та показу стрічки через API Gateway.

## Документація
- [Vision](docs/vision.md)
- [Use cases / Backlog](docs/use-cases.md)
- [Architecture diagram](docs/architecture.png)
- [Demo checklist](docs/demo-checklist.md)

## MVP Сервіси
| Сервіс | Призначення | Persistence |
|---|---|---|
| `api-gateway` | Єдина REST-точка входу, JWT-перевірка, proxy | Redis allowlist lookup |
| `auth-service` | Register / login / logout, JWT | Postgres + Redis |
| `ingestion-service` | RSS polling -> Kafka `articles.raw` | MongoDB `ingestion` |
| `processing-service` | Dedup, tagging, Mongo write, Kafka `articles.processed` | MongoDB `processing` |
| `feed-service` | Kafka read model + `GET /feed` | MongoDB `feed` |

## Інфраструктура
- Kafka (KRaft mode) для асинхронної обробки.
- MongoDB replica set (`rs0`, 3 ноди) з окремими логічними БД `ingestion`, `processing`, `feed`.
- Postgres для користувачів auth-service.
- Redis для JWT allowlist між дубльованими auth-service інстансами.
- `auth-service` дубльований за nginx (`auth-lb`) для HA-сценарію.

`llm-service` та Elasticsearch/search залишені як future scope і запускаються через Compose profile `future`.

## Запуск
```bash
cp .env.example .env
docker compose up -d
docker compose exec kafka bash /scripts/topics.sh
```

## API Gateway
```text
POST /auth/register
POST /auth/login
POST /auth/logout
GET  /feed?page=1&page_size=20&topic=technology
```
