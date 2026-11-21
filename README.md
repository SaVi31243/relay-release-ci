# Relay

Сервіс Flask відповідає на `/health` станом із `release-profile.json`, а `/version` повертає версію з `RELAY_REVISION`.

## Локальна перевірка

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-test.txt
cp .env.example .env
docker build --build-arg RELAY_REVISION=local -t relay-lab:local .
docker compose up -d --wait --wait-timeout 21
python -m pytest -q test_relay.py
python -m pytest -q test_container.py --hosts="docker://$(docker compose ps -q relay)"
python probe.py 8291 local
docker compose down
```

## Випуск та досліди

Pull request до `main` запускає тести й збірку. Після злиття образ проходить Testinfra й HTTP-перевірку на Ubuntu, після чого публікується в GHCR із тегом SHA. Артефакти зберігають JUnit XML та журнали.

Запусти `Relay release checks` вручну для `experiment/assertion-failure`, щоб перевірити блокування розгортання. Для `experiment/maintenance` потрібен попередній успішний запуск `main`. У цій гілці профіль містить `maintenance`. CI повертає попередній образ із GHCR, перевіряє його та залишає статус Failure для відхиленого випуску.

## Ручний відкат

Підстав повний SHA останньої справної версії. Для приватного пакета спочатку увійди до GHCR з доступом на читання.

```bash
export RELAY_IMAGE=ghcr.io/savi31243/relay-release-ci:PREVIOUS_SHA
docker compose pull relay
docker compose up -d --force-recreate --wait --wait-timeout 21
python probe.py 8291 PREVIOUS_SHA
docker compose down
```

Навчальне середовище існує під час завдання GitHub Actions. На власній Linux VM команда підтримувала б Docker, ОС і мережеві правила. На PaaS провайдер обслуговував би платформу, а команда оновлювала б образ. Основні витрати створюють обчислення, сховище та трафік.
