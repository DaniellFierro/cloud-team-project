# Cloud Service Catalog

Учебное HTTP-приложение для знакомства с моделями **IaaS**, **PaaS** и **SaaS**.
Каталог доступен как JSON API; главная HTML-страница содержит ссылки на API и проверку состояния.

## Автор

Сазонов Даниил Евгеньевич, группа ДОТ2026_ИСР262дк, GitHub **DaniellFierro**.
Работа выполняется индивидуально: разработка, документация и самопроверка.

## Возможности

- Просмотр каталога трёх моделей облачных сервисов.
- Проверка работы HTTP-процесса через `/health`.
- Настройка заголовка, интерфейса и порта через окружение.
- Шесть автоматических тестов реального HTTP-сервера.

## Архитектура

Простой монолит: один процесс Python и локальный JSON-файл. Клиент отправляет GET,
обработчик выбирает маршрут и формирует HTML или JSON. При запросе каталога обработчик
читает `app/services.json`. Записи через API нет; обновление каталога выполняется через Git.

| Компонент | Назначение | Взаимодействие |
|---|---|---|
| Браузер / curl | Клиент | HTTP GET к серверу |
| `app/main.py` | Маршрутизация и ответы | Читает каталог и переменные окружения |
| `app/services.json` | Данные каталога | JSON с массивом `services` |
| Окружение процесса | Настройка запуска | `HOST`, `PORT`, `APP_TITLE` |

```text
Клиент → HTTP-сервер → services.json
Клиент ← HTML / JSON ← HTTP-сервер
```

Подробнее: [архитектура](docs/architecture.md), [формат каталога](docs/services.md).

## Структура репозитория

```text
app/                 исходный код и services.json
config/example.env   безопасный пример окружения
docs/                техническая документация
tests/test_app.py    HTTP-тесты
.github/             шаблоны Issues и Pull Requests
.gitignore           исключения Git
requirements.txt     внешних зависимостей нет
README.md            входная точка документации
```

## Технологии и зависимости

Python 3.12, стандартная библиотека (`http.server`, `json`, `unittest`), Git и GitHub.
Для Linux требуются пакеты `python3`, `python3-venv`, `python3-pip`, `git`, `curl`.
`requirements.txt` намеренно содержит только комментарий: сторонние Python-пакеты не нужны.

## Запуск в Linux

1. Клонировать репозиторий и создать отдельное окружение.

```bash
git clone https://github.com/DaniellFierro/cloud-team-project.git
cd cloud-team-project
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

2. Задать параметры и запустить приложение.

```bash
export APP_TITLE="Cloud Service Catalog"
export HOST=127.0.0.1
export PORT=5000
python -m app.main
```

3. Во втором терминале проверить ответы.

```bash
curl -i http://127.0.0.1:5000/
curl -i http://127.0.0.1:5000/health
curl -i http://127.0.0.1:5000/api/services
```

Для остановки нажмите Ctrl+C в терминале сервера.

## Запуск в Windows PowerShell

Python и Git должны быть доступны в PATH. Активация окружения не обязательна.

```powershell
git clone https://github.com/DaniellFierro/cloud-team-project.git
cd cloud-team-project
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:APP_TITLE = "Cloud Service Catalog"
$env:HOST = "127.0.0.1"
$env:PORT = "5000"
.\.venv\Scripts\python.exe -m app.main
# Проверка из второго терминала
curl.exe -i http://127.0.0.1:5000/health
```

## Конфигурация

| Переменная | По умолчанию | Назначение |
|---|---|---|
| `APP_TITLE` | Cloud Service Catalog | Заголовок HTML; экранируется |
| `HOST` | 0.0.0.0 | Интерфейс прослушивания |
| `PORT` | 5000 | TCP-порт приложения |

`config/example.env` — образец; приложение не загружает `.env` автоматически.
Для проверки только на своём компьютере используйте `HOST=127.0.0.1`.
Если порт занят, задайте, например, `PORT=5050` и используйте тот же порт в запросах.
Для доступа к ВМ через проброс порта сервер внутри ВМ должен слушать `0.0.0.0`.

## Маршруты

| GET | Код | Результат |
|---|---|---|
| `/` | 200 | HTML-страница со ссылками |
| `/health` | 200 | `{"status": "ok"}` |
| `/api/services` | 200 | JSON с IaaS, PaaS, SaaS |
| Неизвестный путь | 404 | `{"error":"not found"}` |

`/health` проверяет доступность процесса, а не целостность каталога. Для проверки данных
обращайтесь к `/api/services`. Каталог должен существовать и содержать корректный JSON.

## Тестирование и разработка

```bash
python -m unittest discover -s tests -v
git diff --check
```

В Windows без активации замените `python` на `.\.venv\Scripts\python.exe`.
Проверяются три основных маршрута, 404, query string, экранирование HTML и заголовки.
Изменения оформляются через [Issues](https://github.com/DaniellFierro/cloud-team-project/issues)
и отдельные ветви. См. [порядок разработки](docs/git-workflow.md).

## Ограничения

Это учебный прототип без аутентификации, HTTPS и операций записи. Для производственного
размещения нужен подходящий серверный стек и дополнительные средства защиты.
Модуль [http.server](https://docs.python.org/3.12/library/http.server.html) не рекомендуется
Python для production. Секреты, токены и локальные `.env` не публикуются.

## Развертывание на виртуальной машине

Для Ubuntu установите `git python3 python3-pip python3-venv curl`, клонируйте этот
репозиторий и создайте `.venv`, как описано выше. В учебной ВМ пользователь — `daniil`.

```bash
.venv/bin/python -m pip install --no-index -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
sudo install -m 0644 config/cloud-catalog.service /etc/systemd/system/cloud-catalog.service
sudo systemctl daemon-reload
sudo systemctl enable --now cloud-catalog
curl --retry 5 --retry-connrefused --retry-delay 1 -fsS http://127.0.0.1:5000/health
```

Для другого имени пользователя исправьте пути и `User` в unit-файле до установки.
Служба запускает `.venv/bin/python -m app.main` с `HOST=0.0.0.0`, `PORT=5000`.
Windows обращается к `http://127.0.0.1:5000` через NAT VirtualBox в `10.0.2.15:5000`.
Полные команды обновления, диагностики и остановки: [развёртывание на ВМ](docs/vm-deployment.md).
