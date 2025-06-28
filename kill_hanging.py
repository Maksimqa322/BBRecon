#!/usr/bin/env python3
"""
Скрипт для принудительного завершения зависших процессов разведки
"""

import os
import subprocess
import signal
import psutil
import time

def find_recon_processes():
    """Находит процессы разведки"""
    recon_processes = []
    
    # Ищем процессы по ключевым словам
    keywords = ['subfinder', 'httpx', 'waybackurls', 'katana', 'urlfinder', 'recon.py']
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            for keyword in keywords:
                if keyword in cmdline.lower():
                    recon_processes.append(proc)
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return recon_processes

def kill_process_tree(pid):
    """Завершает процесс и все его дочерние процессы"""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        
        # Сначала завершаем дочерние процессы
        for child in children:
            try:
                child.terminate()
            except psutil.NoSuchProcess:
                pass
        
        # Ждем завершения дочерних процессов
        gone, alive = psutil.wait_procs(children, timeout=3)
        
        # Принудительно завершаем оставшиеся дочерние процессы
        for child in alive:
            try:
                child.kill()
            except psutil.NoSuchProcess:
                pass
        
        # Завершаем родительский процесс
        parent.terminate()
        try:
            parent.wait(timeout=3)
        except psutil.TimeoutExpired:
            parent.kill()
        
        return True
    except psutil.NoSuchProcess:
        return False

def main():
    print("🔍 Поиск процессов разведки...")
    
    recon_processes = find_recon_processes()
    
    if not recon_processes:
        print("✅ Процессы разведки не найдены")
        return
    
    print(f"📋 Найдено {len(recon_processes)} процессов разведки:")
    
    for proc in recon_processes:
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else proc.info['name']
            print(f"  PID {proc.info['pid']}: {cmdline[:100]}...")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    print("\n⚠️  Завершаем процессы разведки...")
    
    killed_count = 0
    for proc in recon_processes:
        try:
            if kill_process_tree(proc.info['pid']):
                print(f"✅ Завершен процесс {proc.info['pid']}")
                killed_count += 1
            else:
                print(f"❌ Не удалось завершить процесс {proc.info['pid']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"❌ Ошибка при завершении процесса {proc.info['pid']}: {e}")
    
    print(f"\n📊 Завершено {killed_count} из {len(recon_processes)} процессов")
    
    # Проверяем, остались ли процессы
    remaining = find_recon_processes()
    if remaining:
        print(f"⚠️  Осталось {len(remaining)} процессов, принудительно завершаем...")
        for proc in remaining:
            try:
                proc.kill()
                print(f"💀 Принудительно завершен процесс {proc.info['pid']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

if __name__ == "__main__":
    main() 