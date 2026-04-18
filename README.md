# Micro News Aggregator

Мікросервісна платформа для збору, обробки та персоналізованого показу новин.

## Документація
- [Vision](docs/vision.md)
- [Use cases / Backlog](docs/use-cases.md)
- [Architecture diagram](docs/architecture.svg)

## Сервіси
| Сервіс | Призначення | Стек |
|---|---|---|
| `api-gateway` | Маршрутизація, auth middleware | FastAPI |
| `auth-service` | Реєстрація / login / logout (JWT) | FastAPI + Postgres + Redis |
| `ingestion-service` | Збір RSS → Kafka | FastAPI + aiokafka |
| `processing-service` | Дедуп / теги → Mongo | FastAPI + Kafka + MongoDB |
| `llm-service` | AI-сумаризація (Gemini) | FastAPI + Kafka |
| `feed-service` | Стрічка + пошук | FastAPI + MongoDB + Elasticsearch + Redis |

## Інфраструктура
- Kafka + Zookeeper
- MongoDB replica set (`rs0`, 3 ноди)
- Postgres, Redis, Elasticsearch
- `auth-service` дубльований + nginx (`auth-lb`) для HA

## Запуск
```bash
cp .env.example .env
docker compose up -d
docker compose exec kafka bash /scripts/topics.sh
```
