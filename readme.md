# Habit Tracker (Django + DRF)

Проект контейнеризован и поставляется с готовым CI/CD на GitHub Actions и деплоем через Docker Compose. Ниже — как запустить локально **одной командой** и как настроить автодеплой на сервер.

---

## Требования

- Docker 24.x+
- **docker-compose** (v1.29.x или `docker compose` v2)
- Открыт порт **80** (nginx)

---

## Быстрый старт локально (одной командой)

1. Создайте `.env` в корне (По образцу .env_example).
2. Запустите стек:

```bash
docker-compose up -d --build
```

3. Откройте: `http://localhost` (через nginx).

**Что поднимется**: db(PostgreSQL 16), redis(7), backend(Django+Gunicorn на 8000), celery, celery-beat, nginx(80). Nginx проксирует на `backend:8000`, backend имеет healthcheck по `GET /health`.

Полезные команды:

```bash
# логи
docker-compose logs -f backend nginx

# миграции (если нужно вручную)
docker-compose exec backend python manage.py migrate --noinput

# суперпользователь
docker-compose exec backend python manage.py createsuperuser

# остановить стек
docker-compose down --remove-orphans
```

---

## CI/CD (GitHub Actions)

Workflow `ci.yml` состоит из этапов:

1. **lint** — flake8.
2. **test** — установка зависимостей, ожидание Postgres, `manage.py migrate`, тесты.
3. **image-smoke** — сборка образа backend, запуск мини-стека (db+redis+backend), миграции внутри контейнера и heathcheck HTTP.
4. **deploy** — деплой по SSH: `docker-compose pull` и `docker-compose up -d --build` на сервере.

В smoke-этапе backend проверяется напрямую (порт 8000) без nginx для скорости.

---

## Подготовка сервера (однократно)

1. Установите Docker и docker-compose.
2. Создайте каталог деплоя и положите туда `.env` с прод-настройками (По образцу .env_example).
3. Настройте SSH-доступ (публичный ключ в `~/.ssh/authorized_keys`).
4. Убедитесь, что порт 80 доступен.

---

## Настройка секретов GitHub Actions

- `SSH_USER` — пользователь на сервере
- `SSH_HOST` — адрес сервера
- `SSH_KEY` — приватный ключ (PEM) с доступом на сервер
- `DEPLOY_DIR` — путь каталога деплоя на сервере (например, `/opt/habit-tracker`)

---

## Деплой (автоматически)

После CI Action выполнит на сервере:

```bash
docker-compose pull
docker-compose up -d --build
```
---

## Постдеплойные проверки

```bash
docker-compose ps
curl -i http://localhost/nginx-health || curl -i http://localhost/health
```

Если `200 OK` — всё поднято. При `502` смотрите логи:

```bash
docker-compose logs --tail=200 nginx backend
```

---

## Структура репозитория

- `docker-compose.yml` — сервисы (db, redis, backend, celery, celery-beat, nginx) с healthchecks.
- `.github/workflows/ci.yml` — lint, test, smoke, deploy.
- `nginx/nginx.conf` — upstream на `backend:8000` и healthcheck.
