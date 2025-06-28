#!/usr/bin/env python3
"""
Модуль отладки и логирования для BagBountyAuto
"""

import os
import sys
import time
import logging
import threading
import signal
import traceback
from datetime import datetime
from pathlib import Path
from functools import wraps

# Цвета для вывода
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
RESET = '\033[0m'

class DebugLogger:
    """Класс для отладки и логирования"""
    
    def __init__(self, debug_level='INFO', log_file=None, enable_console=True):
        self.debug_level = debug_level.upper()
        self.log_file = log_file
        self.enable_console = enable_console
        self.logger = None
        self.start_time = time.time()
        self.active_processes = {}
        self.timeout_warnings = {}
        
        self._setup_logger()
    
    def _setup_logger(self):
        """Настройка логгера"""
        self.logger = logging.getLogger('BagBountyDebug')
        self.logger.setLevel(getattr(logging, self.debug_level))
        
        # Очищаем существующие обработчики
        self.logger.handlers.clear()
        
        # Форматтер
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Консольный обработчик
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, self.debug_level))
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Файловый обработчик
        if self.log_file:
            # Создаем директорию для логов если нужно
            log_dir = os.path.dirname(self.log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setLevel(getattr(logging, self.debug_level))
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message):
        """Отладочное сообщение"""
        if self.logger:
            self.logger.debug(f"[DEBUG] {message}")
        if self.enable_console and self.debug_level == 'DEBUG':
            print(f"{CYAN}[DEBUG]{RESET} {message}")
    
    def info(self, message):
        """Информационное сообщение"""
        if self.logger:
            self.logger.info(f"[INFO] {message}")
        if self.enable_console:
            print(f"{BLUE}[INFO]{RESET} {message}")
    
    def warning(self, message):
        """Предупреждение"""
        if self.logger:
            self.logger.warning(f"[WARN] {message}")
        if self.enable_console:
            print(f"{YELLOW}[WARN]{RESET} {message}")
    
    def error(self, message):
        """Ошибка"""
        if self.logger:
            self.logger.error(f"[ERROR] {message}")
        if self.enable_console:
            print(f"{RED}[ERROR]{RESET} {message}")
    
    def critical(self, message):
        """Критическая ошибка"""
        if self.logger:
            self.logger.critical(f"[CRITICAL] {message}")
        if self.enable_console:
            print(f"{RED}[CRITICAL]{RESET} {message}")
    
    def command_start(self, command, timeout=300):
        """Логирует начало выполнения команды"""
        process_id = f"cmd_{int(time.time() * 1000)}"
        self.active_processes[process_id] = {
            'command': command,
            'start_time': time.time(),
            'timeout': timeout,
            'thread': threading.current_thread().ident
        }
        
        self.info(f"Начало выполнения команды [{process_id}]: {command}")
        self.debug(f"Таймаут: {timeout}с, Поток: {threading.current_thread().ident}")
        
        # Запускаем мониторинг таймаута
        if timeout > 0:
            self._start_timeout_monitor(process_id, timeout)
        
        return process_id
    
    def command_end(self, process_id, success=True, output=None, error=None):
        """Логирует завершение выполнения команды"""
        if process_id in self.active_processes:
            process_info = self.active_processes[process_id]
            duration = time.time() - process_info['start_time']
            
            status = "УСПЕХ" if success else "ОШИБКА"
            self.info(f"Завершение команды [{process_id}] ({status}): {process_info['command']}")
            self.debug(f"Время выполнения: {duration:.2f}с")
            
            if output:
                self.debug(f"Вывод: {output[:500]}{'...' if len(output) > 500 else ''}")
            
            if error:
                self.error(f"Ошибка: {error}")
            
            del self.active_processes[process_id]
            
            # Удаляем из таймаут-мониторинга
            if process_id in self.timeout_warnings:
                del self.timeout_warnings[process_id]
    
    def _start_timeout_monitor(self, process_id, timeout):
        """Запускает мониторинг таймаута для команды"""
        def monitor():
            time.sleep(timeout)
            if process_id in self.active_processes:
                process_info = self.active_processes[process_id]
                elapsed = time.time() - process_info['start_time']
                self.warning(f"Команда [{process_id}] выполняется дольше {timeout}с ({elapsed:.1f}с): {process_info['command']}")
                self.timeout_warnings[process_id] = True
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def check_hanging_processes(self):
        """Проверяет зависшие процессы"""
        current_time = time.time()
        hanging = []
        
        for process_id, process_info in self.active_processes.items():
            elapsed = current_time - process_info['start_time']
            if elapsed > process_info['timeout']:
                hanging.append({
                    'id': process_id,
                    'command': process_info['command'],
                    'elapsed': elapsed,
                    'thread': process_info['thread']
                })
        
        if hanging:
            self.warning(f"Обнаружено {len(hanging)} зависших процессов:")
            for proc in hanging:
                self.warning(f"  [{proc['id']}] {proc['elapsed']:.1f}с: {proc['command']}")
        
        return hanging
    
    def log_exception(self, exception, context=""):
        """Логирует исключение с контекстом"""
        self.error(f"Исключение {context}: {str(exception)}")
        self.debug(f"Traceback: {traceback.format_exc()}")
    
    def log_memory_usage(self):
        """Логирует использование памяти"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            self.debug(f"Использование памяти: {memory_info.rss / 1024 / 1024:.1f} MB")
        except ImportError:
            self.debug("psutil не установлен, пропускаем мониторинг памяти")
    
    def log_system_info(self):
        """Логирует системную информацию"""
        self.info("=== Системная информация ===")
        self.info(f"Python версия: {sys.version}")
        self.info(f"Платформа: {sys.platform}")
        self.info(f"Рабочая директория: {os.getcwd()}")
        self.info(f"Время запуска: {datetime.fromtimestamp(self.start_time)}")
        
        # Информация о системе
        try:
            import platform
            self.info(f"ОС: {platform.system()} {platform.release()}")
            self.info(f"Архитектура: {platform.machine()}")
        except:
            pass
    
    def get_summary(self):
        """Возвращает сводку выполнения"""
        total_time = time.time() - self.start_time
        active_count = len(self.active_processes)
        hanging_count = len(self.timeout_warnings)
        
        summary = {
            'total_time': total_time,
            'active_processes': active_count,
            'hanging_processes': hanging_count,
            'log_file': self.log_file
        }
        
        return summary
    
    def print_summary(self):
        """Выводит сводку выполнения"""
        summary = self.get_summary()
        
        self.info("=== Сводка выполнения ===")
        self.info(f"Общее время: {summary['total_time']:.2f}с")
        self.info(f"Активных процессов: {summary['active_processes']}")
        self.info(f"Зависших процессов: {summary['hanging_processes']}")
        if summary['log_file']:
            self.info(f"Файл лога: {summary['log_file']}")

def debug_command(func):
    """Декоратор для отладки выполнения команд"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        debug_logger = kwargs.get('debug_logger')
        if debug_logger:
            process_id = debug_logger.command_start(f"{func.__name__}({args}, {kwargs})")
            try:
                result = func(*args, **kwargs)
                debug_logger.command_end(process_id, success=True, output=str(result))
                return result
            except Exception as e:
                debug_logger.command_end(process_id, success=False, error=str(e))
                debug_logger.log_exception(e, f"в функции {func.__name__}")
                raise
        else:
            return func(*args, **kwargs)
    return wrapper

def timeout_monitor(timeout_seconds=300):
    """Декоратор для мониторинга таймаутов"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            debug_logger = kwargs.get('debug_logger')
            if debug_logger:
                process_id = debug_logger.command_start(f"{func.__name__}", timeout_seconds)
                try:
                    result = func(*args, **kwargs)
                    debug_logger.command_end(process_id, success=True)
                    return result
                except Exception as e:
                    debug_logger.command_end(process_id, success=False, error=str(e))
                    raise
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Глобальный экземпляр логгера
debug_logger = None

def init_debug_logger(debug_level='INFO', log_file=None, enable_console=True):
    """Инициализирует глобальный логгер отладки"""
    global debug_logger
    debug_logger = DebugLogger(debug_level, log_file, enable_console)
    debug_logger.log_system_info()
    return debug_logger

def get_debug_logger():
    """Возвращает глобальный логгер отладки"""
    return debug_logger 