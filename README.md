# BagBountyAuto 🎯

Автоматизированный фреймворк для багбаунти-разведки и поиска уязвимостей

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Быстрый старт

```bash
# Клонирование репозитория
git clone https://github.com/your-username/BagBountyAuto.git
cd BagBountyAuto

# Установка зависимостей
./install.sh

# Запуск полного сканирования
python3 bagbounty.py example.com
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
├── reports/               # 📊 Организованные отчеты
├── bagbounty.py          # Главный скрипт запуска
├── manage_reports.py     # 🆕 Управление отчетами
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

# Указать папку для отчетов
python3 bagbounty.py example.com --reports-dir /path/to/reports

# Очистить старые отчеты перед запуском
python3 bagbounty.py example.com --cleanup-reports

# Показать сводку отчетов в конце
python3 bagbounty.py example.com --show-summary

# Проверка зависимостей
python3 bagbounty.py --check-deps
```

### 🆕 Управление отчетами

```bash
# Показать сводку всех отчетов
python3 manage_reports.py summary

# Очистить отчеты старше 30 дней
python3 manage_reports.py cleanup 30

# Организовать существующие отчеты для домена
python3 manage_reports.py organize example.com

# Настроить папку для отчетов
python3 manage_reports.py setup --reports-dir /path/to/reports

# Показать отчеты для конкретного домена
python3 manage_reports.py list example.com
```

### Результаты

После выполнения создается организованная структура отчетов:

```
reports/
├── recon_reports/           # Отчеты разведки
│   └── example.com/
│       └── 2024-01-15/
│           └── recon_report_20240115-143022.md
├── analysis_reports/        # Отчеты анализа
│   └── example.com/
│       └── 2024-01-15/
│           └── vulnerability_report.md
├── vuln_scan_reports/       # Отчеты сканирования уязвимостей
│   └── example.com/
│       └── 2024-01-15/
│           ├── sqlmap_report_*.txt
│           ├── nuclei_*.txt
│           └── vulnerability_scan_report_*.md
├── filtered_reports/        # Отфильтрованные результаты
│   └── example.com/
│       └── 2024-01-15/
│           └── filtered_urls.txt
└── logs/                    # Логи выполнения
    └── execution_logs.txt
```

## 🛠️ Требования

- **Python 3.8+**
- **Go 1.16+**
- **subfinder, httpx, waybackurls, katana, nuclei, sqlmap, trufflehog**

## 📚 Документация

- [Установка](INSTALL.md) - подробные инструкции по установке
- [Примеры](examples/) - примеры использования
- [Конфигурация](config/) - настройки и параметры

## 🔧 Настройка отчетов

### Переменные окружения

```bash
# Указать папку для отчетов
export BAGBOUNTY_REPORTS_DIR="/path/to/reports"

# Запуск с новой папкой
python3 bagbounty.py example.com
```

### Конфигурация в settings.py

```python
REPORTS_CONFIG = {
    'base_dir': 'reports',           # Базовая папка
    'max_age_days': 30,              # Максимальный возраст отчетов
    'cleanup_enabled': True,         # Автоочистка
    'organize_by_date': True,        # Организация по дате
    'organize_by_domain': True,      # Организация по домену
}
```

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE) файл.

## ⚠️ Отказ от ответственности

Этот инструмент предназначен только для образовательных целей и тестирования собственных систем. Используйте ответственно и в соответствии с законодательством.


