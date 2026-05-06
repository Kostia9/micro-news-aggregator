# Use Cases / Product Backlog

## UC-1: Реєстрація користувача
**Actor:** Читач
**Flow:** POST `/auth/register` → hash пароля → запис у Postgres → видача JWT.

## UC-2: Логін
**Actor:** Читач
**Flow:** POST `/auth/login` → перевірка хешу → видача JWT → запис у Redis (allowlist).

## UC-3: Логаут
**Actor:** Читач
**Flow:** POST `/auth/logout` → видалення токена з Redis (blacklist/revoke).

## UC-4: Перегляд стрічки
**Actor:** Читач
**Flow:** GET `/feed` через API Gateway з JWT → feed-service → Mongo read model.

## UC-5: Збір новин (фоновий)
**Actor:** System
**Flow:** ingestion-service читає RSS → публікує в Kafka `articles.raw`.

## UC-6: Обробка статей (фоновий)
**Actor:** System
**Flow:** processing-service консюмить `articles.raw` → дедуп/теги → Mongo + `articles.processed`.

## UC-7: Feed read model (фоновий)
**Actor:** System
**Flow:** feed-service консюмить `articles.processed` → upsert у Mongo DB `feed`.

## Backlog
- [x] Auth: register/login/logout + JWT в Redis
- [x] API Gateway: proxy + JWT/Redis allowlist check
- [x] Ingestion: RSS fetcher + Kafka producer
- [x] Processing: Kafka consumer + dedup/tagger + Mongo writer
- [x] Feed: Kafka read model + REST feed API
- [x] HA: два інстанси auth-service + nginx + Redis tokens
- [x] Mongo replica set init
- [ ] Future: LLM summarization
- [ ] Future: Elasticsearch full-text search
