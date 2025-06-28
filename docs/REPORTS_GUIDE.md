# 📊 Руководство по управлению отчетами

## Обзор

BagBountyAuto теперь использует организованную систему отчетов, которая автоматически сортирует все результаты по типам, доменам и датам, предотвращая засорение рабочей директории.

## 🏗️ Структура отчетов

```
reports/
├── recon_reports/           # Отчеты разведки
│   └── example.com/
│       └── 2024-01-15/
│           └── recon_report_20240115-143022.md
├── analysis_reports/        # Отчеты анализа уязвимостей
│   └── example.com/
│       └── 2024-01-15/
│           └── vulnerability_report.md
├── vuln_scan_reports/       # Отчеты активного сканирования
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

## 🚀 Использование

### Автоматическая организация

При запуске основного скрипта отчеты автоматически организуются:

```bash
# Обычный запуск - отчеты сохраняются в reports/
python3 bagbounty.py example.com

# Указать другую папку для отчетов
python3 bagbounty.py example.com --reports-dir /path/to/reports

# Очистить старые отчеты перед запуском
python3 bagbounty.py example.com --cleanup-reports

# Показать сводку в конце
python3 bagbounty.py example.com --show-summary
```

### Управление отчетами

```bash
# Показать сводку всех отчетов
python3 manage_reports.py summary

# Очистить отчеты старше 30 дней
python3 manage_reports.py cleanup 30

# Принудительная очистка без подтверждения
python3 manage_reports.py cleanup 30 --force

# Организовать существующие отчеты для домена
python3 manage_reports.py organize example.com

# Показать отчеты для конкретного домена
python3 manage_reports.py list example.com

# Настроить новую папку для отчетов
python3 manage_reports.py setup --reports-dir /path/to/reports
```

## ⚙️ Настройка

### Переменные окружения

```bash
# Указать папку для отчетов по умолчанию
export BAGBOUNTY_REPORTS_DIR="/path/to/reports"
```

### Конфигурация в config/settings.py

```python
REPORTS_CONFIG = {
    'base_dir': 'reports',           # Базовая папка
    'max_age_days': 30,              # Максимальный возраст отчетов
    'cleanup_enabled': True,         # Включить автоочистку
    'organize_by_date': True,        # Организация по дате
    'organize_by_domain': True,      # Организация по домену
}

REPORTS_STRUCTURE = {
    'recon': 'recon_reports',
    'analysis': 'analysis_reports', 
    'vuln_scan': 'vuln_scan_reports',
    'filtered': 'filtered_reports',
    'logs': 'logs'
}
```

## 🔧 Миграция существующих отчетов

Если у вас есть старые отчеты в формате `recon-example.com/`, их можно автоматически организовать:

```bash
# Организовать все существующие отчеты
python3 manage_reports.py organize example.com

# Или запустить основной скрипт - он автоматически переместит отчеты
python3 bagbounty.py example.com
```

## 📋 Типы отчетов

### Recon Reports (Разведка)
- Отчеты о найденных поддоменах
- Статистика собранных URL
- Результаты работы subfinder, httpx, waybackurls, katana

### Analysis Reports (Анализ)
- Анализ URL на потенциальные уязвимости
- Классификация по типам уязвимостей
- Статистика по паттернам

### Vuln Scan Reports (Сканирование уязвимостей)
- Результаты sqlmap
- Отчеты nuclei
- Результаты truffleHog
- Ручное тестирование payloads

### Filtered Reports (Фильтрация)
- Отфильтрованные URL
- Очищенные от дубликатов результаты
- URL с параметрами

## 🗑️ Очистка отчетов

### Автоматическая очистка
- По умолчанию отчеты старше 30 дней удаляются автоматически
- Можно настроить период в конфигурации

### Ручная очистка
```bash
# Очистить отчеты старше 7 дней
python3 manage_reports.py cleanup 7

# Очистить отчеты старше 60 дней
python3 manage_reports.py cleanup 60
```

## 📊 Мониторинг

### Сводка отчетов
```bash
python3 manage_reports.py summary
```

Вывод включает:
- Общее количество файлов
- Общий размер в MB
- Распределение по типам отчетов
- Распределение по доменам

### Просмотр отчетов домена
```bash
python3 manage_reports.py list example.com
```

Показывает:
- Все отчеты для указанного домена
- Размер каждого файла
- Организацию по типам

## 🔒 Безопасность

- Отчеты содержат конфиденциальную информацию
- Папка `reports/` добавлена в `.gitignore`
- Рекомендуется хранить отчеты в защищенном месте
- Регулярно очищайте старые отчеты

## 🐛 Устранение неполадок

### Проблема: Отчеты не создаются
```bash
# Проверьте права доступа
ls -la reports/

# Создайте папку вручную
mkdir -p reports/
```

### Проблема: Ошибки при перемещении файлов
```bash
# Проверьте свободное место
df -h

# Проверьте права на запись
ls -la
```

### Проблема: Неправильная организация
```bash
# Пересоздайте структуру
python3 manage_reports.py setup

# Организуйте заново
python3 manage_reports.py organize example.com
``` 