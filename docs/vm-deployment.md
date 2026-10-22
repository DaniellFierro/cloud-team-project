# Развёртывание на виртуальной машине

## Среда лабораторной работы

VirtualBox, Ubuntu Server 24.04.5 LTS, 4 ГБ RAM, 2 vCPU, диск 30 ГиБ.
Пользователь `daniil`, адрес NAT `10.0.2.15`. NAT-правила хоста Windows:
`127.0.0.1:2222 → 22`, `127.0.0.1:5000 → 5000`, `127.0.0.1:8080 → 8080`.
Эти правила ограничивают вход со стороны Windows локальным компьютером.
Адрес ВМ может измениться: проверяйте `ip -br addr`.

## Получение кода и окружение

```bash
sudo apt-get update
sudo apt-get install -y git python3 python3-pip python3-venv curl ca-certificates
cd ~
git clone https://github.com/DaniellFierro/cloud-team-project.git
cd cloud-team-project
python3 -m venv .venv
.venv/bin/python -m pip install --no-index -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
```

Внешних пакетов Python нет; `--no-index` достаточен для текущего requirements.txt.
Если зависимости будут добавлены, измените инструкцию установки вместе с ними.
Точка запуска: `.venv/bin/python -m app.main`.

## Запуск как служба

В `config/cloud-catalog.service` заданы пользователь и путь конкретной учебной ВМ.
На другой машине сначала измените `User`, `WorkingDirectory` и `ExecStart`.
Переменные не содержат секретов. Служба читает проект, но не может менять его файлы.

```bash
sudo install -m 0644 config/cloud-catalog.service /etc/systemd/system/cloud-catalog.service
sudo systemctl daemon-reload
sudo systemctl enable --now cloud-catalog
systemctl is-active cloud-catalog
systemctl status cloud-catalog --no-pager
ss -ltnp 'sport = :5000'
curl -i http://127.0.0.1:5000/health
curl -i http://10.0.2.15:5000/api/services
```

Из Windows: `curl.exe -i http://127.0.0.1:5000/health`.
Здесь `127.0.0.1` обозначает Windows, а NAT перенаправляет запрос в ВМ.
На самой ВМ тот же адрес означает гостевую Ubuntu. `0.0.0.0` — адрес привязки
сервера, а не адрес для открытия в браузере.

## Проверка, обновление и остановка

```bash
curl -i http://127.0.0.1:5000/
curl -i http://127.0.0.1:5000/health
curl -i http://127.0.0.1:5000/api/services
sudo journalctl -u cloud-catalog -n 20 --no-pager
git status --short
git pull --ff-only
.venv/bin/python -m unittest discover -s tests -v
sudo systemctl restart cloud-catalog
curl --retry 5 --retry-connrefused --retry-delay 1 -fsS http://127.0.0.1:5000/health
# Остановка и повторный запуск
sudo systemctl stop cloud-catalog
sudo systemctl start cloud-catalog
```

При локальных изменениях сначала сохраните их; не используйте принудительное сбрасывание.
После изменения unit-файла повторите install и daemon-reload.
При ошибке проверьте журнал, путь `.venv/bin/python`, интерфейс и порт.
Первый запуск ВМ не предоставил SSH; включение последовательного журнала и повторный
запуск позволили завершить cloud-init. Точная причина первой задержки не установлена.
Порт Windows 5000 занят NAT-правилом: для отдельного локального запуска в Windows
используйте другой порт, например 5050.

При первом запуске `is-active` уже возвращал `active`, но порт ещё не был открыт.
Первый HTTP-запрос получил отказ соединения; ограниченный повтор curl через секунду
получил HTTP 200. Статус процесса не заменяет проверку готовности приложения.

## Следующие шаги автоматизации

CI может проверять код и зависимости, а CD — доставлять версию, перезапускать службу,
проверять HTTP и возвращать предыдущую версию при ошибке. В данной работе эти действия
выполняются вручную; действующий CI/CD-конвейер не настроен.
