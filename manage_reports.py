#!/usr/bin/env python3
"""
Скрипт управления отчетами BagBountyAuto
Позволяет организовывать, очищать и просматривать отчеты
"""

import sys
import argparse
from pathlib import Path

# Добавляем src в путь
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.reports_manager import ReportsManager
from config.settings import REPORTS_STRUCTURE

def main():
    parser = argparse.ArgumentParser(
        description='Управление отчетами BagBountyAuto',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s summary                           # Показать сводку отчетов
  %(prog)s cleanup 30                        # Очистить отчеты старше 30 дней
  %(prog)s organize example.com              # Организовать отчеты для домена
  %(prog)s setup --reports-dir /path/to/reports  # Настроить папку для отчетов
  %(prog)s list example.com                  # Показать отчеты для домена
        """
    )
    
    parser.add_argument('command', choices=['summary', 'cleanup', 'organize', 'setup', 'list'], 
                       help='Команда для выполнения')
    parser.add_argument('target', nargs='?', help='Целевой домен или количество дней')
    parser.add_argument('--reports-dir', help='Директория для отчетов')
    parser.add_argument('--force', action='store_true', help='Принудительное выполнение')
    
    args = parser.parse_args()
    
    # Создаем менеджер отчетов
    manager = ReportsManager(args.reports_dir)
    
    if args.command == 'summary':
        manager.print_summary()
        
    elif args.command == 'cleanup':
        days = int(args.target) if args.target else None
        if not args.force:
            print(f"Будут удалены отчеты старше {days or manager.max_age_days} дней")
            confirm = input("Продолжить? (y/N): ")
            if confirm.lower() != 'y':
                print("Операция отменена")
                return
        manager.cleanup_old_reports(days)
        
    elif args.command == 'organize':
        if not args.target:
            print("Укажите домен для организации")
            return
        domain = args.target
        print(f"Организация отчетов для домена: {domain}")
        manager.move_existing_reports(domain)
        manager.print_summary()
        
    elif args.command == 'setup':
        print(f"Настройка системы отчетов в: {manager.base_dir}")
        manager._create_base_structure()
        print("Структура папок создана:")
        for report_type, folder_name in REPORTS_STRUCTURE.items():
            print(f"  - {folder_name}/ ({report_type})")
        print(f"  - logs/ (логи)")
        
    elif args.command == 'list':
        if not args.target:
            print("Укажите домен для просмотра отчетов")
            return
        domain = args.target
        print(f"Отчеты для домена: {domain}")
        
        # Показываем отчеты по типам
        base_path = Path(manager.base_dir)
        found_reports = False
        
        for report_type, folder_name in REPORTS_STRUCTURE.items():
            domain_path = base_path / folder_name / domain
            if domain_path.exists():
                print(f"\n{report_type.upper()}:")
                found_reports = True
                for report_file in domain_path.rglob('*'):
                    if report_file.is_file():
                        size = report_file.stat().st_size / 1024  # KB
                        print(f"  {report_file.name} ({size:.1f} KB)")
        
        if not found_reports:
            print("Отчеты для данного домена не найдены")

if __name__ == "__main__":
    main() 