# BagBountyAuto 🎯

Автоматизированный фреймворк для багбаунти-разведки и поиска уязвимостей

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Быстрый старт

### Локальная установка
```bash
git clone https://github.com/Maksimqa322/BagBountyAuto.git
cd BagBountyAuto
./install.sh
./bagbounty_wrapper.sh example.com
```

### Docker
```bash
git clone https://github.com/Maksimqa322/BagBountyAuto.git
cd BagBountyAuto
docker-compose run --rm bagbountyauto example.com
```

## 📋 Возможности

- 🔍 **Автоматическая разведка** - поиск поддоменов, сбор URL, скачивание файлов
- 🧹 **Умная фильтрация** - удаление дубликатов и неинтересных файлов
- 📊 **Анализ уязвимостей** - поиск XSS, SQLi, LFI, SSRF, open redirect
- 🔬 **Активное сканирование** - nuclei, sqlmap, truffleHog
- 📁 **Организованные отчеты** - автоматическая сортировка по типам и датам
- 🐳 **Docker поддержка** - готовые контейнеры

## 🛠️ Установка

### Требования
- Python 3.8+
- Go 1.16+
- Ruby (для wayback_machine_downloader)

### Варианты установки

**Рекомендуемый (виртуальное окружение):**
```bash
./install.sh
./bagbounty_wrapper.sh example.com
```

**Альтернативный (глобальная установка):**
```bash
./install_legacy.sh
python3 bagbounty.py example.com
```

**Docker:**
```bash
docker-compose run --rm bagbountyauto example.com
```

## 🎯 Использование

### Основные команды
```bash
# Полное сканирование
./bagbounty_wrapper.sh example.com

# Только разведка
./bagbounty_wrapper.sh example.com --recon-only

# Без активного сканирования
./bagbounty_wrapper.sh example.com --skip-scan

# С ограничением потоков
./bagbounty_wrapper.sh example.com --threads 5

# Указать папку для отчетов
./bagbounty_wrapper.sh example.com --reports-dir /path/to/reports

# Очистить старые отчеты
./bagbounty_wrapper.sh example.com --cleanup-reports

# Показать сводку
./bagbounty_wrapper.sh example.com --show-summary
```

### Управление отчетами
```bash
# Сводка всех отчетов
python3 manage_reports.py summary

# Очистить отчеты старше 30 дней
python3 manage_reports.py cleanup 30

# Организовать отчеты для домена
python3 manage_reports.py organize example.com

# Показать отчеты домена
python3 manage_reports.py list example.com
```

### Docker команды
```bash
# Сканирование
docker-compose run --rm bagbountyauto example.com

# Интерактивный режим
docker-compose run --rm bagbountyauto-shell

# Просмотр отчетов
docker-compose run --rm bagbountyauto-reports
```

## 📁 Структура отчетов

```
reports/
├── recon_reports/           # Отчеты разведки
│   └── example.com/
│       └── 2024-01-15/
├── analysis_reports/        # Анализ уязвимостей
├── vuln_scan_reports/       # Результаты сканирования
├── filtered_reports/        # Отфильтрованные данные
└── logs/                    # Логи выполнения
```

## ⚙️ Настройка

### Переменные окружения
```bash
export BAGBOUNTY_REPORTS_DIR="/path/to/reports"
```

### Конфигурация
```python
# config/settings.py
REPORTS_CONFIG = {
    'base_dir': 'reports',
    'max_age_days': 30,
    'cleanup_enabled': True,
    'organize_by_date': True,
    'organize_by_domain': True,
}
```

## 🔧 Инструменты

### Разведка
- **subfinder** - поиск поддоменов
- **httpx** - проверка живых хостов
- **waybackurls** - сбор URL из Wayback Machine
- **katana** - краулинг веб-сайтов
- **wayback_machine_downloader** - скачивание архивов

### Сканирование
- **nuclei** - сканирование уязвимостей
- **sqlmap** - тестирование SQL инъекций
- **truffleHog** - поиск секретов

## 📚 Документация

- [Руководство по отчетам](docs/REPORTS_GUIDE.md)
- [Примеры использования](examples/)
- [Конфигурация](config/)

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE) файл.

## ⚠️ Отказ от ответственности

Этот инструмент предназначен только для образовательных целей и тестирования собственных систем. Используйте ответственно и в соответствии с законодательством.


