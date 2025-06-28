#!/usr/bin/env python3
import os
import re
import json
import argparse
from urllib.parse import urlparse, parse_qs
from collections import defaultdict

def analyze_urls(urls_file, output_dir):
    """Анализирует URL на предмет потенциальных уязвимостей"""
    if not os.path.exists(urls_file):
        print(f"[-] Файл {urls_file} не найден")
        return
    
    print(f"[+] Анализ URL из {urls_file}")
    
    # Паттерны для поиска потенциальных уязвимостей
    patterns = {
        'sqli': [
            r'id=\d+',
            r'user_id=\d+',
            r'product_id=\d+',
            r'page=\d+',
            r'offset=\d+',
            r'limit=\d+'
        ],
        'xss': [
            r'search=',
            r'q=',
            r'query=',
            r'keyword=',
            r'term=',
            r'input='
        ],
        'lfi': [
            r'file=',
            r'page=',
            r'include=',
            r'path=',
            r'dir=',
            r'document='
        ],
        'rce': [
            r'cmd=',
            r'command=',
            r'exec=',
            r'system=',
            r'shell=',
            r'run='
        ],
        'ssrf': [
            r'url=',
            r'link=',
            r'redirect=',
            r'next=',
            r'target=',
            r'callback='
        ],
        'open_redirect': [
            r'redirect=',
            r'return=',
            r'next=',
            r'url=',
            r'link=',
            r'goto='
        ]
    }
    
    results = defaultdict(list)
    
    with open(urls_file, 'r') as f:
        for line in f:
            url = line.strip()
            if not url:
                continue
            
            # Парсинг URL
            try:
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                
                # Проверка параметров на потенциальные уязвимости
                for vuln_type, vuln_patterns in patterns.items():
                    for pattern in vuln_patterns:
                        match = re.search(pattern, url, re.IGNORECASE)
                        if match:
                            results[vuln_type].append({
                                'url': url,
                                'parameter': match.group(),
                                'domain': parsed.netloc,
                                'path': parsed.path
                            })
                            break
                
                # Поиск API эндпоинтов
                if '/api/' in url or '/rest/' in url or '/graphql' in url:
                    results['api_endpoints'].append({
                        'url': url,
                        'method': 'GET',  # По умолчанию
                        'domain': parsed.netloc,
                        'path': parsed.path
                    })
                
                # Поиск файлов с потенциально чувствительной информацией
                sensitive_extensions = [
                    '.bak', '.backup', '.old', '.tmp', '.temp',
                    '.log', '.sql', '.db', '.config', '.conf',
                    '.env', '.ini', '.xml', '.json', '.yaml', '.yml'
                ]
                
                for ext in sensitive_extensions:
                    if ext in url.lower():
                        results['sensitive_files'].append({
                            'url': url,
                            'extension': ext,
                            'domain': parsed.netloc,
                            'path': parsed.path
                        })
                        break
                        
            except Exception as e:
                print(f"[-] Ошибка парсинга URL {url}: {e}")
    
    # Сохранение результатов
    for vuln_type, vuln_urls in results.items():
        if vuln_urls:
            output_file = os.path.join(output_dir, f"{vuln_type}_urls.txt")
            with open(output_file, 'w') as f:
                for item in vuln_urls:
                    f.write(f"{item['url']}\n")
            print(f"[+] Найдено {len(vuln_urls)} потенциальных {vuln_type} URL")
    
    return results

def analyze_subdomains(subdomains_file, output_dir):
    """Анализирует поддомены на предмет интересных паттернов"""
    if not os.path.exists(subdomains_file):
        print(f"[-] Файл {subdomains_file} не найден")
        return
    
    print(f"[+] Анализ поддоменов из {subdomains_file}")
    
    interesting_patterns = {
        'admin': r'admin',
        'api': r'api',
        'dev': r'dev|development|staging|test',
        'internal': r'internal|intranet|private',
        'cloud': r'cloud|aws|azure|gcp',
        'mobile': r'mobile|app|ios|android',
        'cdn': r'cdn|static|assets|media',
        'mail': r'mail|smtp|pop|imap',
        'database': r'db|database|mysql|postgres|mongo',
        'monitoring': r'monitor|grafana|prometheus|zabbix',
        'jenkins': r'jenkins|ci|cd|build',
        'wordpress': r'wp|wordpress|blog',
        'cms': r'cms|drupal|joomla|magento'
    }
    
    results = defaultdict(list)
    
    with open(subdomains_file, 'r') as f:
        for line in f:
            subdomain = line.strip()
            if not subdomain:
                continue
            
            for pattern_name, pattern in interesting_patterns.items():
                if re.search(pattern, subdomain, re.IGNORECASE):
                    results[pattern_name].append(subdomain)
                    break
    
    # Сохранение результатов
    for pattern_name, subdomains in results.items():
        if subdomains:
            output_file = os.path.join(output_dir, f"{pattern_name}_subdomains.txt")
            with open(output_file, 'w') as f:
                for subdomain in subdomains:
                    f.write(f"{subdomain}\n")
            print(f"[+] Найдено {len(subdomains)} поддоменов с паттерном {pattern_name}")
    
    return results

def generate_vulnerability_report(domain, results_dir, output_file):
    """Генерирует отчет о потенциальных уязвимостях"""
    print(f"[+] Генерация отчета о уязвимостях: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Отчет о потенциальных уязвимостях: {domain}\n\n")
        
        # Анализ URL
        f.write("## Анализ URL\n\n")
        url_patterns = ['sqli', 'xss', 'lfi', 'rce', 'ssrf', 'open_redirect', 'api_endpoints', 'sensitive_files']
        
        for pattern in url_patterns:
            pattern_file = os.path.join(results_dir, f"{pattern}_urls.txt")
            if os.path.exists(pattern_file):
                count = sum(1 for _ in open(pattern_file))
                f.write(f"### {pattern.upper()}\n")
                f.write(f"Найдено URL: {count}\n\n")
                
                # Показываем первые 10 примеров
                with open(pattern_file, 'r') as url_file:
                    for i, url in enumerate(url_file):
                        if i < 10:
                            f.write(f"- `{url.strip()}`\n")
                        else:
                            break
                f.write("\n")
        
        # Анализ поддоменов
        f.write("## Анализ поддоменов\n\n")
        subdomain_patterns = ['admin', 'api', 'dev', 'internal', 'cloud', 'mobile', 'cdn', 'mail', 'database', 'monitoring', 'jenkins', 'wordpress', 'cms']
        
        for pattern in subdomain_patterns:
            pattern_file = os.path.join(results_dir, f"{pattern}_subdomains.txt")
            if os.path.exists(pattern_file):
                count = sum(1 for _ in open(pattern_file))
                f.write(f"### {pattern.upper()}\n")
                f.write(f"Найдено поддоменов: {count}\n\n")
                
                # Показываем первые 10 примеров
                with open(pattern_file, 'r') as subdomain_file:
                    for i, subdomain in enumerate(subdomain_file):
                        if i < 10:
                            f.write(f"- `{subdomain.strip()}`\n")
                        else:
                            break
                f.write("\n")

def main():
    parser = argparse.ArgumentParser(description='Анализ результатов разведки')
    parser.add_argument('domain', help='Target domain (e.g. example.com)')
    args = parser.parse_args()
    
    # Пути к файлам
    recon_dir = f"recon-{args.domain}"
    urls_file = f"{recon_dir}/urls/all_urls.txt"
    subdomains_file = f"{recon_dir}/subdomains/subdomains.txt"
    analysis_dir = f"{recon_dir}/analysis"
    
    # Создание директории для анализа
    os.makedirs(analysis_dir, exist_ok=True)
    
    print(f"[=== Анализ результатов разведки для {args.domain} ===]\n")
    
    # Анализ URL
    if os.path.exists(urls_file):
        analyze_urls(urls_file, analysis_dir)
    else:
        print(f"[-] Файл с URL не найден: {urls_file}")
    
    # Анализ поддоменов
    if os.path.exists(subdomains_file):
        analyze_subdomains(subdomains_file, analysis_dir)
    else:
        print(f"[-] Файл с поддоменами не найден: {subdomains_file}")
    
    # Генерация отчета
    report_file = f"{analysis_dir}/vulnerability_report.md"
    generate_vulnerability_report(args.domain, analysis_dir, report_file)
    
    print(f"\n[=== Анализ завершен! Отчет: {report_file} ===]")

if __name__ == "__main__":
    main() 