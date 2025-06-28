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

# Добавляем src в путь
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.common import print_status, print_success, print_error, print_warning, time_tracker
from src.utils.reports_manager import setup_reports_for_domain, ReportsManager

def run_step(command, step_name, cwd=None):
    """Выполняет этап и обрабатывает ошибки"""
    time_tracker.start_stage(step_name)
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        time_tracker.end_stage(step_name)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        time_tracker.end_stage(step_name)
        print_error(f"Ошибка на этапе: {step_name}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        time_tracker.end_stage(step_name)
        print_error(f"Неожиданная ошибка в {step_name}: {e}")
        return False

def check_dependencies():
    """Проверяет наличие основных зависимостей"""
    time_tracker.start_stage("Проверка зависимостей")
    print_status("Проверка зависимостей...")
    
    required_tools = ['python3', 'subfinder', 'httpx', 'waybackurls', 'katana']
    missing = []
    
    for tool in required_tools:
        try:
            subprocess.run([tool, '--help'], capture_output=True, timeout=5)
            print_success(f"{tool} - OK")
        except:
            print_error(f"{tool} - НЕ НАЙДЕН")
            missing.append(tool)
    
    if missing:
        print_warning(f"Отсутствуют инструменты: {', '.join(missing)}")
        print_warning("Запустите ./install.sh для установки")
        time_tracker.end_stage("Проверка зависимостей")
        return False
    
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
    
    args = parser.parse_args()
    
    # Начинаем отсчет общего времени
    time_tracker.start_total()
    
    if args.check_deps:
        check_dependencies()
        time_tracker.end_total()
        return
    
    # Проверка зависимостей
    if not check_dependencies():
        time_tracker.end_total()
        return
    
    # Настройка менеджера отчетов
    time_tracker.start_stage("Настройка системы отчетов")
    print_status("Настройка системы отчетов...")
    reports_manager = setup_reports_for_domain(args.domain, args.reports_dir)
    time_tracker.end_stage("Настройка системы отчетов")
    
    # Очистка старых отчетов если запрошено
    if args.cleanup_reports:
        time_tracker.start_stage("Очистка старых отчетов")
        print_status("Очистка старых отчетов...")
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
    
    print_status(f"Начало работы с доменом: {args.domain}")
    
    # 1. Разведка
    if not run_step(f"python3 src/recon/recon.py {args.domain}", "Разведка домена"):
        print_error("Разведка завершилась с ошибкой")
        time_tracker.end_total()
        return
    
    if args.recon_only:
        print_success("Режим 'только разведка' - завершение")
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
        return
    
    # 2. Фильтрация
    if not run_step(f"python3 src/filter/filter_recon.py {all_urls_file}", "Фильтрация результатов"):
        print_error("Фильтрация завершилась с ошибкой")
        time_tracker.end_total()
        return
    
    # 3. Анализ
    if not run_step(f"python3 src/analyze/analyze.py {args.domain}", "Анализ URL на уязвимости"):
        print_warning("Анализ завершился с ошибкой, продолжаем...")
    
    # 4. Активное сканирование (если не пропущено)
    if not args.skip_scan:
        scan_cmd = f"python3 src/scanner/vuln_scanner.py {recon_out} --threads {args.threads}"
        if not run_step(scan_cmd, "Активное сканирование уязвимостей"):
            print_warning("Активное сканирование завершилось с ошибкой")
    
    # Организуем все отчеты
    time_tracker.start_stage("Организация отчетов")
    print_status("Организация отчетов...")
    reports_manager.move_existing_reports(args.domain)
    time_tracker.end_stage("Организация отчетов")
    
    print_success("Все этапы завершены!")
    print_status(f"Отчеты организованы в: {reports_manager.base_dir}/")
    
    # Показываем статистику
    try:
        with open(f"{recon_out}/urls/all_urls.txt", 'r') as f:
            urls_count = sum(1 for _ in f)
        print_status(f"Всего URL: {urls_count}")
    except:
        pass
    
    # Показываем сводку отчетов если запрошено
    if args.show_summary:
        reports_manager.print_summary()
    
    # Показываем статистику времени выполнения
    if args.show_timing:
        time_tracker.print_summary()
    
    # Завершаем общий отсчет времени
    time_tracker.end_total()

if __name__ == "__main__":
    main() 