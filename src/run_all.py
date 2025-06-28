#!/usr/bin/env python3
"""
BagBountyAuto - Автоматизированный фреймворк для багбаунти
Запускает полный цикл: разведка -> фильтрация -> анализ -> сканирование уязвимостей
"""

import sys
import subprocess
import os

# Цвета для вывода
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def run_step(command, step_name):
    """Выполняет этап и обрабатывает ошибки"""
    print(f"\n{YELLOW}[+] {step_name}{RESET}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"{GREEN}[+] {step_name} завершен успешно{RESET}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{RED}[-] Ошибка на этапе: {step_name}{RESET}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"{RED}[-] Неожиданная ошибка в {step_name}: {e}{RESET}")
        return False

def main():
    if len(sys.argv) < 2:
        print(f"Использование: python3 run_all.py <домен>")
        sys.exit(1)
    domain = sys.argv[1]

    recon_out = f"recon-{domain}"
    all_urls_file = f"{recon_out}/urls/all_urls.txt"
    filtered_out = f"filtered-{domain}.txt"

    # 1. Recon
    run_step(f"python3 recon.py {domain}", "Разведка домена")

    # 2. Фильтрация
    run_step(f"python3 filter_recon.py {all_urls_file}", "Фильтрация результатов")

    # 3. Анализ
    run_step(f"python3 analyze.py {filtered_out}", "Анализ URL на уязвимости")

    # 4. Активное сканирование
    run_step(f"python3 vuln_scanner.py {filtered_out}", "Активное сканирование (поиск секретов, тестирование параметров)")

    print(f"\n{GREEN}Все этапы успешно завершены!{RESET}")

if __name__ == "__main__":
    main()
