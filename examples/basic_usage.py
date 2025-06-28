#!/usr/bin/env python3
"""
Пример базового использования BagBountyAuto
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.utils.common import print_status, print_success

def main():
    print_status("Пример использования BagBountyAuto")
    
    # Пример 1: Полный цикл
    print_success("1. Полный цикл:")
    print("   python3 bagbounty.py example.com")
    
    # Пример 2: Только разведка
    print_success("2. Только разведка:")
    print("   python3 bagbounty.py example.com --recon-only")
    
    # Пример 3: Без активного сканирования
    print_success("3. Без активного сканирования:")
    print("   python3 bagbounty.py example.com --skip-scan")
    
    # Пример 4: С ограничением потоков
    print_success("4. С ограничением потоков:")
    print("   python3 bagbounty.py example.com --threads 5")
    
    # Пример 5: Проверка зависимостей
    print_success("5. Проверка зависимостей:")
    print("   python3 bagbounty.py --check-deps")

if __name__ == "__main__":
    main() 