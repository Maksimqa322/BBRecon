# Руководство по отладке BagBountyAuto

Это руководство описывает отладочные возможности BagBountyAuto для локальной разработки и диагностики проблем.

## Обзор

Система отладки включает:
- Детальное логирование всех операций
- Мониторинг зависших процессов
- Отслеживание времени выполнения
- Сохранение логов в файлы
- Различные уровни детализации

## Опции отладки

### Основные флаги

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

# Уровень отладки
./bagbounty.py example.com --debug-level DEBUG
```

### Комбинированное использование

```bash
# Полная отладка с мониторингом
./bagbounty.py example.com \
  --debug \
  --log-file logs/full_debug.log \
  --timeout 900 \
  --monitor-hanging \
  --verbose
```

## Уровни логирования

- **DEBUG** - Максимальная детализация, все операции
- **INFO** - Основная информация о ходе выполнения
- **WARNING** - Предупреждения и потенциальные проблемы
- **ERROR** - Только ошибки

## Структура логов

### Автоматические имена файлов

При использовании `--debug` без указания `--log-file` создается файл:
```
logs/bagbounty_debug_YYYYMMDD_HHMMSS.log
```

### Формат логов

```
2024-01-15 14:30:25 - INFO - Запуск BagBountyAuto с отладкой
2024-01-15 14:30:25 - INFO - Домен: example.com
2024-01-15 14:30:25 - INFO - Опции: recon_only=False, skip_scan=False
2024-01-15 14:30:25 - INFO - Таймаут: 300с
2024-01-15 14:30:25 - INFO - Начало выполнения команды [cmd_1705323025123]: subfinder -d example.com -all -recursive -silent
2024-01-15 14:30:45 - INFO - Завершение команды [cmd_1705323025123] (УСПЕХ): subfinder -d example.com -all -recursive -silent
2024-01-15 14:30:45 - DEBUG - Время выполнения: 20.15с
```

## Мониторинг зависаний

### Автоматический мониторинг

При использовании `--monitor-hanging` система каждые 30 секунд проверяет активные процессы:

```
2024-01-15 14:35:25 - WARN - Команда [cmd_1705323025123] выполняется дольше 300с (325.1с): katana -list alive.txt -d 3
2024-01-15 14:35:25 - WARN - Найдено 1 зависших процессов
```

### Ручная проверка

В коде можно проверить зависшие процессы:

```python
from src.utils.debug_logger import get_debug_logger

debug_logger = get_debug_logger()
hanging = debug_logger.check_hanging_processes()
if hanging:
    print(f"Найдено {len(hanging)} зависших процессов")
```

## Отслеживание команд

### Автоматическое отслеживание

Все команды автоматически отслеживаются при включенной отладке:

```python
# В run_command и run_step
result = run_command("subfinder -d example.com", debug_logger=debug_logger)
```

### Ручное отслеживание

```python
from src.utils.debug_logger import get_debug_logger

debug_logger = get_debug_logger()
process_id = debug_logger.command_start("my_command", timeout=300)

try:
    # Выполнение команды
    result = execute_my_command()
    debug_logger.command_end(process_id, success=True, output=str(result))
except Exception as e:
    debug_logger.command_end(process_id, success=False, error=str(e))
```

## Обработка исключений

### Автоматическое логирование

```python
try:
    # Код, который может вызвать исключение
    risky_operation()
except Exception as e:
    debug_logger.log_exception(e, "в risky_operation")
```

### Ручное логирование

```python
debug_logger.error(f"Ошибка: {str(exception)}")
debug_logger.debug(f"Traceback: {traceback.format_exc()}")
```

## Операции с файлами

### Безопасные операции

```python
from src.utils.common import check_file_exists, get_file_size, safe_file_operation

# Проверка существования
exists = check_file_exists("file.txt", debug_logger)

# Получение размера
size = get_file_size("file.txt", debug_logger)

# Безопасная операция
def read_file(filepath):
    with open(filepath, 'r') as f:
        return f.read()

content = safe_file_operation(read_file, "file.txt", debug_logger)
```

## Системная информация

### Автоматический сбор

При инициализации логгера автоматически собирается системная информация:

```
2024-01-15 14:30:25 - INFO - === Системная информация ===
2024-01-15 14:30:25 - INFO - Python версия: 3.9.2
2024-01-15 14:30:25 - INFO - Платформа: linux
2024-01-15 14:30:25 - INFO - Рабочая директория: /home/user/BagBountyAuto
2024-01-15 14:30:25 - INFO - Время запуска: 2024-01-15 14:30:25
2024-01-15 14:30:25 - INFO - ОС: Linux 5.4.0
2024-01-15 14:30:25 - INFO - Архитектура: x86_64
```

### Ручной сбор

```python
debug_logger.log_system_info()
debug_logger.log_memory_usage()  # Требует psutil
```

## Сводки и статистика

### Автоматическая сводка

В конце выполнения выводится сводка:

```
2024-01-15 15:30:25 - INFO - === Сводка выполнения ===
2024-01-15 15:30:25 - INFO - Общее время: 3600.25с
2024-01-15 15:30:25 - INFO - Активных процессов: 0
2024-01-15 15:30:25 - INFO - Зависших процессов: 0
2024-01-15 15:30:25 - INFO - Файл лога: logs/bagbounty_debug_20240115_143025.log
```

### Ручная сводка

```python
summary = debug_logger.get_summary()
debug_logger.print_summary()
```

## Тестирование отладки

Запустите тестовый скрипт для проверки отладочных возможностей:

```bash
python3 test_debug.py
```

Этот скрипт проверит:
- Основные функции логирования
- Обработку таймаутов
- Операции с файлами
- Мониторинг зависаний

## Рекомендации по использованию

### Для разработки

```bash
# Максимальная отладка
./bagbounty.py example.com --debug --verbose --log-file logs/dev.log
```

### Для диагностики проблем

```bash
# Отладка с мониторингом зависаний
./bagbounty.py example.com --debug --monitor-hanging --timeout 600
```

### Для продакшена

```bash
# Минимальная отладка, только ошибки
./bagbounty.py example.com --log-file logs/prod.log --debug-level ERROR
```

## Интеграция в код

### Добавление отладки в новые модули

```python
from src.utils.debug_logger import get_debug_logger

def my_function(debug_logger=None):
    if debug_logger:
        debug_logger.info("Начало выполнения my_function")
    
    # Ваш код
    
    if debug_logger:
        debug_logger.info("my_function завершена успешно")
```

### Использование декораторов

```python
from src.utils.debug_logger import debug_command, timeout_monitor

@debug_command
def my_command():
    # Команда будет автоматически отслеживаться
    pass

@timeout_monitor(300)
def long_running_function():
    # Функция с таймаутом 5 минут
    pass
```

## Устранение неполадок

### Логи не создаются

1. Проверьте права на запись в директорию
2. Убедитесь, что директория `logs/` существует
3. Проверьте, что `--debug` или `--log-file` указаны

### Команды зависают

1. Увеличьте таймаут: `--timeout 900`
2. Включите мониторинг: `--monitor-hanging`
3. Проверьте логи на наличие ошибок

### Слишком много логов

1. Уменьшите уровень: `--debug-level INFO`
2. Отключите консольный вывод (уберите `--verbose`)
3. Используйте только файловое логирование

## Примеры использования

### Диагностика медленной разведки

```bash
./bagbounty.py slow-domain.com \
  --debug \
  --log-file logs/slow_recon.log \
  --timeout 1800 \
  --monitor-hanging \
  --recon-only
```

### Отладка сканирования

```bash
./bagbounty.py target.com \
  --debug \
  --log-file logs/scan_debug.log \
  --timeout 600 \
  --skip-scan
```

### Мониторинг продакшена

```bash
./bagbounty.py production.com \
  --log-file logs/prod.log \
  --debug-level WARNING \
  --timeout 1200
``` 