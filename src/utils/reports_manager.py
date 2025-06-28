#!/usr/bin/env python3
"""
Менеджер отчетов для BagBountyAuto
Организует отчеты в отдельные папки и управляет их жизненным циклом
"""

import os
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from config.settings import REPORTS_CONFIG, REPORTS_STRUCTURE

class ReportsManager:
    """Менеджер для организации и управления отчетами"""
    
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or REPORTS_CONFIG['base_dir']
        self.max_age_days = REPORTS_CONFIG['max_age_days']
        self.cleanup_enabled = REPORTS_CONFIG['cleanup_enabled']
        self.organize_by_date = REPORTS_CONFIG['organize_by_date']
        self.organize_by_domain = REPORTS_CONFIG['organize_by_domain']
        
        # Создаем базовую структуру
        self._create_base_structure()
    
    def _create_base_structure(self):
        """Создает базовую структуру папок для отчетов"""
        base_path = Path(self.base_dir)
        base_path.mkdir(exist_ok=True)
        
        # Создаем подпапки для разных типов отчетов
        for report_type, folder_name in REPORTS_STRUCTURE.items():
            (base_path / folder_name).mkdir(exist_ok=True)
        
        # Создаем папку для логов
        (base_path / 'logs').mkdir(exist_ok=True)
        
        print(f"[+] Создана структура отчетов в: {self.base_dir}")
    
    def get_report_path(self, report_type: str, domain: str, filename: str) -> str:
        """Генерирует путь для отчета с учетом организации"""
        base_path = Path(self.base_dir)
        
        # Определяем подпапку для типа отчета
        type_folder = REPORTS_STRUCTURE.get(report_type, report_type)
        report_path = base_path / type_folder
        
        if self.organize_by_domain:
            report_path = report_path / domain
        
        if self.organize_by_date:
            date_folder = datetime.now().strftime("%Y-%m-%d")
            report_path = report_path / date_folder
        
        # Создаем все необходимые папки
        report_path.mkdir(parents=True, exist_ok=True)
        
        return str(report_path / filename)
    
    def move_existing_reports(self, domain: str):
        """Перемещает существующие отчеты в организованную структуру"""
        domain_pattern = f"recon-{domain}"
        vuln_pattern = f"vuln_scan"
        filtered_pattern = f"filtered-{domain}"
        
        patterns = [
            (domain_pattern, 'recon'),
            (vuln_pattern, 'vuln_scan'),
            (filtered_pattern, 'filtered')
        ]
        
        for pattern, report_type in patterns:
            if os.path.exists(pattern):
                # Находим все файлы в папке
                for root, dirs, files in os.walk(pattern):
                    for file in files:
                        if file.endswith(('.txt', '.md', '.json', '.csv')):
                            old_path = os.path.join(root, file)
                            new_path = self.get_report_path(report_type, domain, file)
                            
                            try:
                                shutil.move(old_path, new_path)
                                print(f"[+] Перемещен: {old_path} -> {new_path}")
                            except Exception as e:
                                print(f"[-] Ошибка перемещения {old_path}: {e}")
                
                # Удаляем пустую папку
                try:
                    if os.path.exists(pattern) and not os.listdir(pattern):
                        shutil.rmtree(pattern)
                        print(f"[+] Удалена пустая папка: {pattern}")
                except Exception as e:
                    print(f"[-] Ошибка удаления папки {pattern}: {e}")
    
    def cleanup_old_reports(self, days: Optional[int] = None):
        """Удаляет старые отчеты"""
        if not self.cleanup_enabled:
            return
        
        max_age = days or self.max_age_days
        cutoff_date = datetime.now() - timedelta(days=max_age)
        
        base_path = Path(self.base_dir)
        deleted_count = 0
        
        for root, dirs, files in os.walk(base_path):
            for file in files:
                file_path = Path(root) / file
                try:
                    # Проверяем время модификации файла
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < cutoff_date:
                        file_path.unlink()
                        deleted_count += 1
                        print(f"[+] Удален старый файл: {file_path}")
                except Exception as e:
                    print(f"[-] Ошибка удаления {file_path}: {e}")
        
        if deleted_count > 0:
            print(f"[+] Удалено {deleted_count} старых файлов")
        else:
            print(f"[+] Старые файлы не найдены (старше {max_age} дней)")
    
    def get_reports_summary(self) -> Dict:
        """Возвращает сводку по отчетам"""
        base_path = Path(self.base_dir)
        summary = {
            'total_files': 0,
            'by_type': {},
            'by_domain': {},
            'total_size_mb': 0
        }
        
        for root, dirs, files in os.walk(base_path):
            for file in files:
                file_path = Path(root) / file
                try:
                    size = file_path.stat().st_size
                    summary['total_files'] += 1
                    summary['total_size_mb'] += size / (1024 * 1024)
                    
                    # Определяем тип отчета по папке
                    relative_path = file_path.relative_to(base_path)
                    parts = relative_path.parts
                    
                    if len(parts) >= 1:
                        report_type = parts[0]
                        summary['by_type'][report_type] = summary['by_type'].get(report_type, 0) + 1
                    
                    if len(parts) >= 2:
                        domain = parts[1]
                        summary['by_domain'][domain] = summary['by_domain'].get(domain, 0) + 1
                        
                except Exception as e:
                    print(f"[-] Ошибка анализа {file_path}: {e}")
        
        summary['total_size_mb'] = round(summary['total_size_mb'], 2)
        return summary
    
    def print_summary(self):
        """Выводит сводку по отчетам"""
        summary = self.get_reports_summary()
        
        print(f"\n=== Сводка отчетов ({self.base_dir}) ===")
        print(f"Всего файлов: {summary['total_files']}")
        print(f"Общий размер: {summary['total_size_mb']} MB")
        
        if summary['by_type']:
            print("\nПо типам:")
            for report_type, count in summary['by_type'].items():
                print(f"  {report_type}: {count} файлов")
        
        if summary['by_domain']:
            print("\nПо доменам:")
            for domain, count in summary['by_domain'].items():
                print(f"  {domain}: {count} файлов")
        
        print("=" * 50)

def setup_reports_for_domain(domain: str, base_dir: Optional[str] = None):
    """Настройка отчетов для конкретного домена"""
    manager = ReportsManager(base_dir)
    
    # Перемещаем существующие отчеты
    manager.move_existing_reports(domain)
    
    # Очищаем старые отчеты
    manager.cleanup_old_reports()
    
    return manager

def get_report_path(report_type: str, domain: str, filename: str, base_dir: Optional[str] = None) -> str:
    """Удобная функция для получения пути к отчету"""
    manager = ReportsManager(base_dir)
    return manager.get_report_path(report_type, domain, filename)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python reports_manager.py <команда> [параметры]")
        print("Команды:")
        print("  summary - показать сводку отчетов")
        print("  cleanup [дни] - очистить старые отчеты")
        print("  organize <домен> - организовать отчеты для домена")
        sys.exit(1)
    
    command = sys.argv[1]
    manager = ReportsManager()
    
    if command == "summary":
        manager.print_summary()
    elif command == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else None
        manager.cleanup_old_reports(days)
    elif command == "organize":
        if len(sys.argv) < 3:
            print("Укажите домен для организации")
            sys.exit(1)
        domain = sys.argv[2]
        manager.move_existing_reports(domain)
        manager.print_summary()
    else:
        print(f"Неизвестная команда: {command}")
        sys.exit(1) 