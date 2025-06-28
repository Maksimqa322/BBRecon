#!/usr/bin/env python3
"""
Общие утилиты для BagBountyAuto
"""

import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

# Цвета для вывода
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_status(message):
    """Вывод статуса"""
    print(f"{BLUE}[INFO]{RESET} {message}")

def print_success(message):
    """Вывод успеха"""
    print(f"{GREEN}[SUCCESS]{RESET} {message}")

def print_warning(message):
    """Вывод предупреждения"""
    print(f"{YELLOW}[WARNING]{RESET} {message}")

def print_error(message):
    """Вывод ошибки"""
    print(f"{RED}[ERROR]{RESET} {message}")

def run_command(cmd, output_file=None, timeout=300):
    """Выполняет shell-команду с обработкой ошибок"""
    try:
        print(f"[DEBUG] Выполняется команда: {cmd}")
        
        if output_file:
            result = subprocess.run(
                cmd,
                shell=True,
                text=True,
                capture_output=True,
                timeout=timeout
            )
            if result.returncode == 0 and result.stdout:
                with open(output_file, 'w') as f:
                    f.write(result.stdout)
                print(f"[+] Результат сохранен в: {output_file}")
                return result.stdout.strip()
            else:
                print(f"[-] Команда завершилась с ошибкой: {result.stderr}")
                if result.stderr:
                    print(f"[stderr]: {result.stderr}")
                return None
        else:
            result = subprocess.run(
                cmd,
                shell=True,
                text=True,
                capture_output=True,
                timeout=timeout
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"[-] Команда завершилась с ошибкой: {result.stderr}")
                if result.stderr:
                    print(f"[stderr]: {result.stderr}")
                return None
                
    except subprocess.TimeoutExpired:
        print(f"[-] Таймаут команды: {cmd}")
        return None
    except Exception as e:
        print(f"[-] Неожиданная ошибка: {e}")
        return None

def count_lines(file_path):
    """Подсчитывает количество строк в файле"""
    try:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'r') as f:
                return sum(1 for _ in f)
        return 0
    except Exception:
        return 0

def setup_workspace(domain):
    """Создает структуру директорий"""
    dirs = {
        'base': f"recon-{domain}",
        'subdomains': f"recon-{domain}/subdomains",
        'urls': f"recon-{domain}/urls",
        'files': f"recon-{domain}/files",
        'sensitive': f"recon-{domain}/files/sensitive",
        'js': f"recon-{domain}/files/js",
        'php': f"recon-{domain}/files/php",
        'katana': f"recon-{domain}/katana",
        'waybackurls': f"recon-{domain}/waybackurls",
        'logs': f"recon-{domain}/logs",
        'analysis': f"recon-{domain}/analysis"
    }
    
    for name, path in dirs.items():
        os.makedirs(path, exist_ok=True)
        print(f"[+] Создана директория: {path}")
    
    return dirs

def get_timestamp():
    """Возвращает текущий timestamp"""
    return time.strftime("%Y%m%d-%H%M%S") 