# Cloud Service Catalog

Учебный каталог облачных моделей IaaS, PaaS и SaaS.

**Автор:** Сазонов Даниил Евгеньевич, ДОТ2026_ИСР262дк, GitHub DaniellFierro.
Автор выполняет разработку, документирование и самопроверку индивидуально.

## Структура

- app/ — HTTP-сервер и JSON-каталог.
- tests/ — шесть автоматических HTTP-тестов.
- config/ — безопасный пример переменных окружения.
- docs/ — архитектура и правила Git.
- .github/ — шаблоны задач и Pull Requests.

## Запуск и проверка

Требуется Python 3.12. Внешних библиотек нет.

```bash
python -m app.main
# в другом терминале
python -m unittest discover -s tests -v
curl http://127.0.0.1:5000/health
```

## Выполненные задачи

1. Приложение и тесты — feature/issue-1-app.
2. Архитектура и её уточнение после самопроверки — feature/issue-2-architecture.
3. Конфигурация и процесс разработки — feature/issue-3-team-config.

[Архитектура](docs/architecture.md) · [Git workflow](docs/git-workflow.md)

