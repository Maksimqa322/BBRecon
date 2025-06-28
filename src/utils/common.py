#!/usr/bin/env python3
"""
Общие утилиты для BagBountyAuto
"""

import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Добавляем путь к корневой директории проекта
sys.path.append(str(Path(__file__).parent.parent.parent))

# Цвета для вывода
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_status(message):
    """Выводит статусное сообщение"""
    print(f"[*] {message}")

def print_success(message):
    """Выводит сообщение об успехе"""
    print(f"[+] {message}")

def print_error(message):
    """Выводит сообщение об ошибке"""
    print(f"[-] {message}")

def print_warning(message):
    """Выводит предупреждение"""
    print(f"[!] {message}")

def run_command(command, output_file=None, cwd=None):
    """Выполняет команду и сохраняет результат в файл"""
    try:
        if output_file:
            with open(output_file, 'w') as f:
                result = subprocess.run(command, shell=True, stdout=f, stderr=subprocess.PIPE, text=True, cwd=cwd)
        else:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
        
        if result.returncode == 0:
            return True
        else:
            print_error(f"Команда завершилась с ошибкой: {command}")
            if result.stderr:
                print_error(f"STDERR: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"Ошибка выполнения команды: {e}")
        return False

def count_lines(filename):
    """Подсчитывает количество строк в файле"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        return 0
    except Exception:
        return 0

def setup_workspace(domain):
    """Создает структуру директорий для работы"""
    base_dir = f"recon-{domain}"
    
    dirs = {
        'base': base_dir,
        'subdomains': f"{base_dir}/subdomains",
        'urls': f"{base_dir}/urls",
        'waybackurls': f"{base_dir}/waybackurls",
        'katana': f"{base_dir}/katana",
        'sensitive': f"{base_dir}/sensitive",
        'js': f"{base_dir}/js",
        'php': f"{base_dir}/php"
    }
    
    for dir_path in dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    
    return dirs

def get_timestamp():
    """Возвращает текущую временную метку"""
    return datetime.now().strftime("%Y%m%d-%H%M%S")

class TimeTracker:
    """Класс для отслеживания времени выполнения этапов"""
    
    def __init__(self):
        self.start_time = None
        self.stages = {}
        self.current_stage = None
    
    def start_total(self):
        """Начинает общий отсчет времени"""
        self.start_time = time.time()
        print_status("Начало выполнения...")
    
    def start_stage(self, stage_name):
        """Начинает отсчет времени для этапа"""
        self.current_stage = stage_name
        self.stages[stage_name] = {'start': time.time()}
        print_status(f"Этап: {stage_name}")
    
    def end_stage(self, stage_name=None):
        """Завершает отсчет времени для этапа"""
        if stage_name is None:
            stage_name = self.current_stage
        
        if stage_name in self.stages:
            self.stages[stage_name]['end'] = time.time()
            duration = self.stages[stage_name]['end'] - self.stages[stage_name]['start']
            self.stages[stage_name]['duration'] = duration
            print_success(f"Этап '{stage_name}' завершен за {self.format_duration(duration)}")
    
    def end_total(self):
        """Завершает общий отсчет времени"""
        if self.start_time:
            total_duration = time.time() - self.start_time
            print_success(f"Общее время выполнения: {self.format_duration(total_duration)}")
            return total_duration
        return 0
    
    def format_duration(self, seconds):
        """Форматирует время в читаемый вид"""
        if seconds < 60:
            return f"{seconds:.1f}с"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}м {secs:.1f}с"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = seconds % 60
            return f"{hours}ч {minutes}м {secs:.1f}с"
    
    def get_summary(self):
        """Возвращает сводку по времени"""
        summary = []
        total_stages = 0
        
        for stage_name, stage_data in self.stages.items():
            if 'duration' in stage_data:
                duration = stage_data['duration']
                total_stages += duration
                summary.append(f"  {stage_name}: {self.format_duration(duration)}")
        
        if self.start_time:
            total_duration = time.time() - self.start_time
            summary.append(f"  Общее время: {self.format_duration(total_duration)}")
        
        return summary
    
    def print_summary(self):
        """Выводит сводку по времени"""
        print_status("Статистика времени выполнения:")
        summary = self.get_summary()
        for line in summary:
            print(f"    {line}")

# Глобальный экземпляр трекера времени
time_tracker = TimeTracker() 