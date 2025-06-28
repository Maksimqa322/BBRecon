#!/usr/bin/env python3
"""
Тестовый скрипт для проверки отладочных возможностей BagBountyAuto
"""

import sys
import os
from pathlib import Path

# Добавляем src в путь
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.debug_logger import init_debug_logger, get_debug_logger
from src.utils.common import run_command, print_status, print_success, print_error

def test_debug_logger():
    """Тестирует основные возможности отладки"""
    print_status("Тестирование системы отладки...")
    
    # Инициализация логгера
    debug_logger = init_debug_logger(
        debug_level='DEBUG',
        log_file='logs/test_debug.log',
        enable_console=True
    )
    
    debug_logger.info("Начало тестирования отладочной системы")
    debug_logger.debug("Это отладочное сообщение")
    debug_logger.warning("Это предупреждение")
    
    # Тест выполнения команды
    print_status("Тестирование выполнения команды...")
    result = run_command(
        "echo 'Тестовая команда' && sleep 2",
        debug_logger=debug_logger,
        timeout=10
    )
    
    if result:
        print_success("Команда выполнена успешно")
    else:
        print_error("Команда завершилась с ошибкой")
    
    # Тест зависшей команды
    print_status("Тестирование мониторинга зависаний...")
    debug_logger.info("Запуск команды, которая может зависнуть")
    
    # Симулируем зависшую команду
    result = run_command(
        "sleep 1 && echo 'Быстрая команда'",
        debug_logger=debug_logger,
        timeout=5
    )
    
    # Проверяем зависшие процессы
    hanging = debug_logger.check_hanging_processes()
    if hanging:
        print_error(f"Найдено зависших процессов: {len(hanging)}")
    else:
        print_success("Зависших процессов не найдено")
    
    # Тест исключений
    print_status("Тестирование обработки исключений...")
    try:
        raise ValueError("Тестовое исключение")
    except Exception as e:
        debug_logger.log_exception(e, "в тестовом скрипте")
    
    # Системная информация
    debug_logger.log_system_info()
    
    # Сводка
    debug_logger.print_summary()
    
    print_success("Тестирование отладки завершено")

def test_timeout():
    """Тестирует обработку таймаутов"""
    print_status("Тестирование обработки таймаутов...")
    
    debug_logger = init_debug_logger(
        debug_level='INFO',
        log_file='logs/test_timeout.log',
        enable_console=True
    )
    
    # Команда с коротким таймаутом
    result = run_command(
        "sleep 10",
        debug_logger=debug_logger,
        timeout=2  # Таймаут 2 секунды
    )
    
    if not result:
        print_success("Таймаут обработан корректно")
    else:
        print_error("Таймаут не сработал")
    
    debug_logger.print_summary()

def test_file_operations():
    """Тестирует операции с файлами"""
    print_status("Тестирование операций с файлами...")
    
    debug_logger = init_debug_logger(
        debug_level='DEBUG',
        log_file='logs/test_files.log',
        enable_console=True
    )
    
    from src.utils.common import check_file_exists, get_file_size, safe_file_operation
    
    # Создаем тестовый файл
    test_file = "test_file.txt"
    with open(test_file, 'w') as f:
        f.write("Тестовые данные")
    
    # Проверяем существование
    exists = check_file_exists(test_file, debug_logger)
    print_status(f"Файл существует: {exists}")
    
    # Получаем размер
    size = get_file_size(test_file, debug_logger)
    print_status(f"Размер файла: {size} байт")
    
    # Безопасная операция
    def read_file(filepath):
        with open(filepath, 'r') as f:
            return f.read()
    
    content = safe_file_operation(read_file, test_file, debug_logger)
    if content:
        print_success("Файл прочитан успешно")
    
    # Удаляем тестовый файл
    os.remove(test_file)
    
    debug_logger.print_summary()

def main():
    """Основная функция тестирования"""
    print_status("=== Тестирование отладочных возможностей BagBountyAuto ===")
    
    # Создаем директорию для логов
    os.makedirs('logs', exist_ok=True)
    
    try:
        test_debug_logger()
        print()
        
        test_timeout()
        print()
        
        test_file_operations()
        print()
        
        print_success("Все тесты завершены успешно!")
        
    except Exception as e:
        print_error(f"Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 