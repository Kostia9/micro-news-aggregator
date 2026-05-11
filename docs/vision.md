# Vision

## Призначення
Micro News Aggregator — мікросервісна платформа для збору, обробки та показу новин з відкритих RSS-джерел.

## MVP Можливості
- Реєстрація / автентифікація користувачів через JWT.
- Logout з відкликанням JWT через Redis allowlist.
- Автоматичний збір статей з RSS-джерел.
- Асинхронна обробка через Kafka.
- Дедуплікація, тегування і read model для стрічки.
- Доступ до системи через API Gateway.

## Користувачі
- **Читач** — реєструється, логіниться та переглядає стрічку новин.
- **Адміністратор** — переглядає налаштовані RSS-джерела.

## Нефункціональні вимоги
- Відмовостійкість auth-сервісу: два інстанси + nginx + Redis для токенів.
- Реплікація MongoDB: replica set `rs0` з трьома нодами.
- Окрема persistence-модель для сервісів: Postgres для auth, Mongo DB `ingestion` для ingestion, Mongo DB `processing` для processing, Mongo DB `feed` для feed.
- Асинхронна інтеграція між ingestion, processing і feed через Kafka.

## Future Scope
- AI-сумаризація через LLM.
- Elasticsearch full-text search.
- Окремий frontend.
