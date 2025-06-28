# BagBountyAuto 🎯

Автоматизированный фреймворк для багбаунти-разведки и поиска уязвимостей

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Быстрый старт

```bash
git clone https://github.com/Maksimqa322/BagBountyAuto.git
cd BagBountyAuto
./install.sh
./bagbounty_wrapper.sh example.com
```

## 📋 Возможности

- 🔍 **Автоматическая разведка** - поиск поддоменов, сбор URL, скачивание файлов
- 🧹 **Умная фильтрация** - удаление дубликатов и неинтересных файлов
- 📊 **Анализ уязвимостей** - поиск XSS, SQLi, LFI, SSRF, open redirect
- 🔬 **Активное сканирование** - nuclei, sqlmap, truffleHog
- 📁 **Организованные отчеты** - автоматическая сортировка по типам и датам
- ⏱️ **Статистика времени** - детальное отслеживание времени каждого этапа
- 🐳 **Docker поддержка** - готовые контейнеры
- 🐛 **Отладочные возможности** - детальное логирование и мониторинг зависаний

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

# Показать статистику времени
./bagbounty_wrapper.sh example.com --show-timing

# Показать сводку отчетов
./bagbounty_wrapper.sh example.com --show-summary
```

### Docker
```bash
# Сканирование
docker-compose run --rm bagbountyauto example.com

# Интерактивный режим
docker-compose run --rm bagbountyauto-shell
```

### Управление отчетами
```bash
# Сводка всех отчетов
python3 manage_reports.py summary

# Очистить старые отчеты
python3 manage_reports.py cleanup 30

# Показать отчеты домена
python3 manage_reports.py list example.com
```

### 🐛 Отладочные возможности

```bash
# Включить отладку
./bagbounty.py example.com --debug

# Сохранить логи в файл
./bagbounty.py example.com --log-file logs/debug.log

# Увеличить таймаут (по умолчанию 300с)
./bagbounty.py example.com --timeout 600

# Мониторинг зависших процессов
./bagbounty.py example.com --monitor-hanging

# Подробный вывод
./bagbounty.py example.com --verbose

# Полная отладка
./bagbounty.py example.com \
  --debug \
  --log-file logs/full_debug.log \
  --timeout 900 \
  --monitor-hanging \
  --verbose
```

**Уровни логирования:**
- `DEBUG` - максимальная детализация
- `INFO` - основная информация
- `WARNING` - предупреждения
- `ERROR` - только ошибки

## 📁 Структура отчетов

```
reports/
├── recon_reports/           # Отчеты разведки
├── analysis_reports/        # Анализ уязвимостей
├── vuln_scan_reports/       # Результаты сканирования
├── filtered_reports/        # Отфильтрованные данные
└── logs/                    # Логи выполнения
```

## 🔧 Инструменты

### Разведка
- **subfinder** - поиск поддоменов
- **httpx** - проверка живых хостов
- **waybackurls** - сбор URL из Wayback Machine
- **katana** - краулинг веб-сайтов

### Сканирование
- **nuclei** - сканирование уязвимостей
- **sqlmap** - тестирование SQL инъекций
- **truffleHog** - поиск секретов

## 📚 Документация

- [Руководство по отчетам](docs/REPORTS_GUIDE.md)
- [Руководство по отладке](docs/DEBUG_GUIDE.md)
- [Примеры использования](examples/)

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE) для деталей.


