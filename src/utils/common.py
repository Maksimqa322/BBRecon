#!/usr/bin/env python3
"""
Общие утилиты для BagBountyAuto
"""

import os
import sys
import subprocess
import time
import threading
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

def run_command(command, output_file=None, cwd=None, debug_logger=None, timeout=300):
    """Выполняет команду и сохраняет результат в файл"""
    if debug_logger:
        process_id = debug_logger.command_start(command, timeout)
    
    try:
        if output_file:
            with open(output_file, 'w') as f:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    stdout=f, 
                    stderr=subprocess.PIPE, 
                    text=True, 
                    cwd=cwd,
                    timeout=timeout
                )
        else:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=cwd,
                timeout=timeout
            )
        
        if result.returncode == 0:
            if debug_logger:
                output = result.stdout if result.stdout else "Команда выполнена успешно"
                debug_logger.command_end(process_id, success=True, output=output)
            return True
        else:
            error_msg = f"Команда завершилась с ошибкой: {command}"
            print_error(error_msg)
            
            if debug_logger:
                debug_logger.command_end(process_id, success=False, error=result.stderr)
                if result.stderr:
                    debug_logger.error(f"STDERR: {result.stderr}")
            
            if result.stderr:
                print_error(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired as e:
        error_msg = f"Таймаут выполнения команды: {command}"
        print_error(error_msg)
        
        if debug_logger:
            debug_logger.command_end(process_id, success=False, error=f"Таймаут: {timeout}с")
            debug_logger.warning(f"Команда зависла: {command}")
        
        return False
        
    except Exception as e:
        error_msg = f"Ошибка выполнения команды: {e}"
        print_error(error_msg)
        
        if debug_logger:
            debug_logger.command_end(process_id, success=False, error=str(e))
            debug_logger.log_exception(e, f"при выполнении команды: {command}")
        
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

def check_file_exists(filepath, debug_logger=None):
    """Проверяет существование файла с логированием"""
    exists = os.path.exists(filepath)
    if debug_logger:
        if exists:
            debug_logger.debug(f"Файл найден: {filepath}")
        else:
            debug_logger.warning(f"Файл не найден: {filepath}")
    return exists

def get_file_size(filepath, debug_logger=None):
    """Получает размер файла с логированием"""
    try:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            if debug_logger:
                debug_logger.debug(f"Размер файла {filepath}: {size} байт")
            return size
        else:
            if debug_logger:
                debug_logger.warning(f"Файл не существует: {filepath}")
            return 0
    except Exception as e:
        if debug_logger:
            debug_logger.error(f"Ошибка получения размера файла {filepath}: {e}")
        return 0

def safe_file_operation(operation, filepath, debug_logger=None):
    """Безопасно выполняет операцию с файлом с логированием"""
    try:
        result = operation(filepath)
        if debug_logger:
            debug_logger.debug(f"Операция успешна: {operation.__name__} для {filepath}")
        return result
    except Exception as e:
        if debug_logger:
            debug_logger.error(f"Ошибка операции {operation.__name__} для {filepath}: {e}")
        return None

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

def run_command_with_activity_monitor(command, output_file=None, cwd=None, debug_logger=None, timeout=300, activity_timeout=60):
    """
    Выполняет команду с мониторингом активности.
    Если команда не генерирует результаты в течение activity_timeout секунд, она прерывается.
    """
    if debug_logger:
        process_id = debug_logger.command_start(command, timeout)
    
    # Переменные для отслеживания активности
    last_activity = time.time()
    initial_file_size = 0
    if output_file and os.path.exists(output_file):
        initial_file_size = os.path.getsize(output_file)
    
    # Используем список для хранения состояния между потоками
    activity_state = {
        'last_activity': last_activity,
        'initial_file_size': initial_file_size,
        'should_stop': False
    }
    
    def check_activity():
        """Проверяет активность процесса"""
        while not activity_state['should_stop']:
            time.sleep(10)  # Проверяем каждые 10 секунд
            
            # Проверяем размер выходного файла
            if output_file and os.path.exists(output_file):
                current_size = os.path.getsize(output_file)
                if current_size > activity_state['initial_file_size']:
                    activity_state['last_activity'] = time.time()
                    activity_state['initial_file_size'] = current_size
                    if debug_logger:
                        debug_logger.debug(f"Активность обнаружена: файл {output_file} увеличился до {current_size} байт")
            
            # Проверяем, не прошло ли слишком много времени без активности
            if time.time() - activity_state['last_activity'] > activity_timeout:
                if debug_logger:
                    debug_logger.warning(f"Команда неактивна {activity_timeout}с, прерываем: {command}")
                activity_state['should_stop'] = True
                return False
    
    # Запускаем мониторинг активности в отдельном потоке
    activity_thread = threading.Thread(target=check_activity, daemon=True)
    activity_thread.start()
    
    try:
        if output_file:
            with open(output_file, 'w') as f:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    stdout=f, 
                    stderr=subprocess.PIPE, 
                    text=True, 
                    cwd=cwd,
                    timeout=timeout
                )
        else:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=cwd,
                timeout=timeout
            )
        
        # Останавливаем мониторинг активности
        activity_state['should_stop'] = True
        
        # Проверяем результат
        if result.returncode == 0:
            # Проверяем, есть ли результаты
            has_results = False
            if output_file and os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                if file_size > 0:
                    has_results = True
            
            if has_results:
                if debug_logger:
                    output = f"Команда выполнена успешно, результаты сохранены в {output_file}"
                    debug_logger.command_end(process_id, success=True, output=output)
                print_success(f"Команда выполнена успешно: {command}")
                return True
            else:
                if debug_logger:
                    debug_logger.warning(f"Команда завершилась без результатов: {command}")
                print_warning(f"Команда завершилась без результатов: {command}")
                return False
        else:
            error_msg = f"Команда завершилась с ошибкой: {command}"
            print_error(error_msg)
            
            if debug_logger:
                debug_logger.command_end(process_id, success=False, error=result.stderr)
                if result.stderr:
                    debug_logger.error(f"STDERR: {result.stderr}")
            
            if result.stderr:
                print_error(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired as e:
        # Останавливаем мониторинг активности
        activity_state['should_stop'] = True
        
        error_msg = f"Таймаут выполнения команды: {command}"
        print_error(error_msg)
        
        if debug_logger:
            debug_logger.command_end(process_id, success=False, error=f"Таймаут: {timeout}с")
            debug_logger.warning(f"Команда зависла: {command}")
        
        return False
        
    except Exception as e:
        # Останавливаем мониторинг активности
        activity_state['should_stop'] = True
        
        error_msg = f"Ошибка выполнения команды: {e}"
        print_error(error_msg)
        
        if debug_logger:
            debug_logger.command_end(process_id, success=False, error=str(e))
            debug_logger.log_exception(e, f"при выполнении команды: {command}")
        
        return False 