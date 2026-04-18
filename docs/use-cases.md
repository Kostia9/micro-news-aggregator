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
**Flow:** GET `/feed` через API Gateway → feed-service → Mongo + Redis кеш.

## UC-5: Пошук статей
**Actor:** Читач
**Flow:** GET `/search?q=...` → feed-service → Elasticsearch.

## UC-6: Збір новин (фоновий)
**Actor:** System
**Flow:** ingestion-service читає RSS → публікує в Kafka `articles.raw`.

## UC-7: Обробка статей (фоновий)
**Actor:** System
**Flow:** processing-service консюмить `articles.raw` → дедуп/теги → Mongo + `articles.processed`.

## UC-8: LLM-сумаризація (фоновий)
**Actor:** System
**Flow:** llm-service консюмить `articles.processed` → Gemini → `articles.summarized`.

## Backlog
- [ ] Auth: register/login/logout + JWT в Redis
- [ ] API Gateway: проксі + middleware перевірки JWT
- [ ] Ingestion: RSS fetcher + Kafka producer
- [ ] Processing: Kafka consumer + dedup/tagger + Mongo writer
- [ ] LLM: Kafka consumer + Gemini client
- [ ] Feed: REST API + Mongo reader + Elasticsearch search
- [ ] HA: два інстанси auth-service + nginx + Redis-sessions
- [ ] Mongo replica set init
