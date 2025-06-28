# BagBountyAuto

Автоматизированный фреймворк для багбаунти-разведки и поиска уязвимостей. Включает комплексные инструменты для сбора информации, фильтрации, анализа и активного тестирования.

## Быстрая установка (Ubuntu/Debian)

```bash
# Клонируйте репозиторий
git clone https://github.com/Maksimqa322/BBRecon.git
cd BBRecon

# Запустите автоматическую установку
./install.sh
```

## Docker установка

```bash
# Сборка и запуск контейнера
docker-compose up --build

# Или интерактивный режим
docker-compose run --rm bagbountyauto-shell

# Запуск в контейнере
docker run -it --rm -v $(pwd)/results:/app/results bagbountyauto python3 run_all.py example.com
```

## Основные скрипты

- **recon.py** — автоматическая разведка домена: поиск поддоменов, сбор URL (waybackurls, katana), скачивание файлов, первичный анализ.
- **filter_recon.py** — фильтрация и очистка URL: удаление дубликатов, мусора, 404, неинтересных файлов.
- **analyze.py** — анализ собранных URL на XSS, SQLi, LFI, SSRF, open redirect и чувствительные файлы.
- **vuln_scanner.py** — активное сканирование: поиск секретов, тестирование параметров на LFI, SSRF, SQLi, XSS и др. с помощью sqlmap, nuclei, truffleHog и ручных payloads.

## Быстрый старт

```bash
python3 run_all.py <домен>
```

## Структура результатов

После выполнения скрипта создаётся следующая структура:

```
recon-<домен>/
├── subdomains/          # Найденные поддомены
│   ├── subdomains.txt   # Все поддомены
│   └── alive.txt        # Живые поддомены
├── urls/                # Собранные URL
│   ├── all_urls.txt     # Все URL
│   ├── sensitive_files.txt  # Чувствительные файлы
│   ├── param_urls.txt   # URL с параметрами
│   ├── js_files.txt     # JavaScript файлы
│   ├── php_files.txt    # PHP файлы
│   └── api_endpoints.txt # API endpoints
├── files/               # Скачанные файлы
│   ├── sensitive/       # Чувствительные файлы
│   ├── js/              # JavaScript файлы
│   └── php/             # PHP файлы
├── katana/              # Результаты Katana
│   └── katana_urls.txt
├── waybackurls/         # Результаты waybackurls
│   └── waybackurls_urls.txt
├── logs/                # Логи выполнения
└── report_YYYYMMDD-HHMMSS.md  # Отчёт
```

## Требования

- Python 3.8+
- Go 1.16+
- subfinder, httpx, waybackurls, katana, nuclei, sqlmap, trufflehog, wget, grep, sed, curl

## Установка и инструкции — см. INSTALL.md


