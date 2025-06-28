# BagBountyAuto

🚀 **Автоматизированный фреймворк для багбаунти-разведки и поиска уязвимостей**

Современный инструмент для комплексного анализа целевых доменов, включающий разведку, фильтрацию, анализ и активное тестирование уязвимостей.

## ✨ Возможности

- 🔍 **Автоматическая разведка** - поиск поддоменов, сбор URL, скачивание файлов
- 🧹 **Умная фильтрация** - удаление дубликатов, мусора, неинтересных файлов
- 📊 **Анализ уязвимостей** - поиск потенциальных XSS, SQLi, LFI, SSRF, open redirect
- 🔬 **Активное сканирование** - тестирование с помощью nuclei, sqlmap, truffleHog
- 📋 **Современный интерфейс** - цветной вывод, прогресс-бары, детальные отчеты
- 🐳 **Docker поддержка** - готовые контейнеры для быстрого развертывания

## 🚀 Быстрый старт

### Автоматическая установка (Ubuntu/Debian)

```bash
# Клонируйте репозиторий
git clone https://github.com/Maksimqa322/BBRecon.git
cd BBRecon

# Запустите автоматическую установку
./install.sh

# Запустите сканирование
python3 bagbounty.py example.com
```

### Docker установка

```bash
# Сборка и запуск контейнера
docker-compose up --build

# Или интерактивный режим
docker-compose run --rm bagbountyauto-shell

# Запуск в контейнере
docker run -it --rm -v $(pwd)/results:/app/results bagbountyauto python3 bagbounty.py example.com
```

## 📁 Структура проекта

```
BagBountyAuto/
├── src/                    # Исходный код
│   ├── recon/             # Модуль разведки
│   ├── filter/            # Модуль фильтрации
│   ├── analyze/           # Модуль анализа
│   ├── scanner/           # Модуль сканирования
│   └── utils/             # Общие утилиты
├── config/                # Конфигурация
├── docs/                  # Документация
├── examples/              # Примеры использования
├── tests/                 # Тесты
├── bagbounty.py          # Главный скрипт запуска
├── install.sh            # Автоматический установщик
├── Dockerfile            # Docker образ
└── docker-compose.yml    # Docker Compose
```

## 🎯 Использование

### Основные команды

```bash
# Полный цикл сканирования
python3 bagbounty.py example.com

# Только разведка
python3 bagbounty.py example.com --recon-only

# Без активного сканирования
python3 bagbounty.py example.com --skip-scan

# С ограничением потоков
python3 bagbounty.py example.com --threads 5

# Проверка зависимостей
python3 bagbounty.py --check-deps
```

### Результаты

После выполнения создается структура:

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
├── analysis/            # Результаты анализа
├── katana/              # Результаты Katana
├── waybackurls/         # Результаты waybackurls
├── logs/                # Логи выполнения
└── report_YYYYMMDD-HHMMSS.md  # Отчёт
```

## 🛠️ Требования

- **Python 3.8+**
- **Go 1.16+**
- **subfinder, httpx, waybackurls, katana, nuclei, sqlmap, trufflehog**

## 📚 Документация

- [Установка](INSTALL.md) - подробные инструкции по установке
- [Примеры](examples/) - примеры использования
- [Конфигурация](config/) - настройки и параметры

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE) файл.

## ⚠️ Отказ от ответственности

Этот инструмент предназначен только для образовательных целей и тестирования собственных систем. Используйте ответственно и в соответствии с законодательством.


