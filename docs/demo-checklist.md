# Demo Checklist

## Start
```bash
cp .env.example .env
docker compose up -d
docker compose exec kafka bash /scripts/topics.sh
```

## Auth HA
- Register through API Gateway: `POST http://localhost:8080/auth/register`.
- Login through API Gateway: `POST http://localhost:8080/auth/login`.
- Confirm both `auth-service-1` and `auth-service-2` are running.
- Stop one auth instance and repeat login through `http://localhost:8080/auth/login`.
- Logout through API Gateway and confirm the same JWT no longer works for `/feed`.

## Async News Flow
- Confirm Kafka topics exist: `articles.raw` and `articles.processed`.
- Confirm `ingestion-service` publishes RSS articles into `articles.raw`.
- Confirm `processing-service` writes deduplicated articles into Mongo DB `processing`.
- Confirm `feed-service` consumes `articles.processed` and writes projections into Mongo DB `feed`.
- Fetch feed through API Gateway: `GET http://localhost:8080/feed?page=1&page_size=20`.

## Mongo Replica Set
- Check replica status: `docker compose exec mongo1 mongosh --eval 'rs.status()'`.
- Stop one secondary Mongo node and confirm the system still reads/writes.
- Stop enough Mongo nodes to lose quorum and explain the expected read-only/unavailable behavior.
