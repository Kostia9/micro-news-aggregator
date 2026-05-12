# Demo Checklist

## Running
```bash
cp .env.example .env
docker compose up -d
```

## HA for auth-service
- Register a user through the API Gateway: `POST http://localhost:8080/auth/register`.
- Log in through the API Gateway: `POST http://localhost:8080/auth/login`.
- Confirm that `auth-service-1` and `auth-service-2` are running.
- Stop one auth-service instance and repeat login through `http://localhost:8080/auth/login`.
- Log out through the API Gateway and confirm that the same JWT no longer works for `/feed`.

## Asynchronous News Flow
- Confirm that the Kafka topics exist: `articles.raw` and `articles.processed`.
- Confirm that `ingestion-service` stores seen URLs in MongoDB `ingestion` and publishes new RSS articles to `articles.raw`.
- Confirm that `processing-service` writes deduplicated articles to MongoDB `processing`.
- Confirm that `feed-service` consumes `articles.processed` and writes projections to MongoDB `feed`.
- Fetch the feed through the API Gateway: `GET http://localhost:8080/feed?page=1&page_size=20`.

## Mongo replica set
- Check replication status: `docker compose exec mongo1 mongosh --eval 'rs.status()'`.
- Stop one Mongo secondary node and confirm that the system still reads/writes data.
- Stop enough Mongo nodes to lose quorum and explain the expected read-only or unavailable behavior.
