#!/usr/bin/env python3
"""
BagBountyAuto - Главный скрипт запуска
Автоматизированный фреймворк для багбаунти-разведки и поиска уязвимостей
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
import time

# Добавляем src в путь
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.common import print_status, print_success, print_error, print_warning, time_tracker
from src.utils.reports_manager import setup_reports_for_domain, ReportsManager
from src.utils.debug_logger import init_debug_logger, get_debug_logger

def run_step(command, step_name, cwd=None, debug_logger=None, timeout=300):
    """Выполняет этап и обрабатывает ошибки"""
    time_tracker.start_stage(step_name)
    
    if debug_logger:
        process_id = debug_logger.command_start(command, timeout)
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=cwd,
            timeout=timeout
        )
        time_tracker.end_stage(step_name)
        
        if debug_logger:
            debug_logger.command_end(process_id, success=True, output=result.stdout)
        
        if result.stdout:
            print(result.stdout)
        return True
        
    except subprocess.TimeoutExpired as e:
        time_tracker.end_stage(step_name)
        error_msg = f"Таймаут на этапе: {step_name} (>{timeout}с)"
        print_error(error_msg)
        
        if debug_logger:
            debug_logger.command_end(process_id, success=False, error=f"Таймаут: {timeout}с")
            debug_logger.warning(f"Команда зависла: {command}")
        
        return False
        
    except subprocess.CalledProcessError as e:
        time_tracker.end_stage(step_name)
        print_error(f"Ошибка на этапе: {step_name}")
        
        if debug_logger:
            debug_logger.command_end(process_id, success=False, error=str(e))
            if e.stdout:
                debug_logger.debug(f"STDOUT: {e.stdout}")
            if e.stderr:
                debug_logger.error(f"STDERR: {e.stderr}")
        
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
        
    except Exception as e:
        time_tracker.end_stage(step_name)
        error_msg = f"Неожиданная ошибка в {step_name}: {e}"
        print_error(error_msg)
        
        if debug_logger:
            debug_logger.command_end(process_id, success=False, error=str(e))
            debug_logger.log_exception(e, f"в этапе {step_name}")
        
        return False

def check_dependencies(debug_logger=None):
    """Проверяет наличие основных зависимостей"""
    time_tracker.start_stage("Проверка зависимостей")
    print_status("Проверка зависимостей...")
    
    if debug_logger:
        debug_logger.info("Начало проверки зависимостей")
    
    required_tools = ['python3', 'subfinder', 'httpx', 'waybackurls', 'katana']
    missing = []
    
    for tool in required_tools:
        try:
            if debug_logger:
                debug_logger.debug(f"Проверка инструмента: {tool}")
            
            subprocess.run([tool, '--help'], capture_output=True, timeout=5)
            print_success(f"{tool} - OK")
            
            if debug_logger:
                debug_logger.debug(f"{tool} найден и работает")
                
        except Exception as e:
            print_error(f"{tool} - НЕ НАЙДЕН")
            missing.append(tool)
            
            if debug_logger:
                debug_logger.error(f"{tool} не найден: {e}")
    
    if missing:
        print_warning(f"Отсутствуют инструменты: {', '.join(missing)}")
        print_warning("Запустите ./install.sh для установки")
        
        if debug_logger:
            debug_logger.warning(f"Отсутствуют инструменты: {missing}")
        
        time_tracker.end_stage("Проверка зависимостей")
        return False
    
    if debug_logger:
        debug_logger.info("Все зависимости проверены успешно")
    
    time_tracker.end_stage("Проверка зависимостей")
    return True

def main():
    parser = argparse.ArgumentParser(
        description='BagBountyAuto - Автоматизированный фреймворк для багбаунти',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s example.com                    # Полный цикл
  %(prog)s example.com --recon-only       # Только разведка
  %(prog)s example.com --skip-scan        # Без активного сканирования
  %(prog)s example.com --threads 5        # С ограничением потоков
  %(prog)s example.com --reports-dir /path/to/reports  # Указать папку для отчетов
  
Опции отладки:
  %(prog)s example.com --debug            # Включить отладку
  %(prog)s example.com --log-file logs/debug.log  # Сохранить логи в файл
  %(prog)s example.com --timeout 600      # Увеличить таймаут до 10 минут
  %(prog)s example.com --monitor-hanging  # Мониторинг зависших процессов
  %(prog)s example.com --verbose          # Подробный вывод
        """
    )
    
    parser.add_argument('domain', help='Целевой домен (например: example.com)')
    parser.add_argument('--recon-only', action='store_true', help='Только разведка')
    parser.add_argument('--skip-scan', action='store_true', help='Пропустить активное сканирование')
    parser.add_argument('--threads', type=int, default=3, help='Количество потоков (по умолчанию: 3)')
    parser.add_argument('--output-dir', help='Директория для результатов')
    parser.add_argument('--reports-dir', help='Директория для отчетов (по умолчанию: reports/)')
    parser.add_argument('--check-deps', action='store_true', help='Проверить зависимости и выйти')
    parser.add_argument('--cleanup-reports', action='store_true', help='Очистить старые отчеты перед запуском')
    parser.add_argument('--show-summary', action='store_true', help='Показать сводку отчетов в конце')
    parser.add_argument('--show-timing', action='store_true', help='Показать статистику времени выполнения')
    
    # Новые опции отладки
    parser.add_argument('--debug', action='store_true', help='Включить режим отладки')
    parser.add_argument('--log-file', help='Файл для сохранения логов отладки')
    parser.add_argument('--timeout', type=int, default=300, help='Таймаут для команд в секундах (по умолчанию: 300)')
    parser.add_argument('--monitor-hanging', action='store_true', help='Мониторинг зависших процессов')
    parser.add_argument('--verbose', action='store_true', help='Подробный вывод')
    parser.add_argument('--debug-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Уровень отладки (по умолчанию: INFO)')
    
    args = parser.parse_args()
    
    # Инициализация отладки
    debug_logger = None
    if args.debug or args.log_file or args.verbose:
        log_file = args.log_file
        if not log_file and args.debug:
            # Создаем автоматическое имя файла лога
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"logs/bagbounty_debug_{timestamp}.log"
        
        debug_level = 'DEBUG' if args.debug else args.debug_level
        enable_console = args.verbose or args.debug
        
        debug_logger = init_debug_logger(
            debug_level=debug_level,
            log_file=log_file,
            enable_console=enable_console
        )
        
        debug_logger.info(f"Запуск BagBountyAuto с отладкой")
        debug_logger.info(f"Домен: {args.domain}")
        debug_logger.info(f"Опции: recon_only={args.recon_only}, skip_scan={args.skip_scan}")
        debug_logger.info(f"Таймаут: {args.timeout}с")
    
    # Начинаем отсчет общего времени
    time_tracker.start_total()
    
    if args.check_deps:
        check_dependencies(debug_logger)
        time_tracker.end_total()
        
        if debug_logger:
            debug_logger.print_summary()
        
        return
    
    # Проверка зависимостей
    if not check_dependencies(debug_logger):
        time_tracker.end_total()
        
        if debug_logger:
            debug_logger.error("Проверка зависимостей не прошла")
            debug_logger.print_summary()
        
        return
    
    # Настройка менеджера отчетов
    time_tracker.start_stage("Настройка системы отчетов")
    print_status("Настройка системы отчетов...")
    
    if debug_logger:
        debug_logger.info("Настройка системы отчетов")
    
    reports_manager = setup_reports_for_domain(args.domain, args.reports_dir)
    time_tracker.end_stage("Настройка системы отчетов")
    
    # Очистка старых отчетов если запрошено
    if args.cleanup_reports:
        time_tracker.start_stage("Очистка старых отчетов")
        print_status("Очистка старых отчетов...")
        
        if debug_logger:
            debug_logger.info("Очистка старых отчетов")
        
        reports_manager.cleanup_old_reports()
        time_tracker.end_stage("Очистка старых отчетов")
    
    # Настройка путей
    recon_out = f"recon-{args.domain}"
    all_urls_file = f"{recon_out}/urls/all_urls.txt"
    filtered_out = f"filtered-{args.domain}.txt"
    
    # Создание директории для результатов если указана
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        os.chdir(args.output_dir)
        
        if debug_logger:
            debug_logger.info(f"Изменена рабочая директория на: {args.output_dir}")
    
    print_status(f"Начало работы с доменом: {args.domain}")
    
    # Мониторинг зависших процессов
    if args.monitor_hanging and debug_logger:
        import threading
        def monitor_hanging():
            while True:
                time.sleep(30)  # Проверяем каждые 30 секунд
                hanging = debug_logger.check_hanging_processes()
                if hanging:
                    debug_logger.warning(f"Найдено {len(hanging)} зависших процессов")
        
        monitor_thread = threading.Thread(target=monitor_hanging, daemon=True)
        monitor_thread.start()
        debug_logger.info("Запущен мониторинг зависших процессов")
    
    # 1. Разведка
    if not run_step(f"python3 src/recon/recon.py {args.domain}", "Разведка домена", 
                   debug_logger=debug_logger, timeout=args.timeout):
        print_error("Разведка завершилась с ошибкой")
        
        if debug_logger:
            debug_logger.error("Разведка завершилась с ошибкой")
        
        time_tracker.end_total()
        
        if debug_logger:
            debug_logger.print_summary()
        
        return
    
    if args.recon_only:
        print_success("Режим 'только разведка' - завершение")
        
        if debug_logger:
            debug_logger.info("Завершение в режиме 'только разведка'")
        
        # Организуем отчеты разведки
        time_tracker.start_stage("Организация отчетов")
        reports_manager.move_existing_reports(args.domain)
        time_tracker.end_stage("Организация отчетов")
        
        if args.show_summary:
            reports_manager.print_summary()
        
        # Показываем статистику времени
        if args.show_timing:
            time_tracker.print_summary()
        
        time_tracker.end_total()
        
        if debug_logger:
            debug_logger.print_summary()
        
        return
    
    # 2. Фильтрация
    if not run_step(f"python3 src/filter/filter_recon.py {all_urls_file}", "Фильтрация результатов",
                   debug_logger=debug_logger, timeout=args.timeout):
        print_error("Фильтрация завершилась с ошибкой")
        
        if debug_logger:
            debug_logger.error("Фильтрация завершилась с ошибкой")
        
        time_tracker.end_total()
        
        if debug_logger:
            debug_logger.print_summary()
        
        return
    
    # 3. Анализ
    if not run_step(f"python3 src/analyze/analyze.py {args.domain}", "Анализ URL на уязвимости",
                   debug_logger=debug_logger, timeout=args.timeout):
        print_warning("Анализ завершился с ошибкой, продолжаем...")
        
        if debug_logger:
            debug_logger.warning("Анализ завершился с ошибкой, продолжаем")
    
    # 4. Активное сканирование (если не пропущено)
    if not args.skip_scan:
        scan_cmd = f"python3 src/scanner/vuln_scanner.py {recon_out} --threads {args.threads}"
        if not run_step(scan_cmd, "Активное сканирование уязвимостей",
                       debug_logger=debug_logger, timeout=args.timeout):
            print_warning("Активное сканирование завершилось с ошибкой")
            
            if debug_logger:
                debug_logger.warning("Активное сканирование завершилось с ошибкой")
    
    # Организуем все отчеты
    time_tracker.start_stage("Организация отчетов")
    print_status("Организация отчетов...")
    
    if debug_logger:
        debug_logger.info("Организация отчетов")
    
    reports_manager.move_existing_reports(args.domain)
    time_tracker.end_stage("Организация отчетов")
    
    print_success("Все этапы завершены!")
    print_status(f"Отчеты организованы в: {reports_manager.base_dir}/")
    
    if debug_logger:
        debug_logger.info("Все этапы завершены успешно")
    
    # Показываем статистику
    try:
        with open(f"{recon_out}/urls/all_urls.txt", 'r') as f:
            urls_count = sum(1 for _ in f)
        print_status(f"Всего URL: {urls_count}")
        
        if debug_logger:
            debug_logger.info(f"Найдено URL: {urls_count}")
    except Exception as e:
        if debug_logger:
            debug_logger.warning(f"Не удалось подсчитать URL: {e}")
    
    # Показываем сводку отчетов если запрошено
    if args.show_summary:
        reports_manager.print_summary()
    
    # Показываем статистику времени выполнения
    if args.show_timing:
        time_tracker.print_summary()
    
    time_tracker.end_total()
    
    # Финальная сводка отладки
    if debug_logger:
        debug_logger.print_summary()

if __name__ == "__main__":
    main() 