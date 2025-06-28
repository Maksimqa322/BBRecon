#!/usr/bin/env python3
import os
import re
import subprocess
import argparse
import time
from concurrent.futures import ThreadPoolExecutor

# Настройки
TOOLS = {
    'subfinder': 'subfinder',
    'httpx': 'httpx',
    'waybackurls': 'waybackurls',
    'katana': 'katana',
    'grep': 'grep',
    'sed': 'sed',
    'wget': 'wget'
}
BLACKLIST_EXT = "woff,css,png,svg,jpg,woff2,jpeg,gif"
SENSITIVE_EXT = r"\.(xls|xml|xlsx|json|pdf|sql|doc|docx|pptx|txt|zip|tar\.gz|tgz|bak|7z|rar|log|cache|secret|db|backup|yml|gz|config|csv|yaml|md|md5)$"
PORTS = "80,443,8080,8000,8888"
THREADS = 200
KATANA_DEPTH = 5

def run_command(cmd, output_file=None):
    """Выполняет shell-команду с обработкой ошибок"""
    try:
        print(f"[DEBUG] Выполняется команда: {cmd}")
        
        if output_file:
            # Если нужно сохранить в файл
            result = subprocess.run(
                cmd,
                shell=True,
                text=True,
                capture_output=True
            )
            if result.returncode == 0 and result.stdout:
                with open(output_file, 'w') as f:
                    f.write(result.stdout)
                print(f"[+] Результат сохранен в: {output_file}")
                return result.stdout.strip()
            else:
                print(f"[-] Команда завершилась с ошибкой: {result.stderr}")
                return None
        else:
            # Если нужно только выполнить команду
            result = subprocess.run(
                cmd,
                shell=True,
                text=True,
                capture_output=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"[-] Команда завершилась с ошибкой: {result.stderr}")
                return None
                
    except subprocess.CalledProcessError as e:
        print(f"[-] Ошибка выполнения команды: {cmd}\n{e.stderr}")
        return None
    except Exception as e:
        print(f"[-] Неожиданная ошибка: {e}")
        return None

def check_tools():
    """Проверяет наличие необходимых инструментов"""
    missing_tools = []
    for tool_name, tool_cmd in TOOLS.items():
        try:
            subprocess.run([tool_cmd, '--help'], capture_output=True, timeout=5)
            print(f"[+] {tool_name} найден")
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            print(f"[-] {tool_name} не найден")
            missing_tools.append(tool_name)
    
    if missing_tools:
        print(f"\n[!] Отсутствуют инструменты: {', '.join(missing_tools)}")
        print("[!] Установите их перед запуском скрипта")
        return False
    return True

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
        'logs': f"recon-{domain}/logs"
    }
    
    for name, path in dirs.items():
        os.makedirs(path, exist_ok=True)
        print(f"[+] Создана директория: {path}")
    
    return dirs

def count_lines(file_path):
    """Подсчитывает количество строк в файле"""
    try:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'r') as f:
                return sum(1 for _ in f)
        return 0
    except Exception:
        return 0

def main():
    parser = argparse.ArgumentParser(description='Bug Bounty Recon Automation')
    parser.add_argument('domain', help='Target domain (e.g. example.com)')
    args = parser.parse_args()
    
    # Проверка инструментов
    if not check_tools():
        return
    
    # Настройка рабочего пространства
    dirs = setup_workspace(args.domain)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    
    print(f"\n[=== Начало разведки для {args.domain} ===]\n")
    
    # Этап 1: Обнаружение поддоменов
    print("[Этап 1/7] Поиск поддоменов...")
    subdomains_file = f"{dirs['subdomains']}/subdomains.txt"
    result = run_command(f"{TOOLS['subfinder']} -d {args.domain} -all -recursive -silent", subdomains_file)
    
    if not result or count_lines(subdomains_file) == 0:
        print("[-] Не удалось найти поддомены. Проверьте домен и доступность subfinder.")
        return
    
    # Этап 2: Поиск живых поддоменов
    print("[Этап 2/7] Проверка живых поддоменов...")
    alive_file = f"{dirs['subdomains']}/alive.txt"
    # Исправленная команда httpx
    run_command(f"cat {subdomains_file} | {TOOLS['httpx']} -p {PORTS} -t {THREADS} -silent -o {alive_file}")
    
    if count_lines(alive_file) == 0:
        print("[-] Не найдено живых поддоменов. Проверьте доступность хостов.")
        return
    
    # Этап 3: Сбор URL с помощью waybackurls
    print("[Этап 3/7] Сбор URL (waybackurls)...")
    waybackurls_file = f"{dirs['waybackurls']}/waybackurls_urls.txt"
    # waybackurls работает с доменами
    run_command(f"{TOOLS['waybackurls']} {args.domain}", waybackurls_file)
    
    # Этап 4: Сбор URL с помощью Katana
    print("[Этап 4/7] Сбор URL (katana)...")
    katana_file = f"{dirs['katana']}/katana_urls.txt"
    # Исправленная команда katana
    run_command(f"{TOOLS['katana']} -list {alive_file} -d {KATANA_DEPTH} -jc -fx -ef {BLACKLIST_EXT} -o {katana_file}")
    
    # Этап 5: Объединение и обработка URL
    print("[Этап 5/7] Обработка URL...")
    all_urls_file = f"{dirs['urls']}/all_urls.txt"
    
    # Объединение результатов только если файлы существуют и не пустые
    waybackurls_exists = os.path.exists(waybackurls_file) and os.path.getsize(waybackurls_file) > 0
    katana_exists = os.path.exists(katana_file) and os.path.getsize(katana_file) > 0
    
    if waybackurls_exists and katana_exists:
        run_command(f"cat {waybackurls_file} {katana_file} | sort -u > {all_urls_file}")
    elif waybackurls_exists:
        run_command(f"cp {waybackurls_file} {all_urls_file}")
    elif katana_exists:
        run_command(f"cp {katana_file} {all_urls_file}")
    else:
        print("[-] Не удалось собрать URL. Создаем пустой файл.")
        open(all_urls_file, 'w').close()
    
    # Поиск чувствительных файлов
    if os.path.exists(all_urls_file) and os.path.getsize(all_urls_file) > 0:
        sensitive_files = f"{dirs['urls']}/sensitive_files.txt"
        run_command(f"grep -aE '{SENSITIVE_EXT}' {all_urls_file} > {sensitive_files}")
        
        # Поиск URL с параметрами
        param_file = f"{dirs['urls']}/param_urls.txt"
        run_command(f"grep -aF '=' {all_urls_file} | {TOOLS['sed']} 's/=.*/=/' | sort -u > {param_file}")
        
        # Специфичные категории URL
        for ext, name in [("js$", "js_files.txt"), ("php$", "php_files.txt"), ("/api/", "api_endpoints.txt")]:
            run_command(f"grep -a '{ext}' {all_urls_file} > {dirs['urls']}/{name}")
    
    # Этап 6: Скачивание файлов
    print("[Этап 6/7] Скачивание файлов...")
    
    def download_files(file_type, urls_file, output_dir):
        if os.path.exists(urls_file) and os.path.getsize(urls_file) > 0:
            print(f"[+] Скачивание {file_type} файлов...")
            run_command(f"{TOOLS['wget']} -q -i {urls_file} -P {output_dir} --timeout=10 --tries=1 --no-check-certificate")
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(download_files, "sensitive", f"{dirs['urls']}/sensitive_files.txt", dirs['sensitive'])
        executor.submit(download_files, "js", f"{dirs['urls']}/js_files.txt", dirs['js'])
        executor.submit(download_files, "php", f"{dirs['urls']}/php_files.txt", dirs['php'])
    
    # Этап 7: Генерация отчетов
    print("[Этап 7/7] Генерация отчетов...")
    report_file = f"{dirs['base']}/report_{timestamp}.md"
    
    with open(report_file, 'w', encoding='utf-8') as report:
        report.write(f"# Отчет разведки: {args.domain}\n")
        report.write(f"**Дата:** {timestamp}\n\n")
        
        # Статистика
        stats = {
            "Поддомены": f"{dirs['subdomains']}/subdomains.txt",
            "Живые поддомены": f"{dirs['subdomains']}/alive.txt",
            "Всего URL": f"{dirs['urls']}/all_urls.txt",
            "Чувствительные файлы": f"{dirs['urls']}/sensitive_files.txt",
            "URL с параметрами": f"{dirs['urls']}/param_urls.txt"
        }
        
        report.write("## Статистика\n")
        for name, file in stats.items():
            count = count_lines(file)
            report.write(f"- **{name}:** {count}\n")
        
        # Директории
        report.write("\n## Структура проекта\n")
        for dir_name, dir_path in dirs.items():
            report.write(f"- `{dir_path}`\n")
    
    print(f"\n[=== Завершено! Отчет: {report_file} ===]")
    
    # Финальная статистика
    subdomains_count = count_lines(f"{dirs['subdomains']}/subdomains.txt")
    alive_count = count_lines(f"{dirs['subdomains']}/alive.txt")
    urls_count = count_lines(f"{dirs['urls']}/all_urls.txt")
    
    print(f"Всего собрано данных:")
    print(f"  Поддомены: {subdomains_count}")
    print(f"  Живые хосты: {alive_count}")
    print(f"  URL: {urls_count}")

if __name__ == "__main__":
    main()
