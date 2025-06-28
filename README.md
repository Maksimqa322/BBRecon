# Bug Bounty Recon Automation

Автоматизированный скрипт для разведки в рамках Bug Bounty программ. Выполняет комплексный анализ целевого домена, включая поиск поддоменов, сбор URL, анализ файлов и генерацию отчетов.

## Возможности

- 🔍 **Поиск поддоменов** - автоматическое обнаружение поддоменов с помощью Subfinder
- 🌐 **Проверка доступности** - определение живых хостов с помощью httpx
- 📄 **Сбор URL** - извлечение URL с помощью GAU и Katana
- 🔒 **Анализ чувствительных файлов** - поиск потенциально уязвимых файлов
- 📁 **Скачивание файлов** - автоматическое скачивание JS, PHP и других файлов
- 📊 **Генерация отчетов** - создание подробных отчетов в формате Markdown

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd YA
```

2. Установите необходимые инструменты (см. [INSTALL.md](INSTALL.md)):
```bash
# Установка Go инструментов
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/lc/gau/v2/cmd/gau@latest
go install github.com/projectdiscovery/katana/cmd/katana@latest

# Добавьте в PATH
export PATH=$PATH:$(go env GOPATH)/bin
```

## Использование

```bash
# Базовое использование
python3 recon.py example.com

# Пример с реальным доменом
python3 recon.py google.com
```

## Структура результатов

После выполнения скрипта создается следующая структура:

```
recon-example.com/
├── subdomains/          # Найденные поддомены
│   ├── subdomains.txt   # Все поддомены
│   └── alive.txt        # Живые поддомены
├── urls/                # Собранные URL
│   ├── all_urls.txt     # Все URL
│   ├── sensitive_files.txt  # Чувствительные файлы
│   ├── param_urls.txt   # URL с параметрами
│   ├── js_files.txt     # JavaScript файлы
│   ├── php_files.txt    # PHP файлы
│   └── api_endpoints.txt # API эндпоинты
├── files/               # Скачанные файлы
│   ├── sensitive/       # Чувствительные файлы
│   ├── js/              # JavaScript файлы
│   └── php/             # PHP файлы
├── gau/                 # Результаты GAU
│   └── gau_urls.txt
├── katana/              # Результаты Katana
│   └── katana_urls.txt
├── logs/                # Логи выполнения
└── report_YYYYMMDD-HHMMSS.md  # Отчет
```

## Этапы выполнения

1. **Поиск поддоменов** - Subfinder находит все поддомены
2. **Проверка доступности** - httpx определяет живые хосты
3. **Сбор URL (GAU)** - извлечение URL из архивов
4. **Сбор URL (Katana)** - краулинг сайтов
5. **Обработка URL** - фильтрация и категоризация
6. **Скачивание файлов** - загрузка интересных файлов
7. **Генерация отчетов** - создание итогового отчета

## Настройки

Основные параметры можно изменить в начале файла `recon.py`:

```python
PORTS = "80,443,8080,8000,8888"  # Порты для проверки
THREADS = 200                    # Количество потоков
KATANA_DEPTH = 5                 # Глубина краулинга
BLACKLIST_EXT = "woff,css,png,svg,jpg,woff2,jpeg,gif"  # Исключаемые расширения
```

## Требования

- Python 3.6+
- Go 1.16+
- subfinder
- httpx
- gau
- katana
- wget, grep, sed


