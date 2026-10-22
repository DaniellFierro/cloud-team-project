# Контейнеризация Cloud Service Catalog

## Схема выполнения

Windows → NAT VirtualBox → Ubuntu:8080 → Docker Engine → контейнер:5000 → Python.
ВМ имеет отдельное ядро Linux; контейнер использует это ядро и изолированное
пространство процессов и файлов. Приложение сохраняет монолитную архитектуру.

## Состав образа

Dockerfile основан на предоставленном учебном проекте: python:3.12-slim,
/opt/cloud-app, пользователь appuser с UID 10001, установка requirements.txt,
копирование app/ и запуск python -m app.main. Добавлены HOST, PORT и HEALTHCHECK.
Текущий requirements.txt не требует сетевой установки пакетов.
Тег базового образа изменяемый; точный digest фактической сборки сохраняется в
журнале лабораторной работы. Для строгого повторения используйте FROM с digest.

## Диагностика и проверка

```bash
sudo docker image inspect cloud-catalog:v1
sudo docker ps --filter name=cloud-catalog-docker
sudo docker inspect --format '{{.State.Status}} {{.State.Health.Status}}' cloud-catalog-docker
sudo docker logs cloud-catalog-docker
curl -i http://127.0.0.1:8080/
curl -i http://127.0.0.1:8080/health
curl -i http://127.0.0.1:8080/api/services
sudo docker exec cloud-catalog-docker id
```

HEALTHCHECK проверяет /health; целостность каталога проверяется отдельным запросом.
Статус starting после запуска нормален до первого успешного healthcheck.
Если порт недоступен, проверьте логи, -p и HOST=0.0.0.0 внутри контейнера.
Если имя занято, проверьте существующий контейнер; не удаляйте чужие контейнеры.
В лабораторной работе используются sudo-команды без добавления пользователя
в привилегированную группу docker.

## Проверка исходных тестов внутри образа

Из каталога клона на ВМ можно подключить тесты только на чтение:

```bash
sudo docker run --rm --network none \
  -v "$PWD/tests:/opt/cloud-app/tests:ro" \
  cloud-catalog:v1 python -m unittest discover -s tests -v
```

Тесты поднимают HTTP-сервер на loopback контейнера и не требуют Интернета.
Тесты не включены в рабочий образ, чтобы не увеличивать его состав.

## Ограничения

Один контейнер на одной ВМ не обеспечивает отказоустойчивость к отказу ВМ.
Флаг --restart перезапускает завершившийся процесс; сам по себе статус unhealthy
не гарантирует автоматического перезапуска. Это учебный сервер без TLS и аутентификации.
Инструкция сборки и запуска находится в разделе Docker основного README.
